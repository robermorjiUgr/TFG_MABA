
#PYTHON
import click
import mlflow
import os
import yaml

#DATASCIENCE
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
from matplotlib import pyplot as plt
#OWNER
import Collection.collection  as collect

#SCIPY
from scipy import stats
from impyute.imputation.cs import fast_knn, mice



  
@click.command(help="Dado un fichero CSV, transformar en un artefacto mlflow")
@click.option("--n_rows", type=float, default=0, help="número de filas a extraer, 0 extrae todo")
@click.option("--fields_include", type=str, default=None, help="Incluir los siguientes campos")
@click.option("--input_dir", type=str,default="input_dir/")
@click.option("--alg_outliers", type=str, default="z_score_method_mean", help="algoritmo eliminar outliers")
@click.option("--q1", type=float, default=0.25, help=" % eliminar outliers")
@click.option("--q3", type=float, default=0.75, help=" % eliminar outliers")


def outliers(input_dir,n_rows,q1,q3,fields_include,alg_outliers):
    mlflow.set_tag("mlflow.runName", "Data Outliers")
    
    if not os.path.exists(input_dir+ "/outliers-values"):
        os.makedirs(input_dir+ "/outliers-values")


    # List Analysis File CSV 
    list_file = os.listdir(input_dir)
    list_file = [ l for l in list_file if l.endswith(".csv")]
    fields_include = fields_include.split(",")
    
    for csv in list_file:
        print("Outliers Values: " + str(csv))
        path = input_dir + "/" + csv
        df_origin = load_data(path,n_rows)
        

        if fields_include!=None:      
            df_outliers = load_data(path,n_rows,fields_include)
        else:
            df_outliers = df_origin

        if alg_outliers == 'visualization':
            ### CREATE BOXPLOT
            # import ipdb; ipdb.set_trace()
            print("Create boxplot")
            name_file = csv.replace(".csv","")
            fields_boxplot = [ fields for fields in fields_include]
            data   = df_outliers[fields_boxplot].values
            labels = df_outliers[fields_boxplot].columns.tolist()
            
            fig1, ax1 = plt.subplots(figsize=(15,15))
            ax1.set_title(name_file)
            ax1.set_xlabel('Fields DataSet')
            ax1.set_ylabel('Cantidad')
            ax1.boxplot(data,labels=labels)       

            plt.savefig(input_dir+ "/outliers/boxplot_"+name_file+".jpeg", bbox_inches='tight')
            plt.close('all')

        else:
            print("Execute and create boxplot outliers: z-score-method-mean ")
            name_file = csv.replace(".csv","")
            if alg_outliers == 'z_score_method_mean':
                df_final = z_score_method_mean(df_outliers,q1,q3,fields_include,input_dir,name_file)
            # Update columns remove outliers in the Origin DataSet
            df_origin.update(df_final)
            df_origin.to_csv(path,encoding='utf-8')
       
    mlflow.log_artifacts(input_dir+ "/outliers/")
    

def load_data(path_df, n_rows, fields=[]):
    dataframe = collect.Collections.readCSV(path_df,n_rows,fields)
    return dataframe


def create_dir( path_dir):
    collect.Collections.createDir(path_dir)
    

def create_csv(dataframe, path_csv, name_csv):
    collect.Collections.createCSV(dataframe,path_csv,name_csv)


def z_score_method_mean(df,q1,q3,fields_include,input_dir,name_file):
    # Get only columns necessary    
    df.index.name = 'index'
    processing_include = df.filter(fields_include,axis=1)

    # Draw DataFrame before algorithm outliers
    df.boxplot()
    plt.savefig(input_dir+"/outliers-values/"+name_file+"_before_outliers.jpeg")

    q1 = processing_include.quantile(q1)
    q3 = processing_include.quantile(q3)
    IQR = q3 - q1

    filtered = (processing_include < (q1 - 1.5 * IQR)) |(processing_include > (q3 + 1.5 * IQR))
    
    for name in list(processing_include.columns):
        row_index = processing_include[ filtered[name]==True ][name].index
        for row in row_index:
            processing_include.loc[row, name] = processing_include[name].mean()
    df.update(processing_include)
    # Draw DataFrame after algorithm outliers
    plt.cla() # clean plt
    df.boxplot()
    plt.savefig(input_dir+"/outliers-values/"+name_file+"_after_outliers.jpeg")
    
    return df



if __name__=="__main__":
    outliers()