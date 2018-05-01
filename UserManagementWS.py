#!flask/bin/python

from flask import Flask, request, json, jsonify
import json
import jsonschema
from jsonschema import validate
from ConfigParser import SafeConfigParser
from pymongo import MongoClient
import hashlib
import logging

from dbJSON import dbJSON


# Init Config Parser

app = Flask(__name__)

config_parser = SafeConfigParser()
config_parser.read('SOS.ini')


# Init WS parameters

WSport = int(config_parser.get('init', 'userManagementWS_port'))
WShost = config_parser.get('init', 'userManagementWS_url')

WSlogs = config_parser.get('logs', 'UserManagementWSLog')
WSloglevel = int(config_parser.get('logs', 'UserManagementWSLogLevel'))

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

# Init Logging

logger = logging.getLogger(__name__);
logger.setLevel(WSloglevel);

WSLogHandler = logging.FileHandler(WSlogs)
WSLogHandler.setLevel(logging.INFO)

WSLogFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
WSLogHandler.setFormatter(WSLogFormatter)

logger.addHandler(WSLogHandler)

logger.info('Logger started')

# Database (MongoDB) init

logger.info('Establishing MongoDB connection on ' + dbHost + ':' + str(dbPort) + '/' + dbName)

dbClient = MongoClient(dbHost, dbPort)#, username = dbUser, password = dbPass, authMechanism = dbAuthM)
dbDatabaseName = dbClient[dbName]

logger.info('MongoDB connection established')

# Schemas init


logger.info('Loading Web Service Request Schemas')

schemas = dbDatabaseName['jsonSchemas']

userRegistrationSchemaP = schemas.find_one({"schemaName": userRegistrationSchema})['schema']
logger.info('Schema: ' + userRegistrationSchema + ' loaded')

logger.info(' Web Service Request Schemas loaded')

## with open(userRegistrationSchema, 'r') as f:
##   userRegistrationSchemaP = json.loads(f.read())


# User registration

@app.route(userRegistrationURL, methods=['POST'])
def index():

    logger.info("userRegistration Request received")

    dbJ = dbJSON(json.dumps(request.get_json()))

    logger.debug(dbJ)

    # Document validation against json schema

    res = dbJ.validate(userRegistrationSchemaP)

    logger.debug(res)

    if res['errCode'] == 0:
        logger.info('Request successfully validated');

    if res['errCode'] == 0:

        # Pre-Storing Processing
        
        dbJ.setValue('password',hashlib.sha256(dbJ.getValue('password')).hexdigest())

        logger.info("userRegistration Request password hashed using SHA256")

        # Saving document to MongoDB

        res = dbJ.save(dbDatabaseName,dbUsers)

        logger.debug(res)

        if res['errCode'] == 0:

            logger.info("User Registration request successfully completed");

        else:

            logger.error("User Registration request failed. Reason: " + res['errDesc'])

    else:

        logger.critical('Request validation failed. Reason: ' + res['errDesc'])

    return json.dumps(res)



# Flask app main

if __name__ == '__main__':
    app.run(debug=True, host=WShost, port=WSport)
