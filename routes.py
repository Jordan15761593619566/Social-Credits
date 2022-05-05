from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import login_required, logout_user
from flask_login import LoginManager, login_user, current_user
from forms import Select_Activity, Select_User
import hashlib

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
        user_hashed_password = hashlib.sha256()
        user_hashed_password.update(request.form.get("password").encode())
        password = user_hashed_password.hexdigest()
        if user and user.check_password(password):
            login_user(user)
            #now current_user is set to this user- redirect back to home
            return render_template('home.html', page_title='HOME')
        
        # Else flash an error message
        else:
            flash("Username and password not recognised")
    return render_template("login.html", page_title = 'login')

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    # log out the user
    logout_user()
    return redirect(url_for('home'))

# Home page route
@app.route('/')
def root():
    return render_template('home.html', page_title = 'Home')

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', page_title = 'Admin')

@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    if request.form:
        new_name = request.form.get('name')
        new_address = request.form.get('address')
        new_password = request.form.get('password')
        new_credits = 1000 # Starting the user with 1000 credits - so the value does not print as 'None', and so the user does not start off in the bad

        # Hashing method
        hashed_password = hashlib.sha256()
        hashed_password.update(new_password.encode())
        new_password = hashed_password.hexdigest()

        new_user = models.User(name=new_name, address=new_address, password=new_password, credits = new_credits)
        db.session.add(new_user)
        db.session.commit()

        flash("Successfully created account!")
    return redirect(url_for('admin'))

@app.route('/credits', methods = ["GET","POST"])
def credits():
    user = models.User.query.filter_by(id=current_user.id).first()
    return(render_template('credits.html', page_title = 'Credits', user = user))

@app.route('/give_credits', methods = ["GET", "POST"])
def give_credits():
    form = Select_Activity()
    activities = models.Activities.query.all()
    form.activities.choices = [(activity.id, activity.type) for activity in activities]

    userform = Select_User()
    users = models.User.query.all()

    userform.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users]
    return render_template('give_credits.html', page_title = 'Give Credits', form = form, userform = userform)

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)