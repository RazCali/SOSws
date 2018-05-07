from jsonschema import validate
import json
import jsonschema
import datetime
import pymongo

class sosSession:

    def __init__(self, body):
        self.body = json.loads(body)

    def getValue(self,item):
        return self.body[item]

    def setValue(self,item,value):
        self.body[item]=value
        return 0

    def save(self,dbDBName,dbCollName):
        self.body['creationDate'] = datetime.datetime.now()
        objects = dbDBName[dbCollName]

        try:
            session_id = objects.insert_one(self.body).inserted_id
            rsp = {'errCode': 0, 'ObjectId': str(user_id)}

        except pymongo.errors.DuplicateKeyError as me:
            rsp = {'errCode': -2, 'errDesc': str(me)}

        return rsp

	def generate(self, sUser):

		if 'sessionId' in self.body:

			self.body['authToken'] = generateRandStr(int(tokenSize));

			self.body['userId'] = sUser['_id']

			self.body['userRoleId'] = sUser['roleId'];

		else:

			res['errCode'] = -3

			res['errDesc'] = 'Session creation failed'

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