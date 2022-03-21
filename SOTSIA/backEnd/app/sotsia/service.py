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

@ns_sotsia.route('/get-db-names-sizes', endpoint="get_db_names_sizes")
@ns_sotsia.doc(description="Get a list with the database name and its size")
class get_all_sizes(Resource):
  def get(self):
    databases_size = {"db_sizes": [{}]}
    default_dbs = ['admin', 'local', 'config']
    for db_name in client.list_database_names():
      size = 0
      if db_name not in default_dbs:
        try:
          db = client[db_name]
          print("Connected to database: " + db_name)
          size = db.command("collstats", "data")['totalSize']
          databases_size["db_sizes"][0][db_name] = size
        except:
          print("Connection failed")
    return jsonify(databases_size)

@ns_sotsia.route('/get-db-names-meta', endpoint="get_db_names_meta")
@ns_sotsia.doc(description="Get a list with the database name and its meta keys")
class get_all_meta_keys(Resource):
  def get(self):
    databases_keys = {"meta_keys": [{}]}
    default_dbs = ['admin', 'local', 'config']
    for db_name in client.list_database_names():
      meta_keys = []
      if db_name not in default_dbs:
        try:
          db = client[db_name]
          print("Connected to database: " + db_name)
          collection = db.meta
          item = collection.find_one()
          meta_keys = item['keys']
          databases_keys["meta_keys"][0][db_name] = meta_keys
        except:
          print("Connection failed")
    return jsonify(databases_keys)

# @ns_sotsia.route('/machine-learning/xgboost', endpoint="machine_learning_xgboost")
# @ns_sotsia.doc(description="Experiment with the XGBoost algorithm")
# class machine_learning_xgboost(Resource):
#   def get(self):
#     from pandas import DataFrame
#     try:
#       db = client['ICPE']
#       print("Connected to database: ICPE")
#       collection = db.data
#       data = collection.find()
#       print(data)
#       list_cur = list(data)
#       df = DataFrame(list_cur)
#       print(df.head())
#     except:
#       print("Connection failed")

#     return jsonify({'hello': 'ok'})