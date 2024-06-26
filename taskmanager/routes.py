from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
from taskmanager import app, db, mongo
from taskmanager.models import Category, Task
import os


@app.route("/")
@app.route("/get_tasks")
def get_tasks():

    tasks =  list(Task.query.order_by(Task.id).all())  if os.environ.get("IS_SQL_DB") == "True" else list(mongo.tasks.find())

    return render_template("tasks.html", tasks=tasks)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    tasks = list(mongo.tasks.find({"$text": {"$search": query}}))
    return render_template("tasks.html", tasks=tasks)



@app.route("/get_categories")
def get_categories():
    
    if os.environ.get("IS_SQL_DB") == "True":
       categories = list(Category.query.order_by(Category.category_name).all()) 
    else:
       categories = list(mongo.categories.find().sort("category_name", 1))
    
    return render_template("categories.html", categories=categories)

@app.route("/add_category", methods=["GET", "POST"])
def add_category():
 if request.method == 'POST':
    category_name = request.form.get('category_name')
    if os.environ.get("IS_SQL_DB") == "True":
        existing_category = Category.query.filter_by(category_name=category_name).first()
    else:
        existing_category = mongo.categories.find_one({"category_name": category_name})
        
    if existing_category:
        flash(f'Category {category_name} already exists.', 'warning')
    else:
        if os.environ.get("IS_SQL_DB") == "True":
            new_category = Category(category_name=category_name)
            db.session.add(new_category)
            db.session.commit()
        else:
            category = {
            "category_name": category_name
            }
            mongo.categories.insert_one(category)

        flash(f'Category {category_name} added successfully!', 'success')
        
        return redirect(url_for('get_categories'))
    
 return render_template('add_category.html')

@app.route("/edit_category/<category_id>", methods=["GET", "POST"])
def edit_category(category_id):
    if os.environ.get("IS_SQL_DB") == "True":
       category = Category.query.get_or_404(category_id)
    else:
       category = mongo.categories.find_one({"_id": ObjectId(category_id)})
    if request.method == "POST":
        if os.environ.get("IS_SQL_DB") == "True":
            category.category_name = request.form.get("category_name")
            db.session.commit()
        else:
            mongo.categories.update_one({"_id": ObjectId(category_id)}, {"$set": {"category_name": request.form.get("category_name")}})
        flash("Category updated successfully!")

        return redirect(url_for("get_categories"))
    return render_template("edit_category.html", category=category)

@app.route("/delete_category/<category_id>")
def delete_category(category_id):
    if os.environ.get("IS_SQL_DB") == "True":
       category = Category.query.get_or_404(category_id)
       db.session.delete(category)
       db.session.commit()
    else:
        mongo.categories.delete_one({"_id": ObjectId(category_id)})
    flash("Category deleted successfully!")

    return redirect(url_for("get_categories"))


@app.route("/add_task", methods=["GET", "POST"])
def add_task():

    if os.environ.get("IS_SQL_DB") == "True":
        categories = list(Category.query.order_by(Category.category_name).all())
    else:
        categories = mongo.categories.find().sort("category_name", 1)

   
    if request.method == "POST":
        is_urgent = "on" if request.form.get("is_urgent") else "off"
        task = Task(
            task_name=request.form.get("task_name"),
            task_description=request.form.get("task_description"),
            is_urgent=bool(True if request.form.get("is_urgent") else False),
            due_date=request.form.get("due_date"),
            category_id=request.form.get("category_id")
        ) if os.environ.get("IS_SQL_DB") == "True" else {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
        }

        if os.environ.get("IS_SQL_DB") == "True":
              db.session.add(task)
              db.session.commit()
        else:
            mongo.tasks.insert_one(task)
        flash("Task added successfully!")
        return redirect(url_for("get_tasks"))
    
    return render_template("add_task.html", categories=categories)

@app.route("/edit_task/<task_id>", methods=["GET", "POST"])
def edit_task(task_id):
  
    if request.method == "POST":

        if os.environ.get("IS_SQL_DB") == "True":
           task.task_name = request.form.get("task_name")
           task.task_description = request.form.get("task_description")
           task.is_urgent = bool(True if request.form.get("is_urgent") else False)
           task.due_date = request.form.get("due_date")
           task.category_id = request.form.get("category_id")
           db.session.commit()
        else:
            is_urgent = "on" if request.form.get("is_urgent") else "off"
            task = {
            "category_name": request.form.get("category_name"),
            "task_name": request.form.get("task_name"),
            "task_description": request.form.get("task_description"),
            "is_urgent": is_urgent,
            "due_date": request.form.get("due_date"),
            "created_by": session["user"]
            }
            
   
    
        if os.environ.get("IS_SQL_DB") == "True":
           task = Task.query.get_or_404(task_id)
        else:
          task = mongo.tasks.update_one({"_id": ObjectId(task_id)}, {"$set": task})

        flash("Task Successfully Updated")
    if os.environ.get("IS_SQL_DB") == "True":
       categories = list(Category.query.order_by(Category.category_name).all())
    else:
       categories = mongo.categories.find().sort("category_name", 1)
       task = mongo.tasks.find_one({"_id": ObjectId(task_id)}) 
    return render_template("edit_task.html", task=task, categories=categories)

@app.route("/delete_task/<task_id>")
def delete_task(task_id):

    if os.environ.get("IS_SQL_DB") == "True":
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
    else:
        mongo.tasks.delete_one({"_id": ObjectId(task_id)}) 

    flash("Task Successfully Deleted")
    return redirect(url_for("get_tasks"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))