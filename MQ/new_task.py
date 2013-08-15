'''
Created on Aug 13, 2013

@author: Gabriel Farah
'''
import pika
import logging
from pymongo import MongoClient

#===============================================================================
# Database connection
#===============================================================================
client = MongoClient('ds041188.mongolab.com', 41188)
db = client.tesis
db.authenticate('user', 'P4ssW0rd122#')
collection = db.listRepo

#===============================================================================
# Necesary loggin
#===============================================================================
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.CRITICAL)

#===============================================================================
# RabbitMQ connection 
#===============================================================================
server_credentials = pika.PlainCredentials('admin', 'openhub')
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost', credentials=server_credentials))

#===============================================================================
# Queue declaration
#===============================================================================
channel = connection.channel()
channel.exchange_declare(exchange='repo_classifier',
                         type='direct')

#===============================================================================
# Read from database and send to queue
#===============================================================================
for repo in collection.find({}, {"html_url", "languaje"}).limit(15):
    languaje = "Python"  # CHANGE
    channel.basic_publish(exchange='repo_classifier',
                          routing_key=languaje,
                          body=repo["html_url"],
                          properties=pika.BasicProperties(
                             delivery_mode=2,  # make message persistent
                          ))
    #print " [x] Sent %r:%r" % (languaje, repo["html_url"])

#===============================================================================
# Free resources
#===============================================================================
connection.close()
client.close()