'''
Created on Aug 13, 2013

@author: gabo
'''
import pika
import time
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
print ' [*] Waiting for messages. To exit press CTRL+C'

#===============================================================================
# Consuming callback
#===============================================================================
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    time.sleep( body.count('.') )
    print " [x] Done"
    ch.basic_ack(delivery_tag = method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback,
                      queue='task_queue')

channel.start_consuming()