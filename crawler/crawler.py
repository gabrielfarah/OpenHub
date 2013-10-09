#!/usr/bin/env python
import sys
import json
import github3
import logging
import pika
from github3.models import GitHubError
from pymongo import MongoClient

DATA_PATH = '../data'

LANGUAGES = []

RABBIT_HOST = ''
RABBIT_USER = ''
RABBIT_PWD = ''
RABBIT_KEY = ''
RABBIT_QUEUE = ''

MONGO_HOST = ''
MONGO_PORT = 0
MONGO_USER = ''
MONGO_PWD = ''
MONGO_DB = ''
MONGO_COLL = ''

GH_USERS = []
GH_CUR_USR = 0


def main(start_from=None):

    # Load config information
    load_config()

    # Connect to RabbitMQ Queue
    connection, channel = get_queue_channel(RABBIT_HOST)

    # Connect to databse
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    db.authenticate(MONGO_USER, MONGO_PWD)
    db_repos = db[MONGO_COLL]

    last_id = start_from  # Last id variable to be advanced
    reauth = True  # Reauth variable to check if we need to reauthenticate for GitHub
    gh = None  # Just for good measure

    while 1:
        # Authenticate on GitHub and get all repos
        if reauth:
            gh = github3.login(GH_USERS[GH_CUR_USR]['login'], GH_USERS[GH_CUR_USR]['pwd'])
        repos = gh.iter_all_repos(since=last_id)

        # Crawl repos
        reauth, last_id = start_crawl(repos, db_repos, gh, channel, last_id)

    #Close connection to databse
    client.close()

    #Close connection to queue
    channel.close()
    connection.close()


def start_crawl(repos, db_repos, gh, channel, last_id):
    try:
        for r in repos:
            last_id = r.id
            repo = gh.repository(r.full_name.split('/')[0], r.full_name.split('/')[1])
            if repo is None:
                continue
            json_repo = repo.to_json()
            db_repo = db_repos.find_one({"_id": repo.id})
            to_insert = {"_id": repo.id,
                         "analyzed_at": None,
                         "state": "pending",
                         "name": repo.name,
                         "full_name": repo.full_name,
                         "description": repo.description,
                         "fork": repo.fork,
                         "created_at": repo.created_at,
                         "updated_at": repo.updated_at,
                         "homepage": repo.homepage,
                         "size": repo.size,
                         "language": repo.language,
                         "has_issues": repo.has_issues,
                         "has_downloads": repo.has_downloads,
                         "has_wiki": repo.has_wiki,
                         "forks": repo.forks,
                         "open_issues": repo.open_issues,
                         "watchers": repo.watchers,
                         "network_count": json_repo[u'network_count'],
                         "url": json_repo[u'url'],
                         "git_url": repo.git_url,
                         "issues_url": json_repo[u'issues_url'],
                         "collaborators_url": json_repo[u'collaborators_url'],
                         "languages_url": json_repo[u'languages_url'],
                         "archive_url": json_repo[u'archive_url'],
                         "comments_url": json_repo[u'comments_url'],
                         "contributors_url": json_repo[u'contributors_url'],
                         "html_url": repo.html_url,
                         "subscribers_url": json_repo[u'subscribers_url'],
                         "stargazers_url": json_repo[u'stargazers_url'],
                         "owner": {"html_url": json_repo[u'owner'][u'html_url'],
                                   "type": json_repo[u'owner'][u'type'],
                                   "repos_url": json_repo[u'owner'][u'repos_url']}
                         }

            if db_repo:
                del to_insert['_id']
                to_insert['analyzed_at'] = db_repo[u'analyzed_at']

                if (db_repo[u'state'] == "completed" and repo.updated_at > db_repo[u'analyzed_at']) or (db_repo[u'state'] == "pending" or db_repo[u'state'] == "failed"):
                    db_repos.update({"_id": last_id}, {"$set": to_insert})
                    last_id = repo.id
                    print "Updated repo with id", last_id
                    push_to_queue(repo, channel)

                else:
                    to_insert['state'] = db_repo[u'state']
                    db_repos.update({"_id": last_id}, {"$set": to_insert})
                    last_id = repo.id
                    print "Updated repo with id %s. No analysis necessary. Will not push to queue" % last_id

            else:
                last_id = db_repos.insert(to_insert)
                print "Inserted repo with id", last_id
                push_to_queue(repo, channel)

    except GitHubError as e:
        if e.code != 403:
            return False, last_id
        else:
            global GH_CUR_USR
            print e
            print "Limit reached, switching users and restarting from last inserted id", last_id
            GH_CUR_USR = (GH_CUR_USR + 1) % len(GH_USERS)
            return True, last_id
    # except (KeyboardInterrupt, SystemExit):
    #     raise
    # except Exception as e:
    #     print "Unexpected error:", sys.exc_info()[0]
    #     print "Restarting crawl from last inserted id"
    #     return False, last_id


def get_queue_channel(host):

    # Necesary logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

    # RabbitMQ connection
    server_credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=server_credentials))
    # connection = pika.BlockingConnection(pika.ConnectionParameters(host))

    # Queue declaration
    channel = connection.channel()
    channel.exchange_declare(exchange='repo_classifier',
                             type='direct')

    return connection, channel


def push_to_queue(repo, channel):
    if repo.language in LANGUAGES:
        body = "%s::%i::%s" % (repo.git_url, repo.id, repo.name)
        channel.basic_publish(exchange='repo_classifier',
                              routing_key=repo.language,
                              body=body,
                              properties=pika.BasicProperties(
                                  delivery_mode=2,  # make message persistent
                              ))
        print " [*] Pushed to queue:", body
    else:
        print " [*] Can't analyze language. Did not push to queue."


def load_config():
    global RABBIT_HOST, RABBIT_USER, RABBIT_PWD, RABBIT_KEY, RABBIT_QUEUE, LANGUAGES, GH_USERS, MONGO_PWD, MONGO_USER, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL

    rabbit_cfg = open(DATA_PATH + "/rabbit.json")
    data = json.load(rabbit_cfg)
    RABBIT_HOST = str(data['RABBIT_HOST'])
    RABBIT_USER = str(data['RABBIT_USER'])
    RABBIT_PWD = str(data['RABBIT_PWD'])
    RABBIT_KEY = str(data['RABBIT_KEY'])
    RABBIT_QUEUE = str(data['RABBIT_QUEUE'])
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
    MONGO_DB = data['MONGO_DB']
    MONGO_COLL = data['MONGO_COLL']
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
