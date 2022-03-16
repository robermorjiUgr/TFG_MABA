from urllib import request
from flask import jsonify
from flask import Blueprint
from flask_restx import Api, Resource
import pandas as pd
import json
import numpy as np

sotsia_bp = Blueprint('sotsia', __name__)
api = Api( sotsia_bp )
ns_sotsia = api.namespace('sotsia', "Proyect api dashboard SOTSIA:")

# Connect to database
from flask_pymongo import MongoClient
client = MongoClient("mongodb://localhost")

@ns_sotsia.route('/get-db-names', endpoint="get_db_names")
@ns_sotsia.doc(description="Get a list with the names of the databases created")
class get_db_names(Resource):
  def get(self):
    databases = []
    default_dbs = ['admin', 'local', 'config']
    for db in client.list_database_names():
      if db not in default_dbs:
        databases.append(db)
    return jsonify({'databases': databases})

@ns_sotsia.route('/<database>/get-collection-keys', endpoint="get_collection_keys")
@ns_sotsia.doc(description="Get a list with the names of all the key names in the collection data")
class get_collection_keys(Resource):
  def get(self, database):
    meta_keys = []
    try:
      db = client[database]
      print("Connected to database: " + database)
      collection = db.meta
      item = collection.find_one()
      meta_keys = item['keys']
    except:
      print("Connection failed")

    return jsonify({'keys': meta_keys})

@ns_sotsia.route('/<database>/get-size', endpoint="get_size")
@ns_sotsia.doc(description="Get the size of the data collection given a database name")
class get_database_size(Resource):
  def get(self, database):
    size = 0
    try:
      db = client[database]
      print("Connected to database: " + database)
      size = db.command("collstats", "data")['totalSize']
    except:
      print("Connection failed")

    return jsonify({'total_size': size})


# @ns_sotsia.route('/<database>',endpoint="database")
# @ns_sotsia.doc(description="Get ICPE")
# class icpe_get(Resource):
#   def get(self, database):
#     db = client.database
#     cursor = db.data.find({'sensor': 'C13 - L1 - Current'})
#     list_cur = list(cursor)
#     # Converting to the JSON
#     json_data = json.dumps(list_cur) 
#     return jsonify(json_data)
