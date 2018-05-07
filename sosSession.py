from jsonschema import validate
import json
import jsonschema
import datetime
import pymongo
from utils import generateRandStr

class sosSession:

    def __init__(self, body):
        self.body = json.loads(body)

    def getValue(self,item):
        return self.body[item]

    def setValue(self,item,value):
        self.body[item]=value
        return 0


    def save(self,dbDBName,dbCollName,sUserName,sUserId,tSize):
    	res={}
    	res['creationDate'] = str(datetime.datetime.now());
    	res['lastHitDate'] = str(datetime.datetime.now());
    	res['authToken'] = generateRandStr(int(tSize));
    	res['name'] = str(sUserName);
    	res['userId'] = str(sUserId);
    	res['sessionId'] = self.body['sessionId'];

        sessions = dbDBName[dbCollName]
        res['_id'] = str(sessions.insert_one(res).inserted_id)
        res['errCode'] = 0

        return res


	def getRole (self, dbDBName, dbRoles, searchItem):

		mDBRoles = dbDBName[dbRoles]

        fRole = mDBRoles.find_one(searchItem)

        return fRole

'''
    def authorize (self, dbDBName, dbCollName, jsonSchemaVar, authToken):
        try:




            rsp = {'errCode': 0, 'errDesc': 'Ok'}
           
        except jsonschema.exceptions.ValidationError as ve:

'''