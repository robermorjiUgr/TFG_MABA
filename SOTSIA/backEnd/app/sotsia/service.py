from urllib import request
from flask import jsonify, send_file
from flask import Blueprint
from flask_restx import Api, Resource
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from pandas import DataFrame
from base64 import encode, encodestring, decodestring
from flask import request


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
    '''Get a list with the DB names'''
    databases = []
    default_dbs = ['admin', 'local', 'config']
    for db in client.list_database_names():
      if db not in default_dbs:
        databases.append(db)
    return jsonify({'databases': databases})

@ns_sotsia.route('/<database>/get-collection-keys', endpoint="get_collection_keys")
@ns_sotsia.doc(
  description="Get a list with the names of all the key names in the collection data",
  params={'database': 'The name of the database'}
)
class get_collection_keys(Resource):
  def get(self, database):
    '''Get a list with the collection keys of a database'''
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
@ns_sotsia.doc(
  description="Get the size of the data collection given a database name",
  params={'database': 'The name of the database'}
)
class get_database_size(Resource):
  def get(self, database):
    '''Get the size of a database'''
    size = 0
    try:
      db = client[database]
      print("Connected to database: " + database)
      size = db.command("collstats", "data")['totalSize']
    except:
      print("Connection failed")

    return jsonify({'total_size': size})

@ns_sotsia.route('/<database>/get-min-max-date', endpoint="get_min_max_date")
@ns_sotsia.doc(
  description="Get the min and max date of the database",
  params={'database': 'The name of the database'}
)
class get_min_max_date(Resource):
  def get(self, database):
    '''Get the min and max date of the documents inserted in a database'''
    min_date = max_date = 0
    try:
      db = client[database]
      print("Connected to database: " + database)
      collection = db.actualizada    # CAMBIAR!! Primero lo hacemos con una colección más pequeña (prueba) para evitarnos tiempos muy largos
      dataMongo = collection.find()
      list_cur = list(dataMongo)
      data = DataFrame(list_cur)
      data = data.sort_values(by='date')
      min_date = data['date'].iloc[1]
      max_date = data['date'].iloc[-1]
    except:
      print("Connection failed")

    return jsonify({'min_date': min_date, 'max_date': max_date})

@ns_sotsia.route('/get-db-names-sizes', endpoint="get_db_names_sizes")
@ns_sotsia.doc(description="Get a list with the database name and its size")
class get_all_sizes(Resource):
  def get(self):
    '''Get a list with the DB names and sizes'''
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
    '''Get a list with the DB names and meta information'''
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

@ns_sotsia.route('/deep-learning/lstm/<database>', endpoint="deep_learning_lstm")
@ns_sotsia.doc(
  description="Experiment with the Long Short-Term Memory (LSTM) network algorithm",
  params={
    'dataset': 'Dataset parameters with the form key1=value1&key2=value2&...&keyn=valuen',
    'id_sensor': 'ID of the sensor to apply in the LSTM algorithm'
  }
)
class deep_learning_lstm(Resource):
  @ns_sotsia.response(200, 'Execute LSTM algorithm')
  @ns_sotsia.response(500, 'Internal Server error')
  def get(self, database):
    '''Experiment with LSTM (Deep Learning)'''
    from app.lib import lstm, lstm_algorithm
    from datetime import datetime
    result = {"result": ""}
    try:
      db = client[database]
      print("Connected to database: " + database)
      collection = db.actualizada    # CAMBIAR!! Primero lo hacemos con una colección más pequeña (prueba) para evitarnos tiempos muy largos
      # GET the arguments passed in the url query
      args = request.args
      start_date = args.get("start_date", type=str)
      end_date = args.get("end_date", type=str)
      id_sensor = args.get("id_sensor", type=int)

      # Parse to datetime type
      start_date = datetime.strptime(start_date,'%Y-%m-%d')
      end_date = datetime.strptime(end_date,'%Y-%m-%d')

      # Get the filtered data
      dataMongo = collection.find({
        #'ID_Sensor': int(id_sensor),
        'date': {
          '$gte': start_date,
          '$lte': end_date
        }
      })

      list_cur = list(dataMongo)
      data = DataFrame(list_cur)

      bytes_img = lstm_algorithm.lstm(data, id_sensor)
      encoded_img = encodestring(bytes_img.getvalue()) # encode as base64
      
      # result = {"result": encoded_img.decode(encoding='utf-8')}
      # return result

      return send_file(bytes_img, attachment_filename='plot.png', mimetype='image/png')
    except:
      print("Error encountered")
      result["result"] = "ERROR"

    return jsonify(result)

