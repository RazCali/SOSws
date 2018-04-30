#!flask/bin/python

from flask import Flask, request, json, jsonify
import json
import jsonschema
from jsonschema import validate
from ConfigParser import SafeConfigParser
from pymongo import MongoClient
import hashlib

from dbJSON import dbJSON


# Init Config Parser

app = Flask(__name__)

config_parser = SafeConfigParser()
config_parser.read('SOS.ini')


# Init WS parameters

UMWSport = int(config_parser.get('init', 'userManagementWS_port'))
UMWShost = config_parser.get('init', 'userManagementWS_url')

userRegistrationSchema = config_parser.get('schema', 'userRegistrationSchema')
userRegistrationURL = config_parser.get('urls', 'userRegistrationURL')
userLoginURL = config_parser.get('urls', 'userLoginURL')
userLogoutURL = config_parser.get('urls', 'userLogoutURL')

dbHost = config_parser.get('db', 'host')
dbPort = int(config_parser.get('db', 'port'))
dbUser = config_parser.get('db', 'username')
dbPass = config_parser.get('db', 'password')
dbAuthM = config_parser.get('db', 'authMechanism')
dbName = config_parser.get('db', 'dbName')

dbUsers = config_parser.get('dbCollection', 'user')


# Schemas init

with open(userRegistrationSchema, 'r') as f:
   userRegistrationSchemaP = json.loads(f.read())


# Database (MongoDB) init

dbClient = MongoClient(dbHost, dbPort)#, username = dbUser, password = dbPass, authMechanism = dbAuthM)
dbDatabaseName = dbClient[dbName]


# User registration

@app.route(userRegistrationURL, methods=['POST'])
def index():

    dbJ = dbJSON(json.dumps(request.get_json()))

    # Document validation against json schema

    res = dbJ.validate(userRegistrationSchemaP)

    if res['errCode'] == 0:

        # Pre-Storing Processing
        
        dbJ.setValue('password',hashlib.sha256(dbJ.getValue('password')).hexdigest())

        # Saving document to MongoDB

        res = dbJ.save(dbDatabaseName,dbUsers)

    return json.dumps(res)



# Flask app main

if __name__ == '__main__':
    app.run(debug=True, host=UMWShost, port=UMWSport)
