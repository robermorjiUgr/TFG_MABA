# TSxtend
## Introduction


TSxtend is a tool that will help to perform time series experimentation. The time series experimentation can be recorded with the help of the mlflow library.

It has three modules:

- ETL: It groups data [visualization algorithms](visualization.py), data splitting, to obtain different groupings and store them in csv format [partition-data](partition-data.py), as well as, algorithms to perform data mining, such as outliers elimination, [missing values](missing-values.py) and [features selections](feature_selection.py).

- MLearn: It includes algorithms that use Machine Learning techniques, such as [XGBoost](xgb.py), [Random Forest](rf_regressor.py) and [DTREE](dtre_regressor.py).

- DeepL: It includes algorithms that use Deep Learning techniques, such as [CNN](cnn.py), [LSTM](lstm.py), [MLP](mlp.py), [MLP HEADED](mlp_headed.py). 

All this is done through the execution of a simple command line. For this, it is necessary to configure a series of files, depending on the techniques to be used in our experimentation. This will do all the necessary calculations and store the results helping us to get results quickly and efficiently. 

The modules that include this tool are the next:

- ETL
    
    - [PARTITION DATA.](docs/partition-data.md)
    - [VISUALIZATION.](docs/visualization.md)
    - [MISSING VALUES.](docs/missing-values.md)
    - [FEATURES SELECTIONS.](docs/feature-selection.md)

- MLearn

  - [XGBOOST.](docs/xgb.md)
  - [RANDOM FOREST REGRESSION.](docs/rf_regression.md)
  - [DTREE REGRESSION.](docs/dtree_regression.md)

- DeepL

    - [CONVULATIONAL NETWORKS.](docs/cnn.md) 
    - [LSTM.](docs/lstm.md) 
    - [MLP.](docs/mlp.md) 
    - [MLP HEADED.](docs/mlp_headed.md) 

Main file config is [main.yaml](Config/main.yaml). In this file we can select the algorithms implemented etl, mlearn, deepl in our tool for our experiments. 

We can configure:

- etl: Algorithms list implemented etl. 
- mlearn: Algorithms list implemented machine learning. 
- deepl: Algorithms list implemented Deep Learning. 
- n_rows: Number files show from selected DataSet.
- element: Selection elements analice. [TO-DO]
- input_dir: Input Directory.
- output dir: Output Directory.

Link Code: [ main.py ](main.py)


## Installation



#### VirtualEnv

`pip3 install virtualenv`

`virtualenv -p [path] venv`

#### MLFLOW
~~~
pip3 install mlflow
~~~

#### MLFLOW UI

~~~
mlflow ui
~~~
#### PROJECT RUN
 `mlflow run . --experiment-name=[name_experiment]`

#### CONDA 
[link installation anaconda ](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html#installing-conda-on-a-system-that-has-other-python-installations-or-packages)
