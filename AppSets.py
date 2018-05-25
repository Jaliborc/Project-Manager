import cPickle as pickle
import os

class start():
	def __init__(self, company, app):
		company = os.path.expanduser('~/Library/') + company
		app = company + '/' + app

		if not os.path.isdir(company):
			os.mkdir(company)

		if not os.path.isdir(app):
			os.mkdir(app)
			
		self.dir = app + '/'

	def new(self, name):
		path = self.dir + name
		data = None
		
		if os.path.isfile(path):
			file = open(path, 'r')
			data = pickle.loads(file.read())
			file.close()
		
		return data
	
	def save(self, name, data):
		file = open(self.dir + name, 'w')
		pickle.dump(data, file, True)
		file.close()