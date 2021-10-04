# Class Collections

Class  where localitation all methods for realice insert data in DataBase, such as distinct operation realize with every DataFrames.
Actually implements methods:
    
1. readCSV ( self, path, fields=[]): Read CSV from DataFrame.

2. insertCollection (self, df_final, db_name).

3. MergeDataFrame ( self, dataframe1, dataframe2, on=[]).


## readCSV
---

def readCSV ( self, path, fields=[])

*   Description: 
    
       It reads every CSV, as long as it passes the structure of the file to be read by argument.

*   Arguments:
    
    self: Object class.

    path: Path where is store CSV file.

    fields: Structure of the file to be read.

*   Returns:
    
    self.DataFrame: DataFrame created.

    ```
    def readCSV ( self, path, fields=[]):
        if not fields:
            print(" Fields is empty, please, insert arguments list fields")
        
        self.dataFrame = pd.read_csv(path, skipinitialspace=True, usecols=fields)
        
        return self.dataFrame

    ```

##  insertCollection
---
def  insertCollection (self, df_final, db_name)

*   Description: 
    
    Insert data, via a DataFrame, into the database.

*   Arguments:
self, df_final, db_name
    
    self: Object class.

    df_final: DataFrame insert in collection.

    db_name: Name database. 

*   Returns: empty

```
def insertCollection(self, df_final, db_name):
    _objMongoDB = mongo.MongoConnection(config.URI_CONNECTION,config.MONGODB_TIMEOUT,config.MONGODB_HOST)
    client_mongoDB = _objMongoDB.connection_bbdd()
    db = client_mongoDB.db_name
    collections = db.sensors
    _objMongoDB.insert_collection_dataFrame_ashrae(collections, df_final)
```

## MergeDataFrame
---

MergeDataFrame ( self, dataframe1, dataframe2, on=[])

*   Description:
    Join two DataFrames

*   Arguments:
    self: Object class.

    dataframe1: DataFrame.

    dataframe2: DataFrame.

    on: Column or index level names to join on. These must be found in both DataFrames. If on is None and not merging on indexes then this defaults to the intersection of the columns in both DataFrames.


*   Return:  DataFrame merge.

    ```
    def MergeDataFrame(self, dataframe1, dataframe2, on=[] ):
        return pd.merge( dataframe1,  dataframe2, on=on )
    ```