from crypt import methods
import email
from email.policy import default
from enum import unique
from tokenize import Name
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
# importing SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

from datetime import datetime

import os

# Creating env variable form .env
from dotenv import load_dotenv
load_dotenv()

# Create the instances of main extendes
app = Flask(__name__)


# App Config
    # Secret key required by wtf forms

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    # Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the database
db = SQLAlchemy(app)

# Create db Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(200), nullable = False)
    email = db.Column(db.String(120), nullable = False, unique=True)
    dateAdded = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return'Name % r>' % self.name

# Create the form for our database
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Add User")


# Create the form for user.html
class NameForm(FlaskForm):
    name = StringField("What's Your Name:", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user', methods=["POST", "GET"])
def user():
    # Sets the var name to None form the first render of the page
    name = None
    form = NameForm()
# checks if form validate - has an input then:
    if form.validate_on_submit():
        flash('Submited Succesfully')
        name = form.name.data
        form.name.data = ""
    return render_template('user.html', name=name, form=form)

# Route for the template which will add the user to our database
@app.route('/user/add', methods=['POST', 'GET'])
def add_user():
    name = None
    add_form = UserForm()

    if add_form.validate_on_submit():
        
        user = Users.query.filter_by(email=add_form.email.data).first()
        if user is None:
            flash('User Added Succesfully')
            user = Users(name=add_form.name.data, email=add_form.email.data)
            db.session.add(user)
            db.session.commit()
        
        name = add_form.name.data
        add_form.name.data = ""
        add_form.email.data = ""
        
    our_users = Users.query.order_by(Users.dateAdded)
    
    return render_template('add_user.html', form=add_form, name = name, our_users=our_users)

# Create the update page
@app.route('/update<int:id>', methods=['POST', 'GET'])
def update(id):
    form=UserForm()
    user_to_update = Users.query.get_or_404(id)

    if request.method == "POST":
    
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        try:
            db.session.commit()
            our_users = Users.query.order_by(Users.dateAdded)
            form.name.data = ""
            form.email.data = ""
            flash('User Updated Successfully!')
            return render_template('add_user.html', form=form, name = None, our_users=our_users)
        except:
            flash('There was some problem, try again!')
            our_users = Users.query.order_by(Users.dateAdded)
            return render_template('add_user.html', form=form, name = None, our_users=our_users)
    else:
        # first render of the page
        our_users = Users.query.order_by(Users.dateAdded)
        return render_template('update.html', form=form, user_to_update=user_to_update, our_users=our_users, id=id)

# Delete the entry
@app.route('/delete<int:id>')
def delete(id):
    form=UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!!!')
        our_users = Users.query.order_by(Users.dateAdded)

        # redirect instead of render_template in order to come back to add_user page with out any trace of delete id which can give an error.
        return redirect(url_for('add_user'))
    except:
        flash('Somthing went really wrong when deleteing, try one more time...')
        our_users = Users.query.order_by(Users.dateAdded)
        return redirect(url_for('add_user'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


    

