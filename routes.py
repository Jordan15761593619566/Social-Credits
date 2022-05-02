from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import login_required, logout_user
from flask_login import LoginManager, login_user, current_user

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///CreditsDB.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'correcthorsebatterystaple'

# Initialising the Database access
db = SQLAlchemy(app)

# Initialising the loginManager
login_manager = LoginManager(app)

# Enabling forms
WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = 'sup3r_secr3t_passw3rd'

# Importing the database models
import models

@login_manager.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)

@app.route('/login',methods=['GET','POST'])
def login():
    if (request.method) == "POST":
        #we posted the form- try to login
        #get the user from the forms username field
        user = models.User.query.filter_by(name=request.form.get("username")).first()
        #check if we got one and that the password's match- MUST USE HASHED PASSWORDS!!! THIS IS JUST A DEMO!!
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            #now current_user is set to this user- redirect back to home
            return render_template('home.html', page_title='HOME')
            
        # Else flash an error message
        else:
            print('5')
            flash("Username and password not recognised")
    return render_template("login.html", page_title = 'login')

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    print('1')
    # log out the user
    logout_user()
    print('2')
    return render_template('home.html', page_title='HOME')

# Home page route
@app.route('/')
def root():
    return render_template('home.html', page_title = 'Home')

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)

