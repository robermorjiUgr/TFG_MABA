import pymongo
from pymongo import MongoClient
from config import dev

class connectionMongo:

    # Function that get list names databases
    def list_name_database():
        dbs = MongoClient(dev.CONNECTION_STRING).list_database_names()
        return dbs

    #Function that get first 50 elements from database.
    def get_data(dbName):
        client = MongoClient(dev.CONNECTION_STRING)
        db = client[dbName]
        collection = db['data']
        cursor = collection.find({}).limit(50)
        return cursor