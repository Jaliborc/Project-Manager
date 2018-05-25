import requests
import json
	
def upload(key, project, title, file, name, type, changelog, toc):
	version = getVersion(toc)
	if not version:
		return "TOC version number " + toc + " not found."
	
	headers = {
		'User-Agent': 'CurseForge Uploader Script',
		'X-API-Key': key
	}

	files = {'file': (name, open(file, 'r'))}
	data = {
		'name': title,
		'game_versions': version,
		'file_type': type,
		'change_log': changelog,
		'change_markup_type': 'creole',
		'known_caveats': '',
		'caveats_markup_type': 'plain',
	}

	r = requests.post('http://wow.curseforge.com/addons/' + project + '/upload-file.json', data = data, headers = headers, files = files)
	if r.status_code != requests.codes.ok:
		return r.content
		
def getVersion(toc):
	r = requests.get('http://wow.curseforge.com/game-versions.json')
	if r.status_code != requests.codes.ok:
		return
	
	versions = json.loads(r.content)
	toc = str(toc)

	for id, data in versions.iteritems():
		if 'internal_id' in data:
			if data['internal_id'] == toc:
				return id