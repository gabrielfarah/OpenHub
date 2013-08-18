#crawler v2
import requests, json, sys
from pymongo import MongoClient
#ds041168.mongolab.com:41168/tesisv2
persis = json.loads(open('data.json').read())
idL = persis['last_id']#ultimoIdGuardado
user = 0
client = MongoClient('ds041168.mongolab.com', 41168)
db = client.tesisv2
db.authenticate('user', 'P4ssW0rd122#')
coll = db.listRepo
username = persis["users"][user]["user"]
password = persis["users"][user]["pass"]
link = 'https://api.github.com/repositories?since=%i' % (idL)
while True:
    print link
    r = requests.get(link, auth=(username, password))
    link = r.headers['link'][1:r.headers['link'].find('>')]
    limit = r.headers['X-RateLimit-Remaining']
    time = r.headers['x-ratelimit-reset']
    if True: ## info
        print r.status_code
        print r.headers['link'][1:r.headers['link'].find('>')]
        print r.headers['X-RateLimit-Remaining']
        print r.headers['x-ratelimit-reset']
        print r.encoding
    try:
        data = r.json()
        print "dataRecive %i" % (len(data))
        for repo in data:
            print "id %i" % (repo["id"])
            if coll.find_one({"id": repo["id"]}) != None: ## check si ya esta guardado
                print "ya esta guardado %i" % repo["id"]  #hay algo actualizar
            else:
                #new info
                addInfo = requests.get(repo["url"], auth=(username, password))
                add = addInfo.json()
                limit = addInfo.headers['X-RateLimit-Remaining']
                time = addInfo.headers['x-ratelimit-reset']
                if (limit <= 1):                                #Cambia el user si se acabo el limit
                    user += 1
                    username = persis['users'][user]['user']
                    password = persis['users'][user]['pass']
                coll.insert({#sacaInfo y guarda
                             "id": repo["id"],
                             "url": repo["url"],
                             "description": repo["description"],
                             "downloads_url": repo["downloads_url"],
                             "languages_url": repo["languages_url"],
                             "git_url": add["git_url"],
                             "name":add["name"],
                             "full_name": add["full_name"],
                             "languages": add["language"],
                             "watchers_count": add["watchers_count"],
                             "has_issues": add["has_issues"],
                             "has_downloads": add["has_downloads"],
                             "has_wiki": add["has_wiki"],
                             "forks": add["forks"],
                             "watchers": add["watchers"],
                             "open_issues_count": add["open_issues_count"],
                             "archive_url": repo["archive_url"],
                             "owner": {
                                 "following_url": repo["owner"]["following_url"],
                                 "html_url": repo["owner"]["html_url"],
                                 "starred_url": repo["owner"]["starred_url"],
                                 "type": repo["owner"]["type"],
                                 "followers_url": repo["owner"]["followers_url"],
                                 "repos_url": repo["owner"]["followers_url"]
                             },
                             "html_url": repo["html_url"],
                             "archive_url": repo["archive_url"],
                             "events_url": repo["events_url"],
                })
                idL = repo["id"]
                persis['last_id'] = idL
                persis['users'][user]['limit'] = limit
                persis['users'][user]['timeReset'] = time
                with open('data.json', 'w') as outfile:
                    json.dump(persis, outfile)
            print "limite %s" % (limit)
    except:
        persis['last_id'] = idL
        with open('data.json', 'w') as outfile:
            json.dump(persis, outfile)
        print "error:", sys.exc_info()[0]
        break
