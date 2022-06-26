from ast import Pass
from crypt import methods
import email
from email.policy import default
from pickle import NONE
from enum import unique
from tokenize import Name
from traceback import format_exc
from wsgiref.validate import validator
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_wtf import FlaskForm
from sqlalchemy import Integer
# Imports different components from WTF forms
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length, Email
from wtforms.widgets import TextArea
 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user

from datetime import datetime

from flask_ckeditor import CKEditor
from flask_ckeditor import CKEditorField

import os

# Creating env variable form .env
from dotenv import load_dotenv
load_dotenv()

# Create the instances of main extendes
app = Flask(__name__)

# configuration of CKEditor
app.config['CKEDITOR_PKG_TYPE'] = 'basic'
ckeditor = CKEditor(app)

# App Config
    # Secret key required by wtf forms

app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    # Add database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

# Initialize the database 
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Set up the Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create db Model for the users
# Relationship db one to many, one user, many posts
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(125))
    dateAdded = db.Column(db.DateTime, default=datetime.utcnow)
    # db relationship - post adds the owner column to the Post Model
    post = db.relationship("Post", backref='owner', lazy='dynamic')

    # Property checking if password is hashed
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")

    # Password setter and password verify
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return'Name % r>' % self.name

# Create the database MODEL for our Blog Post
# This db has a extra column owner, added by Users - db Relationship
class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(255))
    content = db.Column(db.Text)
    author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow())
    slug = db.Column(db.String(255))
    # db relation - id of the post owner
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def _repr_(self):
        return '<Post ()>'.format(self.title)

    

# Create the form for our database
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('psw2', message=("Passwords must match"))])
    psw2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Add User")

# Custom validator error checking is username already exist in the database
    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Username alreeady exist, please use diffrent username.")

# Custom validator error checking if the password already exist in the database
    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("This email is already in use, please use another emial.")


