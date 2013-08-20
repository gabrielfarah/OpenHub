import pika
import logging
from pymongo import MongoClient

#===============================================================================
# Database connection
#===============================================================================
client = MongoClient('ds041168.mongolab.com', 41168)
db = client.tesisv2
db.authenticate('user', 'P4ssW0rd122#')
collection = db.listRepo

#===============================================================================
# Necesary loggin
#===============================================================================
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

#===============================================================================
# RabbitMQ connection 
#===============================================================================
# server_credentials = pika.PlainCredentials('admin', 'openhub')
# connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=server_credentials))
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#===============================================================================
# Queue declaration
#===============================================================================
channel = connection.channel()
channel.exchange_declare(exchange='repo_classifier',
                         type='direct')

#===============================================================================
# Read from database and send to queue
#===============================================================================
for repo in collection.find({}, {"id", "full_name", "name", "git_url", "languaje"}).limit(1):
    languaje = "Python"  # CHANGE
    print repo
    body = "%s::%i::%s" % (repo["git_url"], repo["id"], repo["name"])
    channel.basic_publish(exchange='repo_classifier',
                          routing_key=languaje,
                          body=body,
                          properties=pika.BasicProperties(
                              delivery_mode=2, # make message persistent
                          ))
    #print " [x] Sent %r:%r" % (languaje, repo["html_url"])

#===============================================================================
# Free resources
#===============================================================================
connection.close()
client.close()
