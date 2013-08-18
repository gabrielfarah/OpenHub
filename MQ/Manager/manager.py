#!/usr/bin/env python
import pika, logging, imp, glob, urllib, gzip, shutil, git, os, sys
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient

#config
hostDB = 'ds041188.mongolab.com'
portDB = 41188
userDB = 'user'
passDB = 'P4ssW0rd122#'
#ConfigRabbitMq
host = 'localhost'
key = 'Python'
queue = 'task_queue'
dirs = {'secure', 'usability'}
#otherCondig
baseDir="zFileTemp"

#===============================================================================
# Database connection
#===============================================================================
client = MongoClient(hostDB, portDB)
db = client.tesis
db.authenticate(userDB, passDB)
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
# body = "%s::%i::%s::%s" % (repo["git_url"], repo["id"], repo["full_name"], repo["name"])
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    # try:
    data = body.split("::")
    git_url = data[0]
    id = data[1]
    fullname = data[2]
    name= data[3]
    print data
    path = '%s/%s'%(baseDir,name)
    if downRepo(git_url, path):
        for dir in dirs:
            tests = glob.glob("%s/*.py" % dir) ## LISTA DE PRUBAS EN DIRS
            print (tests)
            for test in tests:
                m = imp.load_source(test, test)
                if m.type == 1:
                    print "tipo1"
                elif m.type == 2:
                    print "tipo2"
                else:
                    print "error"
                info = m.runTest(id, path, data)
                print "Respuesta"
                print info
                #TODO hacer algo con el resultado
        ch.basic_ack(delivery_tag=method.delivery_tag)
        deleteRepo(path)
        print "ready Esperando siguiente ..."
    else:
        print "manejar error"
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

