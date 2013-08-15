import sys
import json
import github3
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

DATA_PATH = '../data'

MONGO_HOST = ''
MONGO_PORT = 0
MONGO_USER = ''
MONGO_PWD = ''

GH_LOGIN = ''
GH_PWD = ''


def main(start_from=None):

    load_config()

    gh = github3.login(GH_LOGIN, GH_PWD)

    last_id = start_from

    while 1:
        repos = gh.iter_all_repos(since=last_id)
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.openhub
        db.authenticate(MONGO_USER, MONGO_PWD)
        db_repos = db.repos
        last_id = start_crawl(repos, db_repos)
        client.close()


def start_crawl(repos, db_repos):
    last_id = None
    for repo in repos:
        try:
            rep = repo.to_json()
            to_insert = {"_id": rep[u'id'],
                         "full_name": rep[u'full_name'],
                         "description": rep[u'description'],
                         "fork": rep[u'fork'],
                         "url": rep[u'url'],
                         "languages_url": rep[u'languages_url'],
                         "archive_url": rep[u'archive_url'],
                         "html_url": rep[u'html_url'],
                         "owner": {"html_url": rep[u'owner'][u'html_url'],
                                   "type": rep[u'owner'][u'type'],
                                   "repos_url": rep[u'owner'][u'repos_url']}
                         }
            last_id = db_repos.insert(to_insert)
            print "Inserted repo with id", last_id
        except DuplicateKeyError:
            print "Repo already exists, skipping"
            pass
        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "Restarting crawl from last inserted id"
            return last_id


def load_config():
    global GH_LOGIN, GH_PWD, MONGO_PWD, MONGO_USER, MONGO_HOST, MONGO_PORT

    gh_cfg = open(DATA_PATH + "/gh.json")
    data = json.load(gh_cfg)
    GH_LOGIN = data['GH_LOGIN']
    GH_PWD = data['GH_PWD']
    gh_cfg.close()

    mongo_cfg = open(DATA_PATH + "/mongo.json")
    data = json.load(mongo_cfg)
    MONGO_USER = data['MONGO_USER']
    MONGO_PWD = data['MONGO_PWD']
    MONGO_HOST = data['MONGO_HOST']
    MONGO_PORT = int(data['MONGO_PORT'])
    mongo_cfg.close()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        arg = None
        try:
            arg = int(sys.argv[1])
        except:
            print "Usage: %s <numerical id to start from>" % __file__
            sys.exit()
        main(arg)
    else:
        main()
