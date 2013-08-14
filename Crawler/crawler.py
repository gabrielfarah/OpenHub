#crawler v2
import requests
from pymongo import MongoClient
#ds041168.mongolab.com:41168/tesisv2
idL=-1;#ultimoIdGuardado
client = MongoClient('ds041168.mongolab.com', 41168)
db = client.tesisv2
db.authenticate('user', 'P4ssW0rd122#')
collection = db.listRepo
username='liuspatt';
password='123qweasd';
link='https://api.github.com/repositories';
while True:

	r= requests.get(link, auth=(username, password))			
	link= r.headers['link'][1:r.headers['link'].find('>')]	
	limit= r.headers['X-RateLimit-Remaining']
	if False:
		print r.status_code	
		print r.headers['link'][1:r.headers['link'].find('>')]
		print r.headers['X-RateLimit-Remaining']
		print r.encoding
		print repo	
	try:
		if(limit>1):		
			text= r.text
			data= r.json()				
			for repo in data:					 
				if coll.find_one({"id": repo["id"]}) != None: ## check si ya esta guardado
					break #hay algo actualizar				
				else:				
					coll.insert({
						"id":repo["id"],
						"description":repo["description"],
						"downloads_url":repo["downloads_url"],
						"languages_url":repo["languages_url"],
						"owner":{ 	
									"following_url":repo["owner"]["following_url"],
									"html_url":repo["owner"]["html_url"],
						 			"starred_url":repo["owner"]["starred_url"],
									"type":repo["owner"]["type"],
									"followers_url":repo["owner"]["followers_url"],
									"repos_url":repo["owner"]["followers_url"]
								},				
						"html_url":repo["html_url"],
					})
					idL=repo["id"]				
				break	
			break
		else:
			 #changeUser
			break
		break
	except :
		break # terminar errores