@ns_sotsia.route('/machine-learning/xgboost', endpoint="machine_learning_xgboost")
@ns_sotsia.doc(description="Experiment with the XGBoost algorithm")
class machine_learning_xgboost(Resource):
  def get(self):
    '''Experiment with XGBoost (Machine Learning)'''
    from pandas import DataFrame
    from sklearn.metrics import mean_squared_error
    try:
      db = client['ICPE']
      print("Connected to database: ICPE")
      collection = db.prueba
      dataMongo = collection.find()
      list_cur = list(dataMongo)
      data = DataFrame(list_cur)
      print("Dataframe created correctly")
      print(data.head())
      #data.info()
      X, y = data.iloc[:,:-1],data.iloc[:,-1]
      print("iloc")
      print(X)

      print(y)
     # data_dmatrix = xgb.DMatrix(data=X,label=y)
      print("dmatrix")
      from sklearn.model_selection import train_test_split
      X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)
      print("train")
      # xg_reg = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.1,
      #           max_depth = 5, alpha = 10, n_estimators = 10)
      # print("regression")
      # xg_reg.fit(X_train,y_train)
      # print("fit")
      # preds = xg_reg.predict(X_test)
      # print("pred")
      # rmse = np.sqrt(mean_squared_error(y_test, preds))
      # print("RMSE: %f" % (rmse))
    except:
      print("Connection failed")

    return jsonify({'hello': 'ok'})


@ns_sotsia.route('/plot-dataset', endpoint="plot_dataset")
@ns_sotsia.doc(description="Plot the data of the dataset")
class plot_dataset(Resource):
  def get(self):
    '''Test how to plot the data in the API'''
    from pandas import DataFrame
    try:
      db = client['ICPE']
      print("Connected to database: ICPE")
      collection = db.actualizada
      dataMongo = collection.find()
      list_cur = list(dataMongo)
      data = DataFrame(list_cur)
      print("Dataframe created correctly")
      print(data.head())
      
      # Filtrar por type
      data = data.loc[data['Type']=='E']

      # Obtenemos lista de los sensores que hay en el dataset
      list_sensors = data.ID_Sensor.unique()

      from random import randint
      # Sacamos gráfica de cada sensor
      for sensor in list_sensors:
        # Filtramos el dataset para obtener sólo los datos del sensor correspondiente
        data_sensor = data.loc[data['ID_Sensor']==sensor]
        # Ordenamos por fecha para que no se pinte la gráfica mal
        data_sensor = data_sensor.sort_values(by='date')
        # Obtenemos el valor de la columna date
        date = data_sensor['date']
        # Convertimos a numpy array para que la pinte sin problema
        date = date.to_numpy()
        values = data_sensor['value']
        values = values.to_numpy()
        # Obtenemos un color aleatorio para diferenciar mejor
        color = '#%06X' % randint(0, 0xFFFFFF)
        plt.plot(date, values, color=color, label=sensor)
      
      plt.title('ICPE - Sensors values')
      plt.xlabel('Date')
      plt.ylabel('Values')
      plt.legend()

      import io
      bytes_image = io.BytesIO()
      plt.savefig(bytes_image, format="png")
      bytes_image.seek(0)
      return send_file(bytes_image, attachment_filename='plot.png', mimetype='image/png')
    except:
      print("Connection failed")

    return jsonify({'hello': 'ok'})


@ns_sotsia.route('/<database>/update-meta-collection', endpoint="update_meta_collection")
@ns_sotsia.doc(
  description="Update the meta collection of the database",
  params={'database': 'The name of the database'}
)
class update_meta_collection(Resource):
  def get(self, database):
    '''Update the meta collection of a database'''
    result = {"result": ""}
    try:
      db = client[database]
      print("Connected to database: ICPE")
      # Connect to the data collection
      collection = db.actualizada
      
      # Get the max value of the column date
      max_date = collection.find_one(sort=[("date", -1)])["date"]
      # Get the minimum date value and format it correctly
      min_date = collection.find_one(sort=[("date", 1)])["date"]

      # Get all the keys of the collection using an aggregation
      keys = collection.aggregate([ 
        { "$project": { "arrayofkeyvalue": { "$objectToArray": "$$ROOT" } } }, 
        { "$unwind": "$arrayofkeyvalue" }, 
        { "$group": { "_id": None, "allkeys": { "$addToSet": "$arrayofkeyvalue.k" } } }
      ])
      # keys is a CommandCursor variable so we transform it into a DataFrame
      list_cur = list(keys)
      data = DataFrame(list_cur)
      # Once it's a DataFrame, we get the first (and only) row and the column 'allkeys' 
      keys = data.loc[0, 'allkeys']   # This is an array with all the keys (OK to return it with JSON)
      

      # Connect to the meta collection
      collection = db.meta
      # We drop the previous data
      collection.drop()
      # Insert the new meta data of the database
      collection.insert_one({'keys': keys, 'min_date': min_date, 'max_date': max_date})

      result["result"] = {'keys': keys, 'min_date': min_date, 'max_date': max_date}
    except:
      print("Error encountered")
      result["result"] = "ERROR"

    return jsonify(result)

