#!/usr/bin/env python
import pika, logging, imp, glob, os ,urllib, gzip
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

#===============================================================================
# Database connection
#===============================================================================
client = MongoClient(hostDB, portDB)
db = client.tesis
db.authenticate(userDB, passDB)
collection = db.listRepo

#===============================================================================
# Callback Function
#===============================================================================
def callback(ch, method, properties, body):
    print (" [x] Received %r" % (body,))
    print(body)
    data = body.split("::")
    url = data[0];id = data[1];down = data[2]
    #download
    handle = urllib.urlopen(down)
    ruta = 'zFileTemp/%s'%down;
    ruta = 'zFileTemp/archivo.zip';
    with open(ruta, 'wb') as out:
        while True:
            data = handle.read(1024)
            if len(data) == 0: break
            out.write(data)

    # Extract SEED database
    handle = gzip.open(ruta)
    with open('zFileTemp', 'w') as out:
        for line in handle:
            out.write(line)

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
            info = m.runTest(url, down, data)
            print info

    ch.basic_ack(delivery_tag=method.delivery_tag)

def initRabbitMq(host="localhost", queue="task_queue", key="Python"):
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

#main
initRabbitMq(host, key, queue)