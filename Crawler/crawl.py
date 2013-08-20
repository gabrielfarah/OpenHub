import sys
import json
import github3
import pika
from github3.models import GitHubError
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

DATA_PATH = '../data'

LANGUAGES = []

RABBIT_HOST = ''

MONGO_HOST = ''
MONGO_PORT = 0
MONGO_USER = ''
MONGO_PWD = ''

GH_USERS = []
GH_CUR_USR = 0


def main(start_from=None):

    load_config()
    last_id = start_from
    connection, channel = get_queue_channel(RABBIT_HOST)

    while 1:
        gh = github3.login(GH_USERS[GH_CUR_USR]['login'], GH_USERS[GH_CUR_USR]['pwd'])
        repos = gh.iter_all_repos(since=last_id)
        client = MongoClient(MONGO_HOST, MONGO_PORT)
        db = client.openhub
        db.authenticate(MONGO_USER, MONGO_PWD)
        db_repos = db.repos
        last_id = start_crawl(repos, db_repos, gh, channel)
        client.close()

    channel.close()
    connection.close()


def start_crawl(repos, db_repos, gh, channel):
    last_id = None
    try:
        for repo in repos:
            try:
                rep = gh.repository(repo.full_name.split('/')[0], repo.full_name.split('/')[1]).to_json()
                to_insert = {"_id": rep[u'id'],
                             "analized": False,
                             "name": rep[u'name'],
                             "full_name": rep[u'full_name'],
                             "description": rep[u'description'],
                             "fork": rep[u'fork'],
                             "created_at": rep[u'created_at'],
                             "updated_at": rep[u'updated_at'],
                             "homepage": rep[u'homepage'],
                             "size": rep[u'size'],
                             "language": rep[u'language'],
                             "has_issues": rep[u'has_issues'],
                             "has_downloads": rep[u'has_downloads'],
                             "has_wiki": rep[u'has_wiki'],
                             "forks": rep[u'forks'],
                             "open_issues": rep[u'open_issues'],
                             "watchers": rep[u'watchers'],
                             "url": rep[u'url'],
                             "git_url": rep[u'git_url'],
                             "issues_url": rep[u'issues_url'],
                             "collaborators_url": rep[u'collaborators_url'],
                             "languages_url": rep[u'languages_url'],
                             "archive_url": rep[u'archive_url'],
                             "comments_url": rep[u'comments_url'],
                             "contributors_url": rep[u'contributors_url'],
                             "html_url": rep[u'html_url'],
                             "subscribers_url": rep[u'subscribers_url'],
                             "stargazers_url": rep[u'stargazers_url'],
                             "owner": {"html_url": rep[u'owner'][u'html_url'],
                                       "type": rep[u'owner'][u'type'],
                                       "repos_url": rep[u'owner'][u'repos_url']}
                             }
                last_id = db_repos.insert(to_insert)
                print "Inserted repo with id", last_id

                if to_insert['language'] in LANGUAGES:
                    body = "%s::%i::%s::%s" % (to_insert["git_url"], to_insert["_id"], to_insert["full_name"], to_insert["name"])
                    channel.basic_publish(exchange='repo_classifier',
                                          routing_key=to_insert['language'],
                                          body=body,
                                          properties=pika.BasicProperties(
                                              delivery_mode=2,  # make message persistent
                                          ))
                    print "\tSent to queue:", body
                else:
                    print "\tCan't analyze language. Did not send to queue"

            except DuplicateKeyError:
                print "Repo already exists, skipping"
                pass
    except GitHubError as e:
        global GH_CUR_USR
        print e
        print "Limit reached, switching users"
        GH_CUR_USR = (GH_CUR_USR + 1) % len(GH_USERS)
        return last_id
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print "Restarting crawl from last inserted id"
        return last_id


def get_queue_channel(host):
    # server_credentials = pika.PlainCredentials('admin', 'openhub')
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=server_credentials))
    connection = pika.BlockingConnection(pika.ConnectionParameters(host))

    channel = connection.channel()
    channel.exchange_declare(exchange='repo_classifier',
                             type='direct')

    return connection, channel


def load_config():
    global RABBIT_HOST, LANGUAGES, GH_USERS, MONGO_PWD, MONGO_USER, MONGO_HOST, MONGO_PORT

    rabbit_cfg = open(DATA_PATH + "/rabbit.json")
    data = json.load(rabbit_cfg)
    RABBIT_HOST = data['RABBIT_HOST']
    rabbit_cfg.close()

    langs = open(DATA_PATH + "/langs.json")
    LANGUAGES = set(json.load(langs))
    langs.close()

    gh_cfg = open(DATA_PATH + "/gh.json")
    GH_USERS = json.load(gh_cfg)
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

# TODO Revisar antes de actualizar la ultima fecha de update del repositorio
