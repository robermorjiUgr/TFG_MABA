from flask import Flask
from flask_restx import Api, Resource,fields
from .sotsia.service       import sotsia_bp,ns_sotsia


app = Flask (__name__)


# Creación del objeto api
api = Api(app,version="1.0",title="ApiRest SOTSIA", description="API Rest TFG SOTSIA",contact="" )

# Añadir objeto namespace 
api.add_namespace(ns_sotsia)

# Añadir endpoint service
app.register_blueprint(sotsia_bp)



if __name__ == "__main__":
      app.run()

   