import Collection.collection  as collect
import pandas as pd
import yaml
import ipdb
import os
import json
import numpy as np
import six
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import click

# SKLEARN
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn import svm

# KERAS
from keras.datasets import imdb
from keras.preprocessing import sequence
from keras import layers
from keras.models import Sequential,Model
from keras.layers import Embedding, SimpleRNN,LSTM,Dense,Input, Flatten
from keras.optimizers import RMSprop
from keras.layers.merge import concatenate
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D


# MLFLOW
import mlflow
from mlflow.utils import mlflow_tags
from mlflow.entities import RunStatus
from mlflow.utils.logging_utils import eprint
from mlflow.tracking import MlflowClient, fluent
from mlflow.tracking.fluent import _get_experiment_id_from_env,_get_experiment_id

def _already_ran(entry_point_name, parameters, experiment_id=None):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    
    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    client = mlflow.tracking.MlflowClient()
    all_run_infos = reversed(client.list_run_infos(experiment_id))
    for run_info in all_run_infos:
        full_run = client.get_run(run_info.run_id)
        tags = full_run.data.tags
        if tags.get(mlflow_tags.MLFLOW_PROJECT_ENTRY_POINT, None) != entry_point_name:
            continue
        match_failed = False
        for param_key, param_value in six.iteritems(parameters):
            run_value = full_run.data.params.get(param_key)
            if run_value != param_value:
                match_failed = True
                break
       
        if match_failed:
            continue

        if run_info.to_proto().status != RunStatus.FINISHED:
            eprint(
                ("Run matched, but is not FINISHED, so skipping " "(run_id=%s, status=%s)")
                % (run_info.run_id, run_info.status)
            )
            continue

        return client.get_run(run_info.run_id)
    eprint("No matching run has been found.")
    return None

def _get_or_run(entrypoint, parameters, use_cache=False):
    
    existing_run = _already_ran(entrypoint, parameters)
    
    if use_cache and existing_run:
        print("Found existing run for entrypoint=%s and parameters=%s" % (entrypoint, parameters))
        return existing_run
    print("Launching new run for entrypoint=%s and parameters=%s" % (entrypoint, parameters))
    submitted_run = mlflow.run(".", entrypoint, parameters=parameters)
    return mlflow.tracking.MlflowClient().get_run(submitted_run.run_id)

def workflow():
        
    # Get file YAML 
    m_yaml_file = open("Config/main.yaml")
    main_yaml_file = yaml.load(m_yaml_file, Loader=yaml.FullLoader)
    print(main_yaml_file)
       
    # Create new experiment in the workflow from mlflow
    experiment = mlflow.get_experiment(_get_experiment_id_from_env())
    
    # Algorithms that it will executed. 
    deepl       = main_yaml_file['deepl']
    mlearn      = main_yaml_file['mlearn']
    etl         = main_yaml_file['etl']
    n_rows      = main_yaml_file['n_rows']
    # elements    = main_yaml_file['elements']
    # input_dir   = main_yaml_file['input_dir']
    # output_dir  = main_yaml_file['output_dir']
    
    # # Create folder output_dir
    # if not os.path.exists(str(output_dir)):
    #     os.makedirs(str(output_dir))  

    # Run active run.
    with mlflow.start_run() as active_run:
        name_RunParent = ""


        if deepl:
            name_RunParent += deepl
        if etl:
            name_RunParent += "," + etl
        
        # Set Name Run
        mlflow.set_tag("mlflow.runName", name_RunParent)

        # Development it each one parts: Pre-Processing,machine learning and deep learning
        # Get all algorithms of etl: "Pre-Processing"
        if etl:
            etl = etl.split(",")
        
        for item in etl:
            '''
            Partition Data:
                Algorithm:
                    - Group by data and create new subset data. 
                    - Group by data any fields.
                    - Group by data in several levels. 
            ''' 
            if item=="partition-data":
                a_yaml_file = open("Config/partition-data.yaml")
                parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                print(parsed_yaml_file)
                
                # Parameters get from YAML file [ main, partition-data ]
                parameters = {
                    "n_rows":           n_rows,
                    "date_init":        parsed_yaml_file['date_init'],
                    "date_end":         parsed_yaml_file['date_end'],
                    "fields_include":   parsed_yaml_file['fields_include'],
                    "group_by_parent":  parsed_yaml_file['group_by_parent'],
                    "type_dataset":     parsed_yaml_file['type_dataset'],
                    "output_dir":       parsed_yaml_file['output_dir'],
                    "file_input":       parsed_yaml_file['file_input'],
                }

                partition = _get_or_run("partitionDF",parameters)

            '''
            Analysis DataSet:
                Algorithm that show studie preview of DataSet. 
                
                 - Create summary html:Mean,median,std,q1,q2,q3,Min,Max
                 - Create boxplot: Show distribution data
                 - Create graph line: Graph line each variable from DataSet
            
            ''' 
        
            if item=="analysis":
                # Get File Config YAML
                a_yaml_file = open("Config/analysis.yaml")
                parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                print(parsed_yaml_file)
                
                # Parameters get from YAML file [ main, analysis ]
                parameters = {
                    "n_rows":       n_rows,
                    "fields":       parsed_yaml_file['fields'],
                    "input_dir":    parsed_yaml_file['input_dir'],
                    "output_dir":   parsed_yaml_file['output_dir'],
                }
                
                analysis = _get_or_run("analysis_data",parameters)
            # '''
            # Visualization:
            #     Algorithm divider in two parts:
            #         - First Part.
            #             Show line graphs where you can insert values from some field belonging to DataSet 
            #             in an x-axis and a y-axis. You can to do resample  data, in week,month,years.
            #         -Second Part. 
            #             Show graphs bars,matrix of the missing values DataSet, as well as  relation
            #             between distinct fields DataSet with graphs heatmap and dendograms.
            # ''' 

            # if item=="visualization":
            #     # Get File Config YAML
            #     a_yaml_file = open("Config/visualization.yaml")
            #     parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
            #     print(parsed_yaml_file)
                
            #     # Parameters get from YAML file [ main, visualization ]
            #     parameters = {
            #         "n_rows":       n_rows,
            #         "elements":     elements,
            #         "field_x":      parsed_yaml_file['field_x'],
            #         "field_y":      parsed_yaml_file['field_y'],
            #         "graph":        parsed_yaml_file['graph'],
            #         "_resample":    parsed_yaml_file['_resample'],
            #         "measures":     parsed_yaml_file['measures'],
            #         "input_dir":    parsed_yaml_file['input_dir'],
            #         "timeseries":    parsed_yaml_file['timeseries'],
            #     }
                
            #     visualization = _get_or_run("visualization_data",parameters)
            

            '''
            Missing Values:
                Algorithm:
                    - Algorithms remove missing values DataSet. 
                    - Choose algoritms Missing Values.
            ''' 

            if item=="missing-values":
                a_yaml_file = open("Config/missing-values.yaml")
                parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                print(parsed_yaml_file)
                parameters={
                    # "elements":         elements,
                    "n_rows":           n_rows,
                    "fields_include":   parsed_yaml_file['fields_include'], 
                    "alg_missing":      parsed_yaml_file['alg_missing'],
                    "input_dir":        parsed_yaml_file['input_dir'],
                }
                missing_values = _get_or_run("missing_values", parameters=parameters)

            '''
            Outliers Values:
                Algorithm:
                    - Algorithms remove outliers DataSet. 
                    - Choose algorithms detections Outliers Values.
            ''' 

            if item=="outliers":
                a_yaml_file = open("Config/outliers.yaml")
                parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                print(parsed_yaml_file)
                
                parameters={
                    "n_rows":n_rows,
                    "fields_include":parsed_yaml_file['fields_include'], 
                    "q1":parsed_yaml_file['q1'],
                    "q3":parsed_yaml_file['q3'],
                    "alg_outliers":parsed_yaml_file['alg_outliers'],
                    "input_dir":parsed_yaml_file['input_dir'],
                }
                outliers = _get_or_run("outliers", parameters=parameters)
            
            
            '''
            Feature Selections:
                Algorithm:
                    - Algorithms feature selections DataSet. 
                    - Choose algorithms detections Features Selections.
            ''' 

            if item=="feature-selection":
                a_yaml_file = open("Config/feature-selection.yaml")
                parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                print(parsed_yaml_file)
                parameters = {
                    "n_rows":           n_rows,
                    # "elements":         elements,
                    "fields_include":   parsed_yaml_file['fields_include'], 
                    "alg_fs":           parsed_yaml_file['alg_fs'],
                    "input_dir":        parsed_yaml_file['input_dir'],
                }
                feature_fs = _get_or_run("feature_selection", parameters=parameters)
                
        if mlearn:
            '''
              Algorithms Machine Learning
            '''
            
            mlearn = mlearn.split(",")
            for item in mlearn:
                '''
                    XGBOOST:
                    Algorithms xgboost 
                '''
                if item=="xgb":
                    a_yaml_file = open("Config/xgb.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            print(parsed_yaml_file)
                            parameters = {
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "input_dir_train":      parsed_yaml_file['input_dir_train'],
                                "input_dir_test":       parsed_yaml_file['input_dir_test'],
                                "output_dir":           parsed_yaml_file['output_dir'],
                                "artifact_uri":         active_run.info.artifact_uri,
                                "experiment_id":        active_run.info.experiment_id,
                                "run_id":               active_run.info.run_id,
                                "n_rows":               n_rows,
                                "model_input":          parsed_yaml_file['model_input'], 
                                "model_output":         parsed_yaml_file['model_output'], 
                                "n_splits":             parsed_yaml_file['n_splits'],
                                "objective":            parsed_yaml_file['objective']
                            }
                            xgboost = _get_or_run("xgb", parameters=parameters) 

                '''
                RANDOM FOREST REGRESSOR:
                    Algorithms random forest regressor. 
                '''
                if item=="rf_regressor":
                    a_yaml_file = open("Config/rf_regression.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                    
                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            print(parsed_yaml_file)
                            parameters ={
                                "file_analysis_train":          csv,
                                "file_analysis_test":           csv_test,
                                "artifact_uri":                 active_run.info.artifact_uri,
                                "experiment_id":                active_run.info.experiment_id,
                                "run_id":                       active_run.info.run_id,
                                "n_rows":                       n_rows,
                                "input_dir_train":              parsed_yaml_file['input_dir_train'],
                                "input_dir_test":               parsed_yaml_file['input_dir_test'],
                                "output_dir":                   parsed_yaml_file['output_dir'],
                                "model_input":                  parsed_yaml_file['model_input'], 
                                "model_output":                 parsed_yaml_file['model_output'], 
                                "n_estimators":                 parsed_yaml_file['n_estimators'],
                                "criterion":                    parsed_yaml_file['criterion'],
                                "max_depth":                    parsed_yaml_file['max_depth'],
                                "min_samples_split":            parsed_yaml_file['min_samples_split'],
                                "min_samples_leaf":             parsed_yaml_file['min_samples_leaf'],
                                "min_weight_fraction_leaf":     parsed_yaml_file['min_weight_fraction_leaf'],
                                "max_features":                 parsed_yaml_file['max_features'],
                                "max_leaf_nodes":               parsed_yaml_file['max_leaf_nodes'],
                                "min_impurity_decrease":        parsed_yaml_file['min_impurity_decrease'],
                                "bootstrap":                    parsed_yaml_file['bootstrap'],
                                "oob_score":                    parsed_yaml_file['oob_score'],
                                "n_jobs":                       parsed_yaml_file['n_jobs'],
                                "random_state":                 parsed_yaml_file['random_state'], 
                                "warm_start":                   parsed_yaml_file['warm_start'],
                                "ccp_alpha":                    parsed_yaml_file['ccp_alpha'],
                                "max_samples":                  parsed_yaml_file['max_samples'],
                                "figure":                       parsed_yaml_file['figure'],
                                "verbose":                      parsed_yaml_file['verbose'],
                                "n_splits":                    parsed_yaml_file['n_splits'],
                            }
                            rf_regressor = _get_or_run("rf_regressor", parameters=parameters) 
                '''
                DTREE REGRESSOR:
                    Algorithms DTREE regressor. 
                '''
                if item=="dtree_regressor":
                    a_yaml_file = open("Config/dtree_regression.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                    
                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            # import ipdb; ipdb.set_trace()
                            parameters ={
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "artifact_uri":              active_run.info.artifact_uri,
                                "experiment_id":             active_run.info.experiment_id,
                                "run_id":                    active_run.info.run_id,
                                "n_rows":                    n_rows,
                                "n_splits":                  parsed_yaml_file['n_splits'],
                                "input_dir_train":           parsed_yaml_file['input_dir_train'],
                                "input_dir_test":            parsed_yaml_file['input_dir_test'],
                                "output_dir":                parsed_yaml_file['output_dir'],
                                "model_input":               parsed_yaml_file['model_input'], 
                                "model_output":              parsed_yaml_file['model_output'],  
                                "max_depth":                 parsed_yaml_file['max_depth'],
                                "criterion":                 parsed_yaml_file['criterion'],
                                "splitter":                  parsed_yaml_file['splitter'],
                                "min_samples_split":         parsed_yaml_file['min_samples_split'],
                                "min_samples_leaf":          parsed_yaml_file['min_samples_leaf'],
                                "min_weight_fraction_leaf":  parsed_yaml_file['min_weight_fraction_leaf'],
                                "max_features":              parsed_yaml_file['max_features'],
                                "max_leaf_nodes":            parsed_yaml_file['max_leaf_nodes'],
                                "random_state":              parsed_yaml_file['random_state'], 
                                "figure":                    parsed_yaml_file['figure'],
                            }
                            dtree_regressor = _get_or_run("dtree_regressor", parameters=parameters) 
            
                        
        if deepl:
            # import ipdb; ipdb.set_trace();
            # import ipdb; ipdb.set_trace();
            deepl = deepl.split(",")
            for item in deepl:
                '''
                CNN:
                    Algorithms CNN. 
                '''
                if item=="cnn":
                    a_yaml_file = open("Config/cnn.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)

                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]

                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            parameters = {
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "artifact_uri":         active_run.info.artifact_uri,
                                "experiment_id":        active_run.info.experiment_id,
                                "run_id":               active_run.info.run_id,
                                "n_rows":               n_rows,
                                "input_dir_train":      parsed_yaml_file['input_dir_train'],
                                "input_dir_test":       parsed_yaml_file['input_dir_test'],
                                "output_dir":           parsed_yaml_file['output_dir'],
                                "model_input":          parsed_yaml_file['model_input'], 
                                "model_output":         parsed_yaml_file['model_output'], 
                                "n_steps":              parsed_yaml_file['n_steps'],
                                "n_features":           parsed_yaml_file['n_features'],
                                "conv_filters":         parsed_yaml_file['conv_filters'],
                                "conv_kernel_size":     parsed_yaml_file['conv_kernel_size'],
                                "pool_size":            parsed_yaml_file['pool_size'],
                                "hidden_units":         parsed_yaml_file['hidden_units'],
                                "epochs":               parsed_yaml_file['epochs'],
                                "batch_size":           parsed_yaml_file['batch_size'],
                                "verbose":              parsed_yaml_file['verbose'],
                            } 
                            
                            cnn = _get_or_run("cnn", parameters=parameters)  
                '''
                LSTM:
                    Algorithms LSTM. 
                '''
                if item=="lstm":
                    a_yaml_file = open("Config/lstm.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                    print(parsed_yaml_file)

                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            parameters = {
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "artifact_uri":     active_run.info.artifact_uri,
                                "experiment_id":    active_run.info.experiment_id,
                                "run_id":           active_run.info.run_id,
                                "n_rows":           n_rows,
                                "input_dir_train":  parsed_yaml_file['input_dir_train'],
                                "input_dir_test":   parsed_yaml_file['input_dir_test'],
                                "output_dir":       parsed_yaml_file['output_dir'],
                                "model_input":      parsed_yaml_file['model_input'], 
                                "model_output":     parsed_yaml_file['model_output'], 
                                "n_steps":          parsed_yaml_file['n_steps'],
                                "hidden_units":     parsed_yaml_file['hidden_units'],
                                "epochs":           parsed_yaml_file['epochs'],
                                "batch_size":       parsed_yaml_file['batch_size'],
                                "verbose":          parsed_yaml_file['verbose'],
                            } 
                            
                            lstm = _get_or_run("lstm", parameters=parameters)  
                '''
                MLP:
                    Algorithms MLP. 
                '''
                if item=="mlp":
                    
                    a_yaml_file = open("Config/mlp.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                    print(parsed_yaml_file)
                    
                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                    
                            parameters = {
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "artifact_uri":     active_run.info.artifact_uri,
                                "experiment_id":    active_run.info.experiment_id,
                                "run_id":           active_run.info.run_id,
                                "n_rows":           n_rows,
                                "input_dir_train":  parsed_yaml_file['input_dir_train'],
                                "input_dir_test":   parsed_yaml_file['input_dir_test'],
                                "output_dir":       parsed_yaml_file['output_dir'],
                                "model_input":      parsed_yaml_file['model_input'], 
                                "model_output":     parsed_yaml_file['model_output'], 
                                "n_steps":          parsed_yaml_file['n_steps'],
                                "hidden_units":     parsed_yaml_file['hidden_units'],
                                "epochs":           parsed_yaml_file['epochs'],
                                "batch_size":       parsed_yaml_file['batch_size'],
                                "verbose":          parsed_yaml_file['verbose'],
                            } 
                    
                            mlp = _get_or_run("mlp", parameters=parameters)  
                '''
                MLP_HEADED:
                    Algorithms MLP_HEADED. 
                '''
                if item=="mlp_headed":
                    a_yaml_file = open("Config/mlp_headed.yaml")
                    parsed_yaml_file = yaml.load(a_yaml_file, Loader=yaml.FullLoader)
                    print(parsed_yaml_file)
                    
                    list_file_train = os.listdir(parsed_yaml_file['input_dir_train'])
                    list_file_test  = os.listdir(parsed_yaml_file['input_dir_test'])
                
                    list_file_train =  [ l for l in list_file_train if l.endswith(".csv") ]
                    list_file_test  =  [ l for l in list_file_test  if l.endswith(".csv") ]
                    
                    for csv in list_file_train:
                        file_analysis_test = csv.replace("train_","test_")
                        csv_test = file_analysis_test
                        if file_analysis_test in list_file_test:
                            parameters = {
                                "file_analysis_train":  csv,
                                "file_analysis_test":   csv_test,
                                "artifact_uri":     active_run.info.artifact_uri,
                                "experiment_id":    active_run.info.experiment_id,
                                "run_id":           active_run.info.run_id,
                                "n_rows":           n_rows,
                                "input_dir_train":  parsed_yaml_file['input_dir_train'],
                                "input_dir_test":   parsed_yaml_file['input_dir_test'],
                                "output_dir":       parsed_yaml_file['output_dir'],
                                "model_input":      parsed_yaml_file['model_input'], 
                                "model_output":     parsed_yaml_file['model_output'], 
                                "n_steps":          parsed_yaml_file['n_steps'],
                                "hidden_units":     parsed_yaml_file['hidden_units'],
                                "epochs":           parsed_yaml_file['epochs'],
                                "batch_size":       parsed_yaml_file['batch_size'],
                                "verbose":          parsed_yaml_file['verbose'],
                            } 
                            mlp_headed = _get_or_run("mlp_headed", parameters=parameters)  
                        
                    
        # if output_dir!=None:
        #     mlflow.log_artifacts(output_dir)
        mlflow.end_run()

    
if __name__ == '__main__':
    workflow()
    

