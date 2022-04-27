from urllib import request
from flask import jsonify, send_file
from flask import Blueprint
from flask_restx import Api, Resource
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt

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

@ns_sotsia.route('/deep-learning/lstm', endpoint="deep_learning_lstm")
@ns_sotsia.doc(description="Experiment with the Long Short-Term Memory (LSTM) network algorithm")
class deep_learning_lstm(Resource):
  def get(self):
    from pandas import DataFrame
    from app.lib import lstm, lstm_algorithm
    result = {"result": ""}
    try:
      db = client['ICPE']
      print("Connected to database: ICPE")
      collection = db.actualizada    # CAMBIAR!! Primero lo hacemos con una colección más pequeña (prueba) para evitarnos tiempos muy largos
      dataMongo = collection.find()
      list_cur = list(dataMongo)
      data = DataFrame(list_cur)

      bytes_img = lstm_algorithm.lstm(data)

      return send_file(bytes_img, attachment_filename='plot.png', mimetype='image/png')
      print(encoded)
      print()
      from base64 import decodebytes
      
      
      return encoded
      
      result["result"] = "OK"
    except:
      print("Error encountered")
      result["result"] = "ERROR"

    return jsonify(result)

@ns_sotsia.route('/machine-learning/xgboost', endpoint="machine_learning_xgboost")
@ns_sotsia.doc(description="Experiment with the XGBoost algorithm")
class machine_learning_xgboost(Resource):
  def get(self):
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