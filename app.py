from flask import Flask
from flask_jwt_extended import JWTManager
from flask_smorest import Api
from flask_migrate import Migrate

import os
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST

def create_app():
    # Create the flask app
    app = Flask(__name__)

    # Load all of the variables from .env
    load_dotenv()

    # Setup the configs
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"

    # Responsible for the documentation website
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/docs"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

    # Setup what database we are going to use.
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")


    # Connect our flask_sqlalchemy to flask
    db.init_app(app)
    migrate = Migrate(app, db)

    # Register the blueprints to API Documentation
    api = Api(app) 



    # SETUP A SECRET KEY FOR JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

    # Create a JWT Manager Object
    jwt = JWTManager(app)


    return app
