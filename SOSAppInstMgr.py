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
config_parser.read('SOSAppInstMgr.ini')


# Init WS parameters

WSport = int(config_parser.get('init', 'AppInstMgrWS_port'))
WShost = config_parser.get('init', 'AppInstMgrWS_url')

WSlogs = config_parser.get('logs', 'AppInstMgrWSLog')
WSloglevel = int(config_parser.get('logs', 'AppInstMgrWSLogLevel'))

getAppInstListSchema = config_parser.get('schema', 'getAppInstListSchema')
getAppInstListURL = config_parser.get('urls', 'getAppInstList')

dbHost = config_parser.get('db', 'host')
dbPort = int(config_parser.get('db', 'port'))
dbUser = config_parser.get('db', 'username')
dbPass = config_parser.get('db', 'password')
dbAuthM = config_parser.get('db', 'authMechanism')
dbName = config_parser.get('db', 'dbName')

appInstanceURL = config_parser.get('urls', 'appInstanceURL')
getAppInstListURL = config_parser.get('urls', 'getAppInstListURL')

# Init Logging

logger = logging.getLogger(__name__);
logger.setLevel(WSloglevel);

WSLogHandler = logging.FileHandler(WSlogs)
WSLogHandler.setLevel(WSloglevel)

WSLogFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
WSLogHandler.setFormatter(WSLogFormatter)

logger.addHandler(WSLogHandler)

logger.info('Logger started')

logger.debug('Debug started');

# Database (MongoDB) init

logger.info('Establishing MongoDB connection on ' + dbHost + ':' + str(dbPort) + '/' + dbName)

try:
    dbClient = MongoClient(dbHost, dbPort)#, username = dbUser, password = dbPass, authMechanism = dbAuthM)
except pymongo.errors.ConnectionFailure, e:
    logger.critical('MongoDB connection failed: ' + str(e));

dbDatabaseName = dbClient[dbName]

logger.info('MongoDB connection established')

# Schemas init


logger.info('Loading Web Service Request Schemas')

schemas = dbDatabaseName['jsonSchemas']

getAppInstListSchemaP = schemas.find_one({"schemaName": getAppInstListSchema})['schema']
logger.info('Schema: ' + getAppInstListSchema + ' loaded')

appInstanceSchemaP = schemas.find_one({"schemaName": appInstanceSchema})['schema']
logger.info('Schema: ' + appInstanceSchema + ' loaded')

logger.info(' Web Service Request Schemas loaded')


# User registration

@app.route(getAppInstListURL, methods=['POST'])
def index():

    logger.info("getAppInstList Request received")

    logger.debug("Request content: " + str(request.get_json()))

    dbJ = dbJSON(json.dumps(request.get_json()))

    # Document validation against json schema

    res = dbJ.validate(userRegistrationSchemaP)

    logger.debug("Request validation result: " + str(res))

    if res['errCode'] == 0:
        logger.info('Request successfully validated');

    if res['errCode'] == 0:

        # Pre-Storing Processing
        

        # Saving document to MongoDB

        res = dbJ.save(dbDatabaseName,dbUsers)

        logger.debug("DB save result: " + str(res))

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
