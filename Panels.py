import Cocoa
import wx

# Errors
def Alert ( self, title, text ):
	MessageDialog(self, text, title, wx.ICON_INFORMATION)

def Error ( self, title, text ):
	MessageDialog(self, text, title, wx.ICON_EXCLAMATION)
	
def MessageDialog(*args):
	dialog = wx.MessageDialog(*args)
	dialog.ShowModal()
	dialog.Destroy()
	
		
# Toolbar
class Toolbar ( wx.ToolBar ):
	def __init__( self, parent ):
		wx.ToolBar.__init__ ( self, parent, style = wx.TB_TEXT )
		
		self.AddLabelTool( 1, "New Version",  wx.Bitmap("InsertStack.png")) 
		self.AddLabelTool( 2, "Upload", wx.Bitmap("Upload.png")) 
		self.Bind( wx.EVT_TOOL, parent.OnNewVersion, id = 1 )
		self.Bind( wx.EVT_TOOL, parent.OnUpload, id = 2 )
		self.Realize()
			
		
# Menu
class Menu ( wx.MenuBar ):
	
	def __init__( self, parent ):
		wx.MenuBar.__init__ ( self, style = 0 )
		
		self.User = wx.Menu()
		self.UserKey = wx.MenuItem( self.User, wx.ID_ANY, "Set API Key" "\t" + "CTRL-K", wx.EmptyString, wx.ITEM_NORMAL )
		self.User.AppendItem( self.UserKey )
		self.Append( self.User, "User" ) 

		self.Projects = wx.Menu()
		self.NewProject = wx.MenuItem( self.Projects, wx.ID_ANY, "New Project"+ "\t" + "CTRL-N", wx.EmptyString, wx.ITEM_NORMAL )
		self.Projects.AppendItem( self.NewProject )
		
		self.EditProject = wx.MenuItem( self.Projects, wx.ID_ANY, "Edit Project"+ "\t" + "CTRL+E", wx.EmptyString, wx.ITEM_NORMAL )
		self.Projects.AppendItem( self.EditProject )

		self.MoveProject = wx.MenuItem( self.Projects, wx.ID_ANY, "Move Project"+ "\t" + "CTRL+M", wx.EmptyString, wx.ITEM_NORMAL )
		self.Projects.AppendItem( self.MoveProject )
		
		self.DeleteProject = wx.MenuItem( self.Projects, wx.ID_ANY, "Delete Project"+ "\t" + "CTRL-D", wx.EmptyString, wx.ITEM_NORMAL )
		self.Projects.AppendItem( self.DeleteProject )
		self.Append( self.Projects, "Projects" ) 
		
		self.Versions = wx.Menu()
		self.SaveChangelog = wx.MenuItem( self.Versions, wx.ID_ANY, "Save Changelog"+ "\t" + "CTRL-S", wx.EmptyString, wx.ITEM_NORMAL )
		self.Versions.AppendItem( self.SaveChangelog )
		
		self.GameVersion = wx.MenuItem( self.Versions, wx.ID_ANY, "Set Game Version"+ "\t" + "CTRL-G", wx.EmptyString, wx.ITEM_NORMAL )
		self.Versions.AppendItem( self.GameVersion )
		self.Append( self.Versions, "Versions" ) 
		
		parent.Bind( wx.EVT_MENU, parent.OnUserKey, id = self.UserKey.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnNewProject, id = self.NewProject.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnEditProject, id = self.EditProject.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnMoveProject, id = self.MoveProject.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnDeleteProject, id = self.DeleteProject.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnSaveChangelog, id = self.SaveChangelog.GetId() )
		parent.Bind( wx.EVT_MENU, parent.OnGameVersion, id = self.GameVersion.GetId() )
		
		
