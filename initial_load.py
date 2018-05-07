import os
from pymongo import MongoClient
import json
import jsonschema


dbClient = MongoClient('localhost', 27017)#, username = dbUser, password = dbPass, authMechanism = dbAuthM)
dbDatabaseName = dbClient['Test']

my_collection = dbDatabaseName['jsonSchemas']
my_collection.drop()

for file in os.listdir("schema"):
    if file.endswith(".json"):
    	print file
    	with open(os.path.join("schema", file), 'r') as f:
		schemaP = json.loads(f.read())
    	res = my_collection.insert_one(schemaP).inserted_id
        print(os.path.join("schema", file))
        print res


my_collection = dbDatabaseName['roles']
my_collection.drop()

for file in os.listdir("roles"):
    if file.endswith(".json"):
    	with open(os.path.join("roles", file), 'r') as f:
		schemaP = json.loads(f.read())
    	res = my_collection.insert_one(schemaP).inserted_id
        print(os.path.join("schema", file))
        print res        	

my_collection = dbDatabaseName['appInstances']
my_collection.drop()

for file in os.listdir("appInstances"):
    if file.endswith(".json"):
    	with open(os.path.join("appInstances", file), 'r') as f:
		schemaP = json.loads(f.read())
    	res = my_collection.insert_one(schemaP).inserted_id
        print(os.path.join("appInstances", file))
        print res        	