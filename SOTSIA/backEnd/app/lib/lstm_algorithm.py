from tabnanny import verbose
from unittest import TestLoader
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import datasets
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
import io

# arg 'data' is a DataFrame with the dataset created by the scientist
def lstm(data):
    # Id_Sensor 9093 --> Heating
    data_sensor = data.loc[data['ID_Sensor']==9093]
    # We choose the column of 'value' because is the one that has the information that will be used in the LSTM algorithm
    #   - In order to prevent future errors, all databases used must have this 'value' column
    #   - The loc method convert the DataFrame into a Series object
    data_sensor = data_sensor.sort_values(by='timestamp')
    training_set = data_sensor.loc[:, 'value']
    time = data_sensor.loc[:, 'timestamp']
    # # We need a DataFrame to use the fit transform of the MinMaxScaler
    training_set = training_set.to_frame()
    time = time.to_frame()
    # print(type(training_set))
    # Scaling the data with a range [0,1] and fit the training_set
    sc = MinMaxScaler(feature_range = (0, 1))
    X = sc.fit_transform(training_set)
    y = sc.fit_transform(time)

    # Create two training/validation sets 'X' and 'y' and load the data
    X_train, X_validation = np.split(X, [ int( 0.9*len(X) ) ])
    y_train, y_validation = np.split(y, [ int( 0.9*len(X) ) ])

    # Test set is the whole dataset
    X_test = X
    y_test = y

    # LSTM algorithm
    regressor = Sequential()
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.25))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(0.30))
    regressor.add(LSTM(units = 50))
    regressor.add(Dropout(0.35))
    regressor.add(Dense(units = 1))
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

    # Fitting the algorithm so it can learn with the training and validation datasets
    regressor.fit(X_train, y_train, epochs = 1, validation_data=(X_validation, y_validation), batch_size = 32)

    # Prediction
    predicted_values = regressor.predict(X_test, verbose=0)

    # Reverse of the data so it's no longer between [0-1]
    predicted_values = sc.inverse_transform(predicted_values)
    X_test = sc.inverse_transform(X_test)
    y_test = sc.inverse_transform(y_test)
    print(type(X_test))
    # Plot the result
    #plt.xticks(rotation='vertical')
    # Plot the real values of the dataset
    plt.plot(y_test, X_test, color = 'black', label = 'Real Values')
    # Plot our prediction
    plt.plot(y_test, predicted_values, color = 'green', label = 'Predicted Values')
    plt.title('ICPE Prediction using LSTM')
    plt.xlabel('Time')
    plt.ylabel('Values')
    plt.legend()
    plt.show()
    bytes_image = io.BytesIO()
    plt.savefig(bytes_image, format="png")
    bytes_image.seek(0)

    return bytes_image

# Pasos a seguir para LSTM
#   1. Cargar el dataset
#   2. Hacer un MinMaxScaler para escalar los datos (valores entre 0 y 1) y producir resultados optimizados
#   3. Crear un training set y normalizar los datos con fit_transform
#   4. Dividir los datos y prepararlos antes de entrenarlos
#   5. Entrenar, validar y testear
#   6. Ejecutar LSTM --> 
#       modelo = Sequential()
#       modelo.add(LSTM)
#       modelo.add(Dropout(0.25))
#           - En cada iteración hay que ir subiendo el dropout para reducir el overfitting (obliga a las neuronas cercanas a no depender tanto de las neuronas desactivadas)
#       modelo.add(Dense(units = 1))
#       modelo.compile(loss = 'mean_squared_error', optimizer='Adam'))
#       modelo.fit(X_train, y_train, epochs = 100, batch_size = 32)
#       modelo.predict(X_test)
#   7. Sacamos gráfica del resultado