# Project Editor
class ProjectEditor ( wx.Dialog ):

	def __init__( self, parent, project ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = 'Edit Project', size = wx.Size( 650, 535 ), style = wx.DEFAULT_DIALOG_STYLE )
		
		Layout = wx.BoxSizer( wx.VERTICAL )
		
		self.SlugLabel = wx.StaticText( self, wx.ID_ANY, 'Slug', wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SlugLabel.Wrap( -1 )
		Layout.Add( self.SlugLabel, 0, wx.TOP|wx.LEFT, 10 )
		
		self.SlugInput = wx.TextCtrl( self, wx.ID_ANY, project.get('slug', ''), wx.DefaultPosition, wx.DefaultSize, 0 )
		Layout.Add( self.SlugInput, 0, wx.ALL|wx.EXPAND, 10 )

		self.SolutionLabel = wx.StaticText( self, wx.ID_ANY, 'Solution', wx.DefaultPosition, wx.DefaultSize, 0 )
		self.SolutionLabel.Wrap( -1 )
		Layout.Add( self.SolutionLabel, 0, wx.TOP|wx.LEFT, 10 )

		self.SolutionPicker = wx.FilePickerCtrl(self, wx.ID_ANY, project.get('solution', ''), 'Select solution file')
		Layout.Add( self.SolutionPicker, 0, wx.ALL|wx.EXPAND, 5 )
		
		wx.Window( self, pos = (10, 147), size = (630, 326), style = wx.SUNKEN_BORDER )
		self.AddonList = wx.ListView( self , style = wx.LC_SINGLE_SEL|wx.LC_REPORT)
		Layout.Add( self.AddonList, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 11 )		

		self.AddAddon = Cocoa.LightPlus( self )
		self.RemoveAddon = Cocoa.LightMinus( self, pos = (32, 482) )
		Layout.Add( self.AddAddon, 0, wx.ALL, 10 )
		
		self.SetSizer( Layout )
		self.Layout()
		self.Center()
		
		self.project = project
		self.AddonList.InsertColumn(0, 'Folders', width = self.AddonList.GetSize()[0])
		self.UpdateList()
		
		self.SlugInput.Bind(wx.EVT_TEXT, self.OnSlugSet)
		self.SolutionPicker.Bind(wx.EVT_FILEPICKER_CHANGED, self.OnSolutionSet)
		self.RemoveAddon.Bind(wx.EVT_BUTTON, self.OnRemove )
		self.AddAddon.Bind(wx.EVT_BUTTON, self.OnAdd)
		
	def UpdateList( self ):
		self.AddonList.DeleteAllItems()
		i = 0
		
		for folder in self.project['folders']:
			self.AddonList.InsertStringItem(i, folder)
			i = i + 1
			
	def OnSlugSet( self, event ):
		self.project['slug'] = self.SlugInput.GetValue()
		self.GetParent().SaveProjects()

	def OnSolutionSet( self, event ):
		self.project['solution'] = self.SolutionPicker.GetPath()
		self.GetParent().SaveProjects()
		
	def OnAdd( self, event ):
		dialog = wx.DirDialog(self, 'Select a directory to be added to the project')
		if dialog.ShowModal() == wx.ID_OK:
			target = dialog.GetPath()
			folders = self.project['folders']
			
			for folder in folders:
				if target == folder:
					return dialog.Destroy()
					
			folders.append(target)
			self.GetParent().SaveProjects()
			self.UpdateList()
			
		dialog.Destroy()
		
	def OnRemove( self, event ):
		self.project['folders'].pop(self.AddonList.GetFirstSelected())
		self.GetParent().SaveProjects()
		self.UpdateList()
		
		
# Dialogs
class SettingDialog(wx.Dialog):
	def __init__(self, parent, value):
		wx.Dialog.__init__ (self, parent, id = wx.ID_ANY, title = self.Label, pos = wx.DefaultPosition, size = wx.Size(400, 55), style = wx.DEFAULT_DIALOG_STYLE)
		
		self.SetSizeHintsSz(wx.DefaultSize, wx.DefaultSize)
		Layout = wx.BoxSizer(wx.VERTICAL)
		
		self.Input = wx.TextCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0)
		self.Input.SetValue(value or '')
		Layout.Add(self.Input, 0, wx.ALL|wx.EXPAND, 5)
		
		self.SetSizer(Layout)
		self.Layout()
		self.Centre(wx.BOTH)
		self.Input.Bind(wx.EVT_TEXT, self.OnValueChanged)

class GameVersion(SettingDialog):
	Label = 'World of Warcraft TOC Version'

	def OnValueChanged(self, event):
		self.GetParent().OnBlizzVersion(self.Input)

class UserKey(SettingDialog):
	Label = 'CurseForge/WoWAce User Key'

	def OnValueChanged(self, event):
		self.GetParent().OnUserKeySet(self.Input.GetValue())