# Create the form for user.html
class NameForm(FlaskForm):
    name = StringField("What's Your Name:", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create the Form for the Post
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = StringField("Content", validators=[DataRequired()], widget = TextArea())
    content = CKEditorField('Content', validators=[DataRequired()] ) 
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create LoginForm
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Login")

# Create Search Form
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Search")

# Pass form to the base page.
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Create login page
@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            #  Check the hashed password and user password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('Login Successful!!')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password!!! Try again...')
        else:
            flash("User dos not exist, please register!!!")
    return render_template('login.html', form=form)

# Create dashboard page
@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    all_users = Users.query.order_by(Users.dateAdded)
    return render_template('dashboard.html', all_users=all_users)

# Logout logic
@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    flash('You are logged out!!!')
    return redirect(url_for('login'))

# Main route, showing all the blog's posts
@app.route('/')
def index():
    # Grabbing all the posts from the database, orderes by post date
    posts = Post.query.order_by(Post.date_posted)

    return render_template('index.html', posts=posts)

# Showing all the user's posts
@app.route('/my_posts')
def user_post():
    # Grabbing all the user's posts from the database, orderes by post date
    user = Users.query.filter_by(username=current_user.username).first()
    posts = user.post.all()

    return render_template('user_posts.html', posts=posts)

# A route shownig the individual post page
@app.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

# Added user page - CHECK IF THIS PAGE IS NEEDED!!!!
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
@app.route('/register', methods=['POST', 'GET'])
def register():
    add_form = UserForm()
    if add_form.validate_on_submit():
        user = Users.query.filter_by(username=add_form.username.data).first()
        if user is None:
            flash('User Added Succesfully')
            hashed_password = generate_password_hash(add_form.password_hash.data, "sha256")
            user = Users(name=add_form.name.data, username=add_form.username.data, email=add_form.email.data, password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = add_form.name.data
        add_form.name.data = ""
        add_form.username.data = ""
        add_form.email.data = ""
        return redirect(url_for('login'))
    
    return render_template('register.html', form=add_form)

# Create the User Edit page
@app.route('/edit_user/<int:id>', methods=['POST', 'GET'])
def edit_user(id):
    form=UserForm()
    user_to_update = Users.query.get_or_404(id)

    if request.method == "POST":
    
        user_to_update.name = request.form['name']
        user_to_update.username = request.form['username']
        user_to_update.email = request.form['email']
        try:
            db.session.commit()
            our_users = Users.query.order_by(Users.dateAdded)
            form.name.data = ""
            form.username.data = ""
            form.email.data = ""
            flash('User Updated Successfully!')
            return render_template('dashboard.html')
        except:
            flash('There was some problem, try again!')
            return render_template('dashboard.html')
    else:
        # first render of the page
        our_users = Users.query.order_by(Users.dateAdded)
        return render_template('edit_user.html', form=form, user_to_update=user_to_update, our_users=our_users, id=id)

# Delete the entry
@app.route('/deleteUser/<int:id>')
@login_required
def delete_user(id):
    form=UserForm()
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('User Deleted Successfully!!!')
        our_users = Users.query.order_by(Users.dateAdded)

        # redirect instead of render_template in order to come back to add_user page with out any trace of delete id which can give an error.
        return redirect(url_for('register'))
    except:
        flash('Somthing went really wrong when deleteing, try one more time...')
        our_users = Users.query.order_by(Users.dateAdded)
        return redirect(url_for('register'))

# The route showing how to use JSON in our projects
# Flask will return JSON form standard Python's dictionary
@app.route('/date')
def get_current_date():
    favorite_pizza = {
        "John":"Peperoni",
        "Anna":"Vegi"
    }
    return favorite_pizza
    # return {"Date":date.today()}

# Add the Post Page
@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    form.author.data = current_user.username

    if form.validate_on_submit():
        # For db reletionship, owner of the post = logged user
        owner = Users.query.get(current_user.id)
        post = Post(title=form.title.data, content = form.content.data, author=form.author.data, slug=form.slug.data, owner=owner )
        # Clearing the form
        form.title.data = ''
        form.content.data = ''
        # form.author.data = ''
        form.slug.data = ''
        # Add the post to the database
        db.session.add(post)
        db.session.commit()

        # Return the flash message
        flash("Blog Post has been successfully Added")
        return redirect(url_for("post", id=post.id))

    # Redirect to the Add_Post page
    return render_template("add_post.html", form=form)

@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_post(id):

    post_to_edit = Post.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        post_to_edit.content = form.content.data
        post_to_edit.slug = form.slug.data
        post_to_edit.author = form.author.data

        db.session.add(post_to_edit)
        db.session.commit()

        flash("Post updated succesfully!!!")
        return redirect(url_for("post", id=post_to_edit.id))

    form.title.data = post_to_edit.title
    form.content.data = post_to_edit.content
    form.slug.data = post_to_edit.slug
    form.author.data = post_to_edit.author

    return render_template('edit_post.html', form=form, post=post_to_edit)

@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('Post deleted Successfully')

        posts = Post.query.order_by(Post.date_posted)
        return render_template('index.html', posts=posts)

    except:
        flash('Somthing went really wrong when deleteing, try one more time...')
        posts = Post.query.order_by(Post.date_posted)
        return render_template('index.html', posts=posts)

# Route for search function 
@app.route("/search", methods=["POST"])
def search():
    form = SearchForm()
    searched_posts = Post.query
    if form.validate_on_submit():
        # get data from the search form
        searched_for = form.searched.data
        # query the databese
        searched_posts=searched_posts.filter(Post.content.like('%' + searched_for + '%'))
        searched_posts = searched_posts.order_by(Post.date_posted).all()
        return render_template('search.html', form=form, searched = searched_for, posts = searched_posts)
    else:
        posts = Post.query.order_by(Post.date_posted)
        return render_template('index.html', posts=posts)



@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


    

