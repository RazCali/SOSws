from jsonschema import validate
import json
import jsonschema
import datetime
import pymongo

class dbJSON:

    def __init__(self, body):
        self.body = json.loads(body)

    def validate (self, jsonSchemaVar):
        try:
            validate(self.body, jsonSchemaVar)

            rsp = {'errCode': 0, 'errDesc': 'Ok'}
           
        except jsonschema.exceptions.ValidationError as ve:

            rsp = {'errCode': -1, 'errDesc': str(ve)}

        return rsp

    def getValue(self,item):
        return self.body[item]

    def setValue(self,item,value):
        self.body[item]=value
        return 0

    def save(self,dbDBName,dbCollName):
        self.body['creationDate'] = datetime.datetime.now()
        objects = dbDBName[dbCollName]

        del self.body['authHeader']

        try:
            user_id = objects.insert_one(self.body).inserted_id
            rsp = {'errCode': 0, 'ObjectId': str(user_id)}

        except pymongo.errors.DuplicateKeyError as me:
            rsp = {'errCode': -2, 'errDesc': str(me)}

        return rsp


'''
with open('schema//userRegistration_Req.json', 'r') as f:
   userRegistrationSchemaP = json.loads(f.read())
   
dbJ = dbJSON('{"a": "ceva"}')

rs = dbJ.validate(userRegistrationSchemaP)

print rs['errCode']

print dbJ.validate(userRegistrationSchemaP)
print dbJ.get('a')
'''
