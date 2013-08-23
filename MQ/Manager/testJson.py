#!/usr/bin/env python
import pika, logging, imp, glob, urllib, gzip, shutil, git, os, sys, json
from os import listdir
from os.path import isfile, join
from pymongo import MongoClient
from bson.objectid import ObjectId

import json as _json
class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return _json.JSONEncoder.default(self, o)

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
id=1
data = collection.find_one({"id": id})
print data["id"]
print data["name"]
for i in data:
    print i

if 'security' in data:print 'yes'
else: data["security"] = {}

collection.update({'id': id}, data )


