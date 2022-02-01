from json import JSONEncoder
from flask import jsonify
from . import dataset_bp
import pymongo
from pymongo import MongoClient

from bson import json_util
import json



#Function that get all name database allow access user. 
def list_name_database():
    dbs = MongoClient('127.0.0.1:27017',
                     username='myUserTest',
                     password='123456',
                     authMechanism='SCRAM-SHA-256').list_database_names()
    return dbs

#Function that get first 50 elements from database.
def get_data(dbName):
    client = MongoClient('127.0.0.1:27017',
                     username='myUserTest',
                     password='123456',
                     authMechanism='SCRAM-SHA-256')
    
    db = client[dbName]
    collection = db['data']
    cursor = collection.find({}).limit(50)
    return cursor


@dataset_bp.route('/dbName',methods=['GET'])
def getNameDataBase():
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer las bases de datos correspondientes
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
    dbs = list_name_database() 
    list_dbName = []
    # To DO:
    for db in dbs:
        database ={db:db}
        list_dbName.append(database)
    return jsonify(list_dbName)


@dataset_bp.route('/data',methods=['GET'])
def getData():
    ''''
    To do: 
      Conectar  con la Base de Datos de Mongo
      Traer los datos correspondientes de la base de datos seleccionada
      Almacenarlas en una variable
      Finalmente empaquetarla en un diccionario y enviarlos
    '''
    data = get_data('icpe') 
    data_db = []
    # To DO:
    for db in data:
        data_db.append(db)

    collection = json.loads(json_util.dumps(data_db))

    return jsonify(collection)