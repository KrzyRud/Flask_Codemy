from flask import Flask, render_template, request, session, redirect, url_for, flash

# Create the instances of main extendes
app = Flask(__name__)

# Secret key required by wtf forms
app.config['SECRET_KEY'] = 'IMO9012305!@#'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


    

