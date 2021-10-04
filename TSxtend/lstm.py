#PYTHON
import os
import ipdb
import math
import click 
import yaml

import matplotlib.pyplot as plt

#DATASCIENCE
import numpy as np
import pandas as pd



#MLFLOW
import  mlflow
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import Schema, ColSpec

#OWN
import Collection.collection  as collect

#KERAS
import keras
from keras.datasets import imdb
from keras.preprocessing import sequence
from keras import layers
from keras.models import Sequential,Model
from keras.layers import Embedding, SimpleRNN,LSTM,Dense,Input, Flatten
from keras.optimizers import RMSprop
from keras.layers.merge import concatenate
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D
from keras.losses import Huber


#SKLEARN
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2

@click.command(help="Dado un fichero CSV, transformar en un artefacto mlflow")
@click.option("--file_analysis_train", type=str,default=None)
@click.option("--file_analysis_test", type=str,default=None)
@click.option("--artifact_uri", type=str,default=None)
@click.option("--experiment_id", type=str,default=None)
@click.option("--run_id", type=str,default=None)
@click.option("--input_dir_train", type=str,default=None)
@click.option("--input_dir_test", type=str,default=None)
@click.option("--output_dir", type=str,default=None)
@click.option("--model_input", type=str,default=None)
@click.option("--model_output", type=str,default=None)
@click.option("--n_rows",  default=0.0,  type=float)
@click.option("--n_steps", type=int, default=3, help="n_steps redes convulacionales")
@click.option("--epochs", type=int, default=10, help="Epochs")
@click.option("--hidden_units", type=int, default=50, help="Hidden Units")
@click.option("--batch_size", type=int, default=72, help="Batch Size")
@click.option("--verbose", type=int, default=1, help="Verbose")

def lstm(file_analysis_train,file_analysis_test, artifact_uri,experiment_id, run_id, input_dir_train,input_dir_test, model_input,model_output,n_rows,
n_steps,epochs,hidden_units,batch_size,verbose,output_dir):
    
    
    name_place  = file_analysis_train.split(".csv")[0].split("train_")[1]
    result_dir  = output_dir + name_place +"/lstm/"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    
    # for file_analysis in list_file:
    print(str(file_analysis_train))
    mlflow.set_tag("mlflow.runName", "LSTM -  " + str(file_analysis_train.replace(".csv","").replace("train_","")))
   
    path = input_dir_train+ "/"+file_analysis_train
   
    df_origin = load_data(path,n_rows)
    
    print("LSTM: " + str(file_analysis_train))

    if model_input:
        model_input = model_input.split(",")
        df = df_origin.filter(  model_input , axis=1)
    else:
        df = df_origin
   
    ### Normalización de los datos
    scaler = MinMaxScaler(feature_range=(0, 1))
    df = scaler.fit_transform(df) 
    
    # Split  train, validate and test
    # train,  validate, test = np.split(df,[ int( .8*len(df) ), int( .95 * len(df)) ] )        
    train,validate = np.split(df,[ int( .9*len(df) ) ])
    # Preparation data sequences TRAIN
    X,y = preparation_data(train, n_steps, model_input)
        
    # Preparation data sequences VALIDATE
    validate_X,validate_y = preparation_data(validate, n_steps, model_input)
    
    # Preparation data sequences TEST
    path = input_dir_test+ "/"+file_analysis_test
    df_origin = load_data(path,n_rows)

    print("LSTM Test: " + str(file_analysis_test))
    
    if model_input:
        df = df_origin.filter(  model_input , axis=1)
    else:
        df = df_origin

    scaler = MinMaxScaler(feature_range=(0, 1))
    df = scaler.fit_transform(df) 
    
    test = df
    test_X,test_y = preparation_data(test, n_steps, model_input)
    
        
    
    # MODEL
    # opt = keras.optimizers.RMSprop()
    opt = keras.optimizers.SGD(lr=1e-5, momentum=0.9)
    model = Sequential()
    model.add(Conv1D(filters=hidden_units, kernel_size=5,strides=1,padding="causal",
    activation='relu',input_shape=(X.shape[1], X.shape[2])))
    model.add(LSTM(hidden_units,return_sequences=True))
    model.add(LSTM(hidden_units,return_sequences=True))
    model.add(LSTM(hidden_units))
    model.add(Dense(1))
    model.compile(loss=keras.losses.Huber(), optimizer=opt,metrics=['mae','mse'])
    history = model.fit(
                X, y,
                epochs=epochs, 
                batch_size=batch_size,
                validation_data=(validate_X, validate_y),
                verbose=1,shuffle=False)
  
    # PREDICT TRAIN
    test_predict = model.predict(test_X,verbose=0)
    (rmse, mae, mse, r2) = eval_metrics(test_y, test_predict)
    print(rmse, mae, mse, r2)
    
    plt.plot(test_y,label="Actual")
    plt.plot(test_predict,label="Prection")
    plt.legend()
    plt.savefig(result_dir+"lstm_"+name_place)
    plt.close()
    
    name_model = "model_lstm_"+file_analysis_train.replace(".csv","")
    
    # SCHEMA MODEL MLFlow  
    
    _list_input_schema  = model_input[:-1]
    _list_output_schema = model_output.split(',')
    _list_input_schema = list ( set(_list_input_schema) - set(_list_output_schema))

    _listColSpec= [ColSpec("double",item) for item in _list_input_schema]
    input_schema = Schema(_listColSpec)
    
    _listColSpec = [ColSpec("double",item) for item in _list_output_schema]
    output_schema = Schema(_listColSpec)
    # SAVE SCHEMA MODEL
    signature = ModelSignature(inputs=input_schema, outputs=output_schema)
    # LOG MODEL ARTIFACTS
    # mlflow.keras.log_model(keras_model=model,signature=signature,artifact_path=result_dir)

    #import ipdb; ipdb.set_trace()
    plt.title(file_analysis_train)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.plot(history.history['mae'])
    plt.plot(history.history['val_mae'])
    plt.plot(history.history['mse'])
    plt.plot(history.history['val_mse'])
    plt.title('MAE and Loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train loss', 'validate loss','mae','val_mae'], loc='upper left')
    plt.savefig(result_dir+"lstm__metrics_"+name_place)

    # import ipdb;ipdb.set_trace();
    #mlflow.log_artifact(result_dir+"lstm__metrics_"+name_place+".png")
    mlflow.log_metric("rmse", rmse)
    mlflow.log_metric("mae", mae)
    mlflow.log_metric("mse", mse)
    mlflow.log_metric("r2",r2)

    logs(result_dir,"lstm.txt",rmse,mae,mse,r2)
        
def load_data( path, n_rows, fields=None):
    dataframe = collect.Collections.readCSV(path,n_rows,fields)
    return dataframe
       
def split_sequences(sequences, n_steps):
    X, y = list(), list()
    for i in range(len(sequences)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the dataset
        if end_ix > len(sequences):
            break
        # Input and Output parts of the pattern
        seq_x, seq_y = sequences[i:end_ix, :-1], sequences[end_ix-1, -1]
        X.append(seq_x)
        y.append(seq_y)
    return np.array(X), np.array(y)

def preparation_data(data, n_steps, model_input):
    in_seq=[]
    # Preparation data sequences TRAIN
    for indx in range(0,len(model_input)-1):
        in_seq.append(np.array(data[:,indx]))
    out_seq = np.array(data[:,len(model_input)-1])

    reshape_seq = []

    for in_seq_ in in_seq:
        reshape_seq.append(in_seq_.reshape(len(in_seq_),1))
    out_seq = out_seq.reshape((len(out_seq),1))
    reshape_seq.append(out_seq)

    dataset = np.hstack((reshape_seq))
    return split_sequences(dataset, n_steps)

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mse = mean_squared_error(actual, pred)
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, mse, r2

def logs (path,filename,rmse, mse, mae, r2):
    # import ipdb; ipdb.set_trace()
    print(filename)
    FILENAME =  path + filename
    f = open(FILENAME,"w+")
    
    f.write("\nrmse: " +    str(rmse))
    f.write("\nmse: "  +    str(mse))
    f.write("\nmae: "  +    str(mae))
    f.write("\nr2: "   +    str(r2))
    
    f.close()

if __name__ == '__main__':
    lstm()
