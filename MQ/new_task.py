'''
Created on Aug 13, 2013

@author: Gabriel Farah
'''
import pika
import sys
import logging

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
channel.queue_declare(queue='task_queue', durable=True)

#===============================================================================
# New task send
#===============================================================================
message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(exchange='',
                      routing_key='task_queue',
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print " [x] Sent %r" % (message,)
connection.close()