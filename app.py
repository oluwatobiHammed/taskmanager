import os
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi

# Load environment variables from .env file
load_dotenv()

if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.secret_key = os.environ.get("SECRET_KEY")

# Initialize PyMongo
mongo = None

try:
    client = MongoClient(os.environ.get("MONGO_URI"), tlsCAFile=certifi.where())
    mongo = client[os.environ.get("MONGO_DBNAME")]
    print("MongoDB connected successfully")

except (ConnectionError, ConfigurationError) as e:
    print(f"Error connecting to MongoDB: {e}")

@app.route("/test_connection")
def test_connection():
    if mongo is None or mongo.db is None:
        return "MongoDB connection is not established", 500
    return "MongoDB connection is successful"

@app.route("/")
@app.route("/get_tasks")
def get_tasks():
#    if mongo is None or mongo.db is None:
#         flash("MongoDB connection is not established")
#         return redirect(url_for("test_connection"))

   try:
        tasks = list(mongo.tasks.find())
        return render_template("tasks.html", tasks=tasks)
   except Exception as e:
        print(f"Error fetching tasks: {e}")
        flash("An error occurred while fetching tasks.")
        return redirect(url_for("test_connection"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)