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
from keras.datasets import imdb
from keras.preprocessing import sequence
from keras import layers
from keras.models import Sequential,Model
from keras.layers import Embedding, SimpleRNN,LSTM,Dense,Input, Flatten
from keras.optimizers import RMSprop
from keras.layers.merge import concatenate
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D

#SKLEARN
from sklearn import tree
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import auc, accuracy_score, confusion_matrix, mean_squared_error
from sklearn.model_selection import cross_val_score, GridSearchCV, KFold, RandomizedSearchCV, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

#XGBOOST
import xgboost as xgb
from  xgboost import DMatrix




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
@click.option("--max_depth", type=int, default=1, help="max_depth")
@click.option("--criterion", type=str, default='mse', help="criterion")
@click.option("--splitter", type=str, default="best", help="splitter")
@click.option("--min_samples_split", type=int, default=2, help="min_samples_split")
@click.option("--min_samples_leaf", type=int, default=1, help="min_samples_leaf")
@click.option("--min_weight_fraction_leaf", type=float, default=0., help="min_weight_fraction_leaf")
@click.option("--max_features", type=str, default="auto", help="max_features")
@click.option("--max_leaf_nodes", type=int, default=2, help="max_leaf_nodes")
@click.option("--random_state", type=int, default=0, help="random_state")
@click.option("--figure", type=str, default=False, help="figure")
@click.option("--n_splits", type=int, default=False, help="figure")

def DecisionTree(file_analysis_train,file_analysis_test,artifact_uri,experiment_id, run_id, input_dir_train,input_dir_test,model_input,model_output,n_rows,
max_depth, criterion, splitter,min_samples_split, min_samples_leaf, min_weight_fraction_leaf,max_features, random_state,
max_leaf_nodes, figure, n_splits,output_dir):
    
    # import ipdb; ipdb.set_trace();
    
    name_place  = file_analysis_train.split(".csv")[0].split("train_")[1]
    result_dir  = output_dir + name_place +"/dtree_regression/"
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
 
    # for file_analysis in list_file:
    print(str(file_analysis_train))
    mlflow.set_tag("mlflow.runName", "DECISION TREE REGRESSOR -  " + str(file_analysis_train.replace(".csv","").replace("train_","")))
    path = input_dir_train+ "/"+file_analysis_train
    df_origin = load_data(path,n_rows)
    
    print("DECISION  TREE REGRESSOR: " + str(file_analysis_train))

 
    # Field Input Model
    if model_input:
        model_input = model_input.split(',')
        df = df_origin.filter(  model_input , axis=1)
    else:
        df = df_origin
    
    # Data Normalize
    scaler = MinMaxScaler(feature_range=(0, 1))
    df = scaler.fit_transform(df) 
    # X: All columns except last columns.
    # y: last column.
    X = df[:,0:len(model_input)-1]
    y = df[:,len(model_input)-1:]

    path = input_dir_test + "/"+file_analysis_test
    df_origin = load_data(path,n_rows)  

    print("DECISION  TREE REGRESSOR: " + str(file_analysis_test))
    
    # Field Input Model
    if model_input:
        df = df_origin.filter(  model_input , axis=1)
    else:
        df = df_origin
    
    # Data Normalize
    scaler = MinMaxScaler(feature_range=(0, 1))
    df = scaler.fit_transform(df) 

    test_X = df[:,0:len(model_input)-1]
    test_y = df[:,len(model_input)-1:]

    kfold = KFold(n_splits=n_splits, shuffle=True, random_state=42)

    scores=[]
    dtree_model =  DecisionTreeRegressor(max_depth=max_depth, criterion=criterion, splitter=splitter,
                                     min_samples_split=min_samples_split, min_samples_leaf=min_samples_leaf,
                                     min_weight_fraction_leaf=min_weight_fraction_leaf, max_features=max_features,
                                     random_state=random_state, max_leaf_nodes=max_leaf_nodes)

    idx = 1
    for train_index, test_index in kfold.split(X):   
        X_train, X_test = X[train_index], test_X[test_index]
        y_train, y_test = y[train_index], test_y[test_index]

        dtree_model.fit(X_train, y_train.ravel())
        y_pred = dtree_model.predict(X_test)

        scores.append(mean_squared_error(y_test, y_pred))
        plt.plot(y_test,label="Actual")
        plt.plot(y_pred,label="Prection")
        plt.legend()
        plt.savefig(result_dir+"dtree_regressor_"+name_place+"_split_"+str(idx))
        plt.close()
        idx += 1
        # scores.append(mean_absolute_error(y_test,y_pred))
    
    display_scores(np.sqrt(scores))
    logs(result_dir,"dtree_regressor.txt",scores,np.mean(scores),np.std(scores))
    
    for idx in range(len(scores)):
        mlflow.log_metric("scores",scores[idx], step=idx+1 )
    mlflow.log_metric("mean", np.mean(scores))
    mlflow.log_metric("std", np.std(scores))
    
    model_output = model_output.split(',')
    # tree.plot_tree(dtree_model,
    #             feature_names = model_input, 
    #             class_names= model_output,
    #             filled = True)
    
    # PLOT
    plt.title("Decision Tree Regression: KFold(n_split="+str(n_splits)+")")
    plt.bar(range(len(scores)), scores)
    plt.savefig(result_dir+"dtree_regressor_"+name_place) 
    name_model = "model_dtree_regressor_"+file_analysis_train.replace(".csv","")
    
    # SCHEMA MODEL MLFlow   
    _list_input_schema  = model_input
    _list_output_schema = model_output
    _list_input_schema = list ( set(_list_input_schema) - set(_list_output_schema))

    _listColSpec= [ColSpec("double",item) for item in _list_input_schema]
    input_schema = Schema(_listColSpec)
    
    _listColSpec = [ColSpec("double",item) for item in _list_output_schema]
    output_schema = Schema(_listColSpec)
    # SAVE SCHEMA MODEL
    signature = ModelSignature(inputs=input_schema, outputs=output_schema)
    # LOG MODEL ARTIFACTS
    mlflow.sklearn.log_model(sk_model=dtree_model,signature=signature,artifact_path=input_dir_train+"dtree_regressor" )
    
def display_scores(scores):
    return "Scores: {0}\nMean: {1:.3f}\nStd: {2:.3f}".format(scores, np.mean(scores), np.std(scores))

def load_data( path, n_rows, fields=None):
    dataframe = collect.Collections.readCSV(path,n_rows,fields)
    return dataframe

def logs (path,filename,scores,mean,std):
    # import ipdb; ipdb.set_trace()
    print(filename)
    FILENAME =  path + filename
    f = open(FILENAME,"w+")
    
    str_display = display_scores(np.sqrt(scores)) 
    for idx in range(len(scores)):
        f.write("\n scores "+str(idx) + ": " + str(scores[idx]) )

    f.write("\nMean: " +  str(np.mean(scores)))
    f.write("\nStd: "  +  str(np.std(scores)))
    f.write("\nDisplay Scores: " + str_display)
    
    f.close()


if __name__ == '__main__':
    DecisionTree()
