from flask import Flask
from .dataset       import dataset_bp

def create_app(settings_module='config.dev'):
    app = Flask (__name__)
    app.config.from_object(settings_module)
   
    # a simple page that says hello
    app.register_blueprint(dataset_bp, url_prefix='/dataset')
  

    return app

   