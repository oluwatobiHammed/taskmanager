import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from dotenv import load_dotenv
import certifi
if os.path.exists("env.py"):
    import env  # noqa


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
# Initialize PyMongo
mongo = None
if os.environ.get("DEVELOPMENT") == "True":
     
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
        
    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    print(f"MongoDB URI: {os.environ.get('MONGO_URI')}")

    try:
        client = MongoClient(os.environ.get("MONGO_URI"), tlsCAFile=certifi.where())
        mongo = client[os.environ.get("MONGO_DBNAME")]
        print("MongoDB connected successfully")

    except (ConnectionError, ConfigurationError) as e:
        print(f"Error connecting to MongoDB: {e}")
else:
    uri = os.environ.get("DATABASE_URL")

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        print(f"url: {uri}")
        app.config["SQLALCHEMY_DATABASE_URI"] = uri
        
db = SQLAlchemy(app)

from taskmanager import routes  # noqa