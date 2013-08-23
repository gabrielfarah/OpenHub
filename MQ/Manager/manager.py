#!/usr/bin/env python
import pika, logging, imp, glob, urllib, gzip, shutil, git, os, sys
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient

#config
hostDB = 'ds041168.mongolab.com'
portDB = 41168
userDB = 'user'
passDB = 'P4ssW0rd122#'
#ConfigRabbitMq
host = 'localhost'
key = 'Python'
queue = 'task_queue'
dirs = {'secure', 'usability'}
#otherCondig
baseDir = "zFileTemp"

#===============================================================================
# Database connection
#===============================================================================
# client = MongoClient(hostDB, portDB)
# db = client.tesisv2
# db.authenticate(userDB, passDB)
# collection = db.listRepo

client = MongoClient('ds041168.mongolab.com', 41168)
db = client.tesisv2
db.authenticate('user', 'P4ssW0rd122#')
collection = db.listRepo

#===============================================================================
# Download Repo
#===============================================================================
def downRepo(git_url,path):
    if os.path.exists(path):deleteRepo(path)
    firts=os.getcwd()
    os.chdir("%s/zFileTemp/"%firts)
    print "downloading Code"
    print git.Git().clone(git_url)
    os.chdir(firts)
    print "done"
    return 1

def deleteRepo(path):
    shutil.rmtree(path)


#===============================================================================
# Callback Function
#===============================================================================
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    data = body.split("::")
    git_url = data[0];id = data[1];name = data[2]
    repoJson={'id' : int(id)}
    print data
    path = '%s/%s'%(baseDir,name)
    # try:
    repoJson = collection.find_one({"id": int(id)})
    downRepo(git_url, path)
    for dir in dirs:
        print dir
        tests = glob.glob("%s/*.py" % dir) ## LISTA DE PRUBAS EN DIRS
        print (tests)
        for test in tests:
            try:
                m = imp.load_source(test, test)
                res = m.runTest(id, path, data)
                name = m.name
                repoJson[dir] = []
                data = "{'name':'%s','value':'%s'}}"%(name, res)
                repoJson[dir].append(data)
            except Exception as e:
                print 'Test error %s %s'%(dir,test)
                print str(e)
                print "error:", sys.exc_info()

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print "save results..."
    deleteRepo(path)
    print "delete files..."
    collection.update({"id": int(id)} , repoJson)
    print "ready waiting next..."
    # except:
    #     print "General error"
    #     collection.update({"id": int(id)} , repoJson)
    #     print "error:", sys.exc_info()
    #     #TODO Terminarlos errores
    # except:
    #     print sys.exc_info()
    #     print "ERRORR"

# def initRabbitMq(host="localhost", queue="task_queue", key="Python"):
#     print host
#     print queue
#     print key

#main

#===============================================================================
# Necesary loggin
#===============================================================================
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

#===============================================================================
# RabbitMQ connection
#===============================================================================
# server_credentials = pika.PlainCredentials('admin', 'openhub')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=server_credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters(host))

#===============================================================================
# Queue & Exchange declaration
#===============================================================================
channel = connection.channel()
channel.exchange_declare(exchange='repo_classifier', type='direct')
result = channel.queue_declare(queue=queue, durable=True)
queue_name = result.method.queue

#===============================================================================
# Queue Binding
#===============================================================================
channel.queue_bind(exchange='repo_classifier', queue=queue_name, routing_key=key)

print (' [*] Waiting for messages. To exit press CTRL+C')

#===============================================================================
# Channel Options & Ejecution
#===============================================================================
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()

