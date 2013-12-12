#!/usr/bin/env python
import pika
import logging
import importlib
import glob
import shutil
import os
import json
import datetime
import traceback
import requests
import zipfile
import StringIO
import signal
from openhub_exceptions import TimeoutException
from pymongo import MongoClient
from contextlib import contextmanager


DATA_PATH = '../data'
BASE_DIR = ''
REPO_DOWNLOAD_DIR = ''

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

    delete_repo(path)
    try:
        os.chdir(REPO_DOWNLOAD_DIR)

        print "Downloading code..."
        # print git.Git().clone(git_url)
        # subprocess.call(['git', 'clone', git_url], close_fds=True)
        r = requests.get(git_url)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        z.extractall()

        os.chdir(BASE_DIR)
        print "Done"
    except:
        raise
    finally:
        os.chdir(BASE_DIR)


def delete_repo(path):
    """Delete repo from path."""
    if os.path.exists(path):
        shutil.rmtree(path)


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException, "Timed out!"
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def callback(ch, method, properties, body):
    """Queue callback function.
    Will be executed when the queue pops this worker
    """
    data = body.split("::")
    git_url = data[0]
    repo_id = int(data[1])
    name = data[2]
    print " [x] Received %r" % (data,)

    path = '%s/%s' % (REPO_DOWNLOAD_DIR, name + '-master')
    try:
        repo_json = collection.find_one({"_id": repo_id})
        # down_repo(git_url, path)
        down_repo(repo_json['html_url'] + '/archive/master.zip', path)
        completed = True

        for d in dirs:
            print "Analyzing %s..." % d
            tests = [p.replace('/', '.') for p in glob.glob("%s/*" % d) if os.path.isdir(p)]  # Test list in the directory

            print "Current tests for %s: %s" % (d, tests)
            # repo_json[d] = []
            repo_json[d] = {}

            for test in tests:
                m = importlib.import_module(test + ".main")
                test_name = test.split('.')[1]
                try:
                    with time_limit(120):
                        res = m.run_test(repo_id, path, repo_json)
                        # data = {'name': test_name, 'value': res}
                        # repo_json[d].append(data)
                        repo_json[d][test_name] = res
                except Exception as e:
                    print 'Test error: %s %s' % (test, str(e))
                    # data = {'name': test_name, 'value': "Error:" + str(e)}
                    repo_json[d][test_name] = {'error': "Error:" + str(e), 'stack_trace': traceback.format_exc()}
                    completed = False
                    pass

        repo_json['analyzed_at'] = datetime.datetime.now()
        repo_json['state'] = 'completed' if completed else 'pending'
        print "Saving results to databse..."
        collection.update({"_id": repo_id}, repo_json)

        print "Deleting files..."
        delete_repo(path)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print " [x] Ready, waiting for next repo...\n"
        print "------------------------------------\n"

    except Exception as e:
        print "General error:", str(e)

        collection.update({"_id": repo_id}, {'$set': {'state': 'failed', 'analyzed_at': datetime.datetime.now(), 'error': 'General error:' + str(e), 'stack_trace': traceback.format_exc()}})
        print "Updated repo with failed status"

        print "Deleting files..."
        delete_repo(path)

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print "Will continue. Waiting for next repo...\n"
        print "------------------------------------\n"
        # TODO Terminar de manejar los errores


def load_config():
    global BASE_DIR, REPO_DOWNLOAD_DIR, RABBIT_HOST, RABBIT_USER, RABBIT_PWD, RABBIT_KEY, RABBIT_QUEUE, MONGO_PWD, MONGO_USER, MONGO_HOST, MONGO_PORT, MONGO_DB, MONGO_COLL, dirs

    paths_cfg = open(DATA_PATH + "/paths.json")
    data = json.load(paths_cfg)
    BASE_DIR = str(data['BASE_DIR'])
    REPO_DOWNLOAD_DIR = str(data['REPO_DOWNLOAD_DIR'])
    paths_cfg.close()

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
