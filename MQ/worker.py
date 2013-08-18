'''
Created on Aug 13, 2013

@author: Gabriel Farah
'''
import pika
import logging

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
# Queue & Exchange declaration
#===============================================================================
channel = connection.channel()
channel.exchange_declare(exchange='repo_classifier', type='direct')
result = channel.queue_declare(queue='task_queue', durable=True)
queue_name = result.method.queue

#===============================================================================
# Queue Binding
#===============================================================================
channel.queue_bind(exchange='repo_classifier', queue=queue_name, routing_key='Python') #Change {Python} by the specific languaje

print ' [*] Waiting for messages. To exit press CTRL+C'

#===============================================================================
# Callback Function
#===============================================================================
def callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    ch.basic_ack(delivery_tag = method.delivery_tag)

#===============================================================================
# Channel Options & Ejecution
#===============================================================================
channel.basic_qos(prefetch_count=1)
channel.basic_consume(callback, queue=queue_name)
channel.start_consuming()