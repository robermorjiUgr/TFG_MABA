from urllib import request
from flask import jsonify
from flask import Blueprint
from flask_restx import Api, Resource
# from app import api
from app.lib.machinelearning.unsupervised import clustering as clustering

import pandas as pd

import json

import numpy as np

sotsia_bp = Blueprint('sotsia', __name__)

api = Api( sotsia_bp )
ns_sotsia = api.namespace('sotsia', "Proyect api dashboard SOTSIA:")


@ns_sotsia.route('/hello',endpoint="hello")
@ns_sotsia.doc(description="Hello service")
class helloworld(Resource):
    ''''
    To do: 
      hello world del servicio
    '''
    
    def get(self):
        return jsonify({'hello':'world'})


