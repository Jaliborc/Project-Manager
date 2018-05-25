import zipfile as zipper
from codecs import open
from shutil import copy
import wx.richtext
import os.path
import wx, os, re

from Uploader import upload
import ProjectMover
import AppSets
import Panels

# Tools
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Settings
Sets = AppSets.start('Jaliborc', 'ProjectManager')
BlizzVersion = Sets.new('BlizzVersion') or 0
Projects = Sets.new('Projects') or []
UserKey = Sets.new('UserKey') or ''

# Constants
CODE_DIR = os.path.dirname(os.path.realpath(__file__)).replace(' ', '\ ') + '/'
ZIP_PATH = Sets.dir + 'TempZip.zip'
TEMP_FILE = Sets.dir + 'TempFile.txt'

# Main Window
class MainWindow(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title = 'Project Manager', size = (1000, 600))
		
		self.ProjectList = wx.ListView( self, style = wx.LC_SINGLE_SEL|wx.LC_EDIT_LABELS|wx.LC_REPORT|wx.LC_NO_HEADER )
		self.Changelog = wx.richtext.RichTextCtrl(self, style = wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
		self.Stripes = wx.Window( self, style = wx.SUNKEN_BORDER )

		self.ProjectList.Bind( wx.EVT_LIST_END_LABEL_EDIT, self.OnProjectRename )
		self.ProjectList.Bind( wx.EVT_LIST_ITEM_SELECTED, self.OnProjectSelected )
		
		self.SetToolBar(Panels.Toolbar(self))
		self.SetMenuBar(Panels.Menu(self))
		
		self.ProjectList.InsertColumn(0, '', width = 200)
		self.UpdateProjects()
		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.OnSize(None)
		
	def OnSize(self, event):
		width, height = self.GetClientSize()
		
		self.ProjectList.SetDimensions(0, 0, 200, height)
		self.Changelog.SetDimensions(220, 0, width - 220, height)
		self.Stripes.SetDimensions(200, -5, 20, height + 10)


	# User Events
	def OnUserKey(self, event):
		panel = Panels.UserKey(self, UserKey)
		panel.ShowModal()
		panel.Destroy()

	def OnUserKeySet(self, key):
		global UserKey
		Sets.save('UserKey', key)
		UserKey = key
		
	# Projects Events
	def OnProjectRename( self, selection ):
		self.projects[selection.GetIndex()]['name'] = selection.GetLabel()
		self.UpdateProjects()
		self.SaveProjects()
	
	def OnProjectSelected( self, selection ):
		self.SetProject(selection.GetIndex())

	def OnNewProject(self, event):
		dialog = wx.TextEntryDialog(self, 'Please enter the name for your new project:', 'Project Name')
		if dialog.ShowModal() == wx.ID_OK:
			project = {'name': dialog.GetValue() or '', 'folders': []}
			Projects.append(project)
			
			self.EditProject(project)
			self.UpdateProjects()
		
		dialog.Destroy()

	def OnEditProject(self, event):
		self.EditProject(self.project)

	def OnMoveProject(self, event):
		destination = wx.DirDialog(self, 'Select the destination directory for the project')
		if destination.ShowModal() == wx.ID_OK:
			ProjectMover.run(self.project.get('solution'), self.project['folders'], destination.GetPath())
			self.SaveProjects()

	def OnDeleteProject(self, event):
		dialog = wx.MessageDialog(self, 'Are you sure you want to delete this project? This cannot be undone.', 'Delete Project', wx.YES_NO|wx.ICON_EXCLAMATION)
		if dialog.ShowModal() == wx.ID_YES:
			Projects.remove(self.project)
			self.UpdateProjects()
			self.SaveProjects()
			self.SetProject(0)
			
		dialog.Destroy()
		

	# Projects API
	def SetProject(self, i):
		self.ignore = {}
		self.log = None
		
		if i < self.size:
			project = self.projects[i]
			
			for folder in project['folders']:
				ignore = folder + '/Ignore.manifest'
				log = folder + '/Changelog.txt'
				
				if os.path.isfile(log):
					self.log = log
					
				if os.path.isfile(ignore):
					lines = self.ReadFile(ignore).split('\n')
					
					for line in lines:
						if line != '':
							self.ignore[folder + '/' + line] = True
			
			self.project = project
			self.ProjectList.Select(i)
			self.UpdateChangelog()
		else:
			self.Changelog.SetValue('')
			
	def EditProject(self, project):
		editor = Panels.ProjectEditor(self, project)
		editor.ShowModal()
		editor.Destroy()
			
	def UpdateProjects(self):
		self.ProjectList.DeleteAllItems()
		self.size = len(Projects)
		self.projects = []
		
		for project in Projects:
			self.projects.append(project)
			
		self.projects.sort(key = self.GetProjectName)
		for i, project in enumerate(self.projects):
			self.ProjectList.InsertStringItem(i, project['name'])
			
	def GetProjectName(self, project):
		return project['name']
		
	
	# Upload
	def OnUpload(self, event):	
		if hasattr(self, 'project'):
			name = self.project.get('name')
			slug = self.project.get('slug')
			log = self.ReadChangelog()
			
			version = None
			release = 'r'
			
			if log:
				match = re.search('(\d+\.?\d*\.?\d*)', log)
				if match:
					version = match.group(1)
					if re.search(version + '\s+\(beta\)', log):
						release = 'b'

			if self.UploadRequirement('Slug', slug) and self.UploadRequirement('Version', version):
				self.zipFile = zipper.ZipFile(ZIP_PATH, 'w')
				self.IterateFiles(self.project, self.CompressFile, version)
				self.zipFile.close()
				
				zipName = name + (version and (' ' + version) or '') + '.zip'
				error = self.UploadFile(slug, version, release, log, zipName)
				os.remove(TEMP_FILE)
				os.remove(ZIP_PATH)
				
				if error:
					Panels.Error(self, 'Error Uploading', error)
				else:
					Panels.Alert(self, 'Upload Successful', 'Version ' + version + ' of ' + name + ' has been successfully uploaded.')
				    
	
	def CompressFile(self, origin, target, version):
		isToc = target[-4:] == '.toc'
		if isToc and version:
			text = self.ReadFile(target)
			text = re.sub('## Version:\s*[\d\.]+', '## Version: ' + version, text)
			self.WriteFile(target, text)

		copy(target, TEMP_FILE)
		if isToc:
			text = self.ReadFile(TEMP_FILE)
			title = re.search('## Title:\s*\|cff.{6}(.+)\|r', text)
			if title:
				text = re.sub('## Title:.+\|r', '## Title: ' + title.group(1), text)
			
			self.WriteFile(TEMP_FILE, text)

		self.zipFile.write(TEMP_FILE, target[len(origin):], zipper.ZIP_DEFLATED)
			
	def UploadFile( self, slug, version, release, log, zip ):
		return upload(
			key = UserKey,
			file = ZIP_PATH,
			project = slug,
			title = version,
			changelog = log,
			toc = BlizzVersion,
			type = release,
			name = zip,
		)
			
	def UploadRequirement( self, name, value ):
		if not value or value == '':
			Panels.Error(self, 'Cannot Upload', '"' + name + '" has not been defined.')
		else:
			return True
			
		
	# Game Version
	def OnGameVersion( self, event ):
		panel = Panels.GameVersion(self, BlizzVersion)
		panel.ShowModal()
		panel.Destroy()
		
	def OnBlizzVersion( self, input ):
		global BlizzVersion
		value = input.GetValue()
		
		if is_number(value):
			Sets.save('BlizzVersion', value)
			BlizzVersion = value
			
			for project in Projects:
				self.IterateFiles(project, self.UpdateBlizzVersion, BlizzVersion)
		else:
			input.SetValue('')
	
	def UpdateBlizzVersion(self, origin, path, version):
		if path[:-4] == '.toc':
			text = self.ReadFile(path)
			self.WriteFile(path, re.sub('## Interface:\s*\d+', '## Interface: ' + version, text))
			
	
	# Changelog Events
	def OnNewVersion( self, event ):
		self.Changelog.SetValue( '====== X\n* \n\n' + self.Changelog.GetValue())
			
	def OnSaveChangelog( self, event ):
		self.SaveChangelog()
			
			
	# Changelog API
	def UpdateChangelog(self):
		text = self.ReadChangelog()
		if text:
			self.Changelog.SetValue(text)
		else:
			self.Changelog.SetValue('No changelog found.')
			
	def SaveChangelog(self):
		log = open(self.log, 'w', 'utf-8')
		log.write(self.Changelog.GetValue().replace('', '\n'))
		log.close()
			
	def ReadChangelog(self):
		return open(self.log, 'r', 'utf-8').read()
			

	# File API	
	def IterateFiles(self, project, method, arg):
		for folder in project['folders']:
			origin = folder[0:-len(os.path.basename(folder))]
				
			for dirPath, _, files in os.walk(folder):
				if not self.IsDirIgnored(dirPath):
					if not re.search('/\.', dirPath):
						for entry in files:
							if entry[0] != '.' and entry != 'Icon\r' and entry[-4:]!='.txt' and entry[-3:]!='.md' and entry[-4:] != '.psd' and entry[-9:] != '.manifest':
								path = dirPath + '/' + entry
							
								if not path in self.ignore:
									method(origin, path, arg)
	
	def IsDirIgnored(self, dirPath):
		for line in self.ignore:
			if dirPath.startswith(line):
				return True
	
	def ReadFile(self, path):
		f = open(path, 'r', 'utf-8')
		text = f.read()
		f.close()
		return text
		
	def WriteFile(self, path, text):
		f = open(path, 'w', 'utf-8')
		f.write(text)
		f.close()
	
	def SaveProjects(self):
		Sets.save('Projects', Projects)
