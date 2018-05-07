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
from sosSession import sosSession


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
userLoginSchema = config_parser.get('schema', 'userLoginSchema')
userLoginURL = config_parser.get('urls', 'userLoginURL')
userLogoutURL = config_parser.get('urls', 'userLogoutURL')

dbHost = config_parser.get('db', 'host')
dbPort = int(config_parser.get('db', 'port'))
dbUser = config_parser.get('db', 'username')
dbPass = config_parser.get('db', 'password')
dbAuthM = config_parser.get('db', 'authMechanism')
dbName = config_parser.get('db', 'dbName')

dbUsers = config_parser.get('dbCollection', 'user')
dbSessions = config_parser.get('dbCollection', 'session')
dbRoles = config_parser.get('dbCollection', 'roles')

tokenSize = config_parser.get('session', 'tokenSize')

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

userRegistrationSchemaP = schemas.find_one({"schemaName": userRegistrationSchema})['schema']
logger.info('Schema: ' + userRegistrationSchema + ' loaded')

userLoginSchemaP = schemas.find_one({"schemaName": userLoginSchema})['schema']
logger.info('Schema: ' + userLoginSchema + ' loaded')

logger.info(' Web Service Request Schemas loaded')

## with open(userRegistrationSchema, 'r') as f:
##   userRegistrationSchemaP = json.loads(f.read())


# User registration

@app.route(userRegistrationURL, methods=['POST'])
def login():

    logger.info("userRegistration Request received")

    logger.debug("Request content: " + str(request.get_json()))

    dbJ = dbJSON(json.dumps(request.get_json()))

    # Document validation against json schema

    res = dbJ.validate(userRegistrationSchemaP)

    logger.debug("Request validation result: " + str(res))

    if res['errCode'] == 0:
        logger.info('Request successfully validated');

    if res['errCode'] == 0:

        # Pre-Storing Processing
        
        dbJ.setValue('password',hashlib.sha256(dbJ.getValue('password')).hexdigest())

        logger.info("userRegistration Request password hashed using SHA256")

        # Saving document to MongoDB

        mDBRoles = dbDatabaseName[dbRoles]

        # Find the 'default' role for the end-users (AppUser)

        fRole = mDBRoles.find_one({"default": 1})

        dbJ.setValue("roleId", fRole['_id'])


        res = dbJ.save(dbDatabaseName,dbUsers)

        logger.debug("DB save result: " + str(res))

        if res['errCode'] == 0:

            logger.info("User Registration request successfully completed");

        else:

            logger.error("User Registration request failed. Reason: " + res['errDesc'])

    else:

        logger.critical('Request validation failed. Reason: ' + res['errDesc'])

    return json.dumps(res)




@app.route(userLoginURL, methods=['POST'])
def index():

    logger.info("userLogin Request received")

    logger.debug("Request content: " + str(request.get_json()))

    dbJ = dbJSON(json.dumps(request.get_json()))
    
    # Document validation against json schema

    res = dbJ.validate(userLoginSchemaP)

    logger.debug("Request validation result: " + str(res))

    if res['errCode'] == 0:

        logger.info('Request successfully validated');

        aSession = sosSession('{}')

        aSession.setValue('sessionId', str(dbJ.getValue('sessionId')));

        # Pre-Storing Processing
        
        dbJ.setValue('password',hashlib.sha256(dbJ.getValue('password')).hexdigest())

        logger.info("userLogin Request password hashed using SHA256")

        # Searching for the User in MongoDB

        mDBUsers = dbDatabaseName[dbUsers]

        fUserCnt = mDBUsers.find({"emailAddress": dbJ.getValue('emailAddress'), "password": dbJ.getValue('password')}).count()

        logger.info("User search found " + str(fUserCnt) + " result(s)")

        if fUserCnt > 0:

            fUser = mDBUsers.find_one({"emailAddress": dbJ.getValue('emailAddress'), "password": dbJ.getValue('password')})

            fUserId = fUser['_id']

            fUserName = fUser['name']

            res = aSession.save(dbDatabaseName, dbSessions, fUserName, fUser['_id'], tokenSize)

            logger.info("User Registration request successfully completed");

        else:

            logger.error("User Registration request failed. Reason: " + res['errDesc'])

            res = "{'errCode': 1, 'errDesc': 'Invalid username/password'}";

    else:

        logger.critical('Request validation failed. Reason: ' + res['errDesc'])

    logger.debug("Session save result: " + str(res))

    return json.dumps(res)




# Flask app main

if __name__ == '__main__':
    app.run(debug=True, host=WShost, port=WSport)
