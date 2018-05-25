from shutil import move
from os.path import basename, join

def run(project, folders, to):
	f = project and open(project, 'r+')
	text = f and f.read() or ''

	for i, folder in enumerate(folders):
		destination = join(to, basename(folder))
		text = text.replace(folder, destination)
		folders[i] = destination

		try:
			move(folder, to)
		except:
			pass

	if f:
		f.seek(0)
		f.write(text)
		f.truncate()
		f.close()