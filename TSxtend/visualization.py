
#PYTHON
from datetime import datetime
import ipdb
import click
import yaml
import mlflow
import os
import matplotlib.pyplot as plt
import missingno as msno

#DATASCIENCE
import pandas as pd
import numpy as np

#OWNER
import Collection.collection  as collect


  


@click.command(
    help="Dado un fichero CSV, transformarlo  mlflow"
)
@click.option("--n_rows",default=None, type=float)
@click.option("--field_x",default=None, type=str)
@click.option("--field_y",default=None, type=str)
@click.option("--graph",default=None, type=str)
@click.option("--measures",default=None, type=str)
@click.option("--_resample",default=None, type=str) # W,M,Q,A
@click.option("--input_dir",default=None, type=str)
@click.option("--elements",default=None, type=str)
@click.option("--timeseries",default=True, type=bool)

def Visualization(n_rows,field_x, field_y, graph, measures, _resample, input_dir,elements,timeseries):
    
    mlflow.set_tag("mlflow.runName", "Data Visualization")
       
    if not os.path.exists(input_dir+ "/visualization"):
        os.makedirs(input_dir+ "/visualization/line")  
        os.makedirs(input_dir+ "/visualization/matrix")  
        os.makedirs(input_dir+ "/visualization/bar")  
        os.makedirs(input_dir+ "/visualization/dendograma")  
        os.makedirs(input_dir+ "/visualization/heatmap")  

    list_file = os.listdir(input_dir)
    list_file = [ l for l in list_file if l.endswith(".csv")]
    if elements!=None:
        elements = [ elem for elem in elements.split(",") ]
        list_file = [ l for l in list_file for elem in elements if l.find(elem)!=-1 ]


    # import ipdb; ipdb.set_trace()
    for csv in list_file:
        print("Visualization Data: " + str(csv))
        
        path = input_dir       
        path += "/"+csv
        #import ipdb; ipdb.set_trace()
        df_origin = load_data(path,n_rows)
        
            
        df_origin.sort_index(inplace=True)       
        l_measure = [ m for m in measures.split(",") ]
        df =  df_origin [l_measure]
        
        # plt.rcParams['figure.figsize'] = (50, 50) # change plot size
        # plt.rcParams["legend.loc"] = 'best'
        # plt.title(csv.replace(".csv",''))
        
        df = df.fillna(0)
        if timeseries:
            # Group by for timestamp
            df = df.groupby([field_x]).mean()
            df.index = pd.to_datetime(df.index)
            
            if measures!='None':
                df[l_measure].resample(_resample).mean()
            else:
                df.resample(_resample).mean()
       
        
        if graph=="line":
            # df.fillna(0,inplace=True)
                      
            # df.set_index(field_x,drop=True,inplace=True)
            # if timeseries:
            #     # Group by for timestamp
            #     df = df.groupby([field_x]).mean()
            #     df.index = pd.to_datetime(df.index)
                
            #     if measures!='None':
            #         df[l_measure].resample(_resample).mean().plot(grid=True)
            #     else:
            #         df.resample(_resample).mean().plot(grid=True)
            # else:
            data1  = df.index.values
            data2  = df.values
            labels = df.columns.values
            labels = labels.tolist()
            fig, ax = plt.subplots()  # Create a figure and an axes.
            plt.plot(data1,data2)                       
            ax.set_xlabel('Step')  # Add an x-label to the axes.
            ax.set_ylabel('values')  # Add a y-label to the axes.
            ax.set_title(csv.replace(".csv",""))  # Add a title to the axes.
            ax.legend(labels)  # Add a legend.
            
            plt.savefig(input_dir+ "/visualization/line/"+csv.replace(".csv",'')+".png")
        
        if graph=="missing":
                     
            if measures!='None':

                msno.matrix(df[l_measure])                
                plt.savefig(input_dir+ "/visualization/matrix/"+csv.replace(".csv",'')+".png")
                
                msno.bar(df[l_measure])               
                plt.savefig(input_dir+ "/visualization/bar/"+csv.replace(".csv",'')+".png")

                msno.dendrogram(df[l_measure])               
                plt.savefig(input_dir+ "/visualization/dendograma/"+csv.replace(".csv",'')+".png")

                msno.heatmap(df[l_measure])              
                plt.savefig(input_dir+ "/visualization/heatmap/"+csv.replace(".csv",'')+".png")
            else:
                msno.matrix(df)
                plt.savefig(input_dir+ "/visualization/matrix/"+csv.replace(".csv",'')+".png")

                msno.bar(df)
                plt.savefig(input_dir+ "/visualization/bar/"+csv.replace(".csv",'')+".png")
                
                msno.dendrogram(df)
                plt.savefig(input_dir+ "/visualization/dendograma/"+csv.replace(".csv",'')+".png")

                msno.heatmap(df)
                plt.savefig(input_dir+ "/visualization/heatmap/"+csv.replace(".csv",'')+".png")
       
        plt.close('all')

    mlflow.log_artifacts(input_dir+ "/visualization")
    
def load_data( path, n_rows, fields=None):
       
    dataframe = collect.Collections.readCSV(path,n_rows,fields)
    return dataframe


def create_dir( path):
    collect.Collections.createDir(path)
    

def create_csv( dataframe, path, name):
    collect.Collections.createCSV(dataframe,path,name)

if __name__=="__main__":
    Visualization()
