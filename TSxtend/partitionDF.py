
#PYTHON
from datetime import datetime
import ipdb
import click
import yaml
import mlflow
import os

#DATASCIENCE
import pandas as pd
import numpy as np

#OWNER
import Collection.collection  as collect




@click.command(
    help="Give you CSV file and algorithm group by"
)
@click.option("--date_init", type=str, default="", help="Fecha inicio que ayuda a discriminar por estaciones")
@click.option("--date_end",type=str, default="", help="Fecha final que ayuda a discriminar por estaciones")
@click.option("--n_rows", type=float, default=0, help="número de filas a extraer, 0 extrae todo")
@click.option("--fields_include", type=str, default=None, help="Incluir los siguientes campos")
@click.option("--group_by_parent", type=str, help="filtrar por un campo de las columnas")
@click.option("--type_dataset", type=str,default="")
@click.option("--output_dir", type=str,default="output/")
@click.option("--file_input", type=str, default="", help="Ruta del fichero CSV")

def PartitionDF(date_init, date_end, file_input, n_rows, 
fields_include,group_by_parent, output_dir,type_dataset):
    
    mlflow.set_tag("mlflow.runName", "Data Partition")
    # Create folder output_dir
    
    if not os.path.exists(str(output_dir)):
        os.makedirs(str(output_dir))  

    if date_init != 'None' or date_end != 'None':
        date_init = pd.to_datetime(date_init,format="%Y-%m-%d %H:%M:%S")
        date_end  = pd.to_datetime(date_end,format="%Y-%m-%d %H:%M:%S")
    
    
    
    if fields_include!='None':
        fields_include = fields_include.split(",")
        df_origin = load_data(file_input, int(n_rows), fields_include)
    else:
        df_origin = load_data(file_input, int(n_rows))
        
    # GET DataSet filter for timestamp
    if date_init != 'None' or date_end != 'None':
        df_origin['timestamp'] = pd.to_datetime(df_origin['timestamp'],format="%Y-%m-%d %H:%M:%S")
        mask = ( df_origin['timestamp'] >= date_init ) & ( df_origin['timestamp'] <= date_end )
        df_origin = df_origin.loc[mask]
        df_origin.set_index('timestamp',drop=True,inplace=True)

    # Tree where group by for every element.
    list_groups = []
    if group_by_parent != 'None':
        # Option  if  you want to do some group by
        
        group_by_parent = group_by_parent.split(",")  
        
        for group in group_by_parent:
            list_groups.append(df_origin[group].unique().tolist())
        
        # Tree create csv for groups
        query       =  []
        _query      =  []   # Tuples query store
        _l_tupla    =  []    
        arbol       =  {}    # Group by field
        
        # Recursivity: create tree field
        for ind in range(0,len(list_groups[0])):
            query.append(createQuery(0,len(list_groups)-1,list_groups,arbol, list_groups[0][ind]))
              
        # Create queries
        for item in query:
            _query.append( _format_str_query(item,group_by_parent))
       
        # CREATE DataFrame csv and html for mlflow
        for q_parent in _query:
            for q_child in q_parent:           
                df_final = df_origin.query(q_child)
                list_name_csv = _format_name_csv(q_child)
                
                if type_dataset=="train":
                    name_csv = "train"
                else:
                    name_csv = "test"
                # Create and rename CSV: Two options train and test
                for element in list_name_csv:
                    name_csv += "_"+element[0]+"_"+element[1].replace('/',"").replace("'","")
                name_csv+=".csv"            
                
                # Only create dataframe if it has some data.
                if not df_final.empty:
                    print("Creation trainning partitions: " + name_csv)
                    create_csv(df_final, output_dir, name_csv,index=True)
                else:
                    print("Not creation trainning partitions: " + name_csv + " DataFrame have not values")
    else:
        # Option  if  you don't want to do anything group by
        if type_dataset=="train":
            name_csv = "train.csv"
        else:
            name_csv = "test.csv"

        print("Creation trainning partitions: " + name_csv)
        create_csv(df_origin, output_dir, name_csv,index=True)
       

    # MLFLOW artifact   
    mlflow.log_artifacts(output_dir)
    


# Class tree. 
class Arbol:
    def __init__(self, elemento):
        self.hijos = []
        self.elemento = elemento

def agregarElemento(arbol, elemento, elementoPadre):
    subarbol = buscarSubarbol(arbol, elementoPadre);
    subarbol.hijos.append(Arbol(elemento))

def buscarSubarbol(arbol, elemento):
    if arbol.elemento == elemento:
        return arbol
    for subarbol in arbol.hijos:
        arbolBuscado = buscarSubarbol(subarbol, elemento)
        if (arbolBuscado != None):
            return arbolBuscado
    return None   

def createQuery(level,last_level,lista_groups, arbol, elementoPadre):
    _l_tupla=[]
    
    # For one fields
    if level == 0 and level!=last_level:
        query=[]  
        arbol = Arbol(elementoPadre)
        _l_tupla=createQuery(level+1,last_level,lista_groups,arbol, elementoPadre)
        
        for item_tupla  in _l_tupla:
            tupla   = []
            t_query = []
            
            for t in item_tupla:
                if isinstance(t,list):
                    tupla   = []
                    tupla.append(elementoPadre)
                    for item in t:
                        tupla.append(item)
                    t_query.append(tupla)
                else:                  
                    tupla.append(t)
            if not t_query:          
                query.append(tupla)
            else:
                query.append(t_query)
        return query

    # For child levels
    elif level != last_level:
        for elem in lista_groups[level]:
            agregarElemento( arbol,elem,elementoPadre )
            _l_tupla.append(createQuery(level+1,last_level, lista_groups,arbol, elem))
        return _l_tupla
    
    # For last level
    else:
        lista_tupla = []
        # if level is first  and last
        if level == 0:
            arbol = Arbol(elementoPadre)
            tupla = elementoPadre
            lista_tupla.append(tupla)
        else:
            for elem in lista_groups[level]:
                agregarElemento( arbol,elem,elementoPadre )
                tupla = [ elementoPadre,elem ]
                lista_tupla.append(tupla)
        
        return lista_tupla

def _format_name_csv(elementos):
    lista_elementos = elementos.split("&")
    elementos = [ elem.replace("==","|").replace(" ","") for elem in lista_elementos ] 
    return  [ elem.split("|") for elem in elementos ]



def _format_str_query(query,group_by_parent):
    _query_format = [] 
    
    for qs in query:
        # For multiLevels
        if isinstance (qs,list):
            for qu in qs:               
                if not isinstance(qu,list):
                    _format_query = ""
                    c = 0
                    if len(group_by_parent)>1:
                        
                        for  group in group_by_parent:
                            if group != group_by_parent[-1]:
                                _format_query += group+"=='"+str(qs[c])+"' & "
                            else:
                                _format_query += group+"=='"+str(qs[c])+"'"
                            c+=1
                    else:
                        for group in group_by_parent:
                            _format_query += group+"=='"+str(qu)+"'"
                    _query_format.append(_format_query)
                    break
                else:
                    _format_query = ""
                    c = 0
                    if len(group_by_parent)>1:
                        
                        for  group in group_by_parent:
                            if group != group_by_parent[-1]:
                                _format_query += group+"=='"+str(qu[c])+"' & "
                            else:
                                _format_query += group+"=='"+str(qu[c])+"'"
                            c+=1
                    else:
                        
                        for group in group_by_parent:
                            _format_query += group+"=='"+str(qs)+"'"
                    _query_format.append(_format_query)
        else:
            # For one levels
            _format_query = ""
            for group in group_by_parent:
                _format_query += group+"=='"+str(qs)+"'"
            _query_format.append(_format_query)

    return _query_format


def load_data( path, n_rows, fields=None):       
    dataframe = collect.Collections.readCSV(path,n_rows,fields)
    return dataframe


def create_dir( path):
    collect.Collections.createDir(path)
    

def create_csv( dataframe, path, name,index=True):
    collect.Collections.createCSV(dataframe,path,name,index)

if __name__=="__main__":
    PartitionDF()

