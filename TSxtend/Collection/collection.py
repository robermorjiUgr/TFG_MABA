#PYTHON
import os

#DATASCIENCE
import pandas as pd


"""
Class Collections
==========================================

Clase donde se encuentran los métodos para realizar inserción de los datos en las distintas BBDD, así como distintas operciones que se 
pueden realizar con los distintos DataFrames.

Métodos implementados actualmente: 
    a) readCSV: Lectura directa del CSV a DataFrame
    b) insertCollectionAshrae(self, df_final): Inserción de datos en la colección de datos Ashrae
    c) insertCollectionICPE(self, df_final): Inserción de datos en la colección de datos ICPE
    d) insertCollectionOcupation(self, df_final): Inserción de datos en la colección de datos OCUPATION
    e) MergeDataFrame: para unir por columnas dos dataframe.
     


"""

class Collections:

      
    def __init__(self):
        self.dataFrame = pd.DataFrame()

    def getDataFrame(self):
        return self.dataFrame
    
    def setDataFrame(self, dataFrame):
        self.dataFrame = dataFrame
    
   
    @staticmethod
    def readCSV (path, n_rows, fields=None):
       
        if n_rows!=0:
            if not fields:
                dataFrame = pd.read_csv(path, skipinitialspace=True, nrows=n_rows,index_col=0)
            else:
                dataFrame = pd.read_csv(path, skipinitialspace=True, usecols=fields,nrows=n_rows)
        else:
            if not fields:
                dataFrame = pd.read_csv(path, skipinitialspace=True)
            else:
                dataFrame = pd.read_csv(path, skipinitialspace=True, usecols=fields)
       
        return dataFrame
    
    @staticmethod
    def createDir ( path ):
        try:
            # Create target Directory
            os.makedirs(path)
            print("Directory " , path ,  " Created ") 
        except FileExistsError:
            print("Directory " , path ,  " already exists")
    
    @staticmethod
    def createCSV(dataframe, path, name,index=True):
        dataframe.to_csv(path+name,encoding='utf-8',index=index)

    
    
    # def insertCollection(self, df_final, db_name):
    #     _objMongoDB = mongo.MongoConnection(config.URI_CONNECTION,config.MONGODB_TIMEOUT,config.MONGODB_HOST)
    #     client_mongoDB = _objMongoDB.connection_bbdd()
    #     db = client_mongoDB.db_name
    #     collections = db.sensors
    #     _objMongoDB.insert_collection_dataFrame_ashrae(collections, df_final)

    # def insertCollectionAshrae(self, df_final):
        
    #     _objMongoDB = mongo.MongoConnection(config.URI_CONNECTION,config.MONGODB_TIMEOUT,config.MONGODB_HOST)
    #     client_mongoDB = _objMongoDB.connection_bbdd()
    #     db = client_mongoDB.ashrae
    #     collections = db.sensors
    #     _objMongoDB.insert_collection_dataFrame_ashrae(collections, df_final)
    
    # def insertCollectionICPE(self, df_final):
       
    #     _objMongoDB = mongo.MongoConnection(config.URI_CONNECTION,config.MONGODB_TIMEOUT,config.MONGODB_HOST)
    #     client_mongoDB = _objMongoDB.connection_bbdd()
    #     db = client_mongoDB.icpe
    #     collections = db.sensors
    #     _objMongoDB.insert_collection_dataFrame_icpe(collections, df_final)
    
    # def insertCollectionOcupation(self, df_final):
       
    #     _objMongoDB = mongo.MongoConnection(config.URI_CONNECTION,config.MONGODB_TIMEOUT,config.MONGODB_HOST)
    #     client_mongoDB = _objMongoDB.connection_bbdd()
    #     db = client_mongoDB.ocupation
    #     collections = db.sensors
    #     _objMongoDB.insert_collection_dataFrame_ocupation(collections, df_final)

    # def MergeDataFrame(self, dataframe1, dataframe2, on=[] ):
    #     return pd.merge( dataframe1,  dataframe2, on=on )