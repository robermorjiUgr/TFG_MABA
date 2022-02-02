from json import JSONEncoder
from flask import jsonify
from . import dataset_bp
from app.database.connection import connectionMongo as _mongo

from bson import json_util
import json

#Function that get all name database allow access user. 
@dataset_bp.route('/dbName',methods=['GET'])
def getNameDataBase():
   
    # List Name DataBase
    dbs = _mongo.list_name_database()
    list_dbName = []
    
    for db in dbs:
        database ={db:db}
        list_dbName.append(database)

    return jsonify(list_dbName)


# Function that list the fifty first elements from a database. 
@dataset_bp.route('/data',methods=['GET'])
def getData():
    
    # Get data from selected bbdd. The fifty first elements. 
    data = _mongo.get_data('icpe') 
    data_db = []
   
    for db in data:
        data_db.append(db)

    collection = json.loads(json_util.dumps(data_db))

    return jsonify(collection)