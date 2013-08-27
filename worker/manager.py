#!/usr/bin/env python
import pika
import logging
import imp
import glob
import shutil
import git
import os
import sys
import json
from pymongo import MongoClient

DATA_PATH = '../data'

BASE_DIR = 'zFileTemp'

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

dirs = []
collection = ''


def main():
    global collection

    load_config()

    # Database connection
    client = MongoClient(MONGO_HOST, MONGO_PORT)
    db = client[MONGO_DB]
    db.authenticate(MONGO_USER, MONGO_PWD)
    collection = db[MONGO_COLL]

    # Necesary logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

    # RabbitMQ connection
    server_credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PWD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST, credentials=server_credentials))
    # connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST))

    # Queue and Exchange declaration
    channel = connection.channel()
    channel.exchange_declare(exchange='repo_classifier', type='direct')
    result = channel.queue_declare(queue=RABBIT_QUEUE, durable=True)
    queue_name = result.method.queue

    # Queue Binding
    channel.queue_bind(exchange='repo_classifier', queue=queue_name, routing_key=RABBIT_KEY)

    print ' [*] Waiting for messages. To exit press CTRL+C'

    # Channel Options and Execution
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback, queue=queue_name)
    channel.start_consuming()


def down_repo(git_url, path):
    """Download repo from specified url into path."""

    if os.path.exists(path):
        delete_repo(path)

    firts = os.getcwd()
    os.chdir("%s/%s/" % (firts, BASE_DIR))

    print "Downloading code..."
    print git.Git().clone(git_url)

    os.chdir(firts)

    print "Done"


def delete_repo(path):
    """Delete repo from path."""
    shutil.rmtree(path)


def callback(ch, method, properties, body):
    """Queue callback function.
    Will be executed when the queue pops this worker
    """
    print " [x] Received %r" % (body,)
    data = body.split("::")
    git_url = data[0]
    repo_id = data[1]
    name = data[2]
    repoJson = {'_id': int(repo_id)}
    print data
    path = '%s/%s' % (BASE_DIR, name)
    try:
        repoJson = collection.find_one({"_id": int(repo_id)})
        down_repo(git_url, path)
        for d in dirs:
            print d
            tests = glob.glob("%s/*.py" % d)  # Test list in the directories
            print (tests)
            for test in tests:
                try:
                    m = imp.load_source(test, test)
                    res = m.runTest(repo_id, path, data)
                    name = m.name
                    repoJson[d] = []
                    data = "{'name':'%s','value':'%s'}}" % (name, res)
                    repoJson[d].append(data)
                except Exception as e:
                    print 'Test error %s %s' % (d, test)
                    print str(e)
                    print "Error:", sys.exc_info()

        print "Save results..."
        delete_repo(path)
        print "Delete files..."
        collection.update({"_id": int(repo_id)}, repoJson)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print "Ready, waiting for next repo..."
    except Exception as e:
        print "General error:", e
        collection.update({"_id": int(repo_id)}, repoJson)
        print "Will continue with next repo..."
        ch.basic_ack(delivery_tag=method.delivery_tag)
        pass
        # TODO Terminar de manejar los errores


def load_config():
    global RABBIT_HOST, RABBIT_USER, RABBIT_PWD, RABBIT_KEY, RABBIT_QUEUE, MONGO_PWD, MONGO_USER, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL, dirs

    rabbit_cfg = open(DATA_PATH + "/rabbit.json")
    data = json.load(rabbit_cfg)
    RABBIT_HOST = str(data['RABBIT_HOST'])
    RABBIT_USER = str(data['RABBIT_USER'])
    RABBIT_PWD = str(data['RABBIT_PWD'])
    RABBIT_KEY = str(data['RABBIT_KEY'])
    RABBIT_QUEUE = str(data['RABBIT_QUEUE'])
    rabbit_cfg.close()

    d = open(DATA_PATH + "/analyzers.json")
    dirs = set(json.load(d))
    d.close()

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
    main()
