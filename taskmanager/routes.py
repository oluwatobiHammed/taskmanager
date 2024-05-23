from flask import flash, render_template, request, redirect, url_for
from taskmanager import app, db
from taskmanager.models import Category, Task


@app.route("/")
def home():
    return render_template("tasks.html")

@app.route("/categories")
def categories():
    categories = list(Category.query.order_by(Category.category_name).all())
    return render_template("categories.html", categories=categories)

@app.route("/add_category", methods=["GET", "POST"])
def add_category():
 if request.method == 'POST':
        category_name = request.form.get('category_name')
        existing_category = Category.query.filter_by(category_name=category_name).first()
        
        if existing_category:
            flash(f'Category {category_name} already exists.', 'warning')
        else:
            new_category = Category(category_name=category_name)
            db.session.add(new_category)
            db.session.commit()
            flash(f'Category {category_name} added successfully!', 'success')
        
        return redirect(url_for('categories'))
    
 return render_template('add_category.html')

 