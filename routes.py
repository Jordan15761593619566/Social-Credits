from flask import Flask, render_template, abort, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login.utils import login_required, logout_user
from flask_login import LoginManager, login_user, current_user
from forms import Select_Activity, Select_User
import hashlib

app = Flask(__name__)

# Attaching the database
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
        #check if we got one and that the password's match - using password hashing for security
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
    return redirect(url_for('root'))

# Home page route
@app.route('/')
def root():
    return render_template('home.html', page_title = 'Home')

@app.route('/admin')
@login_required
def admin():
    deleteForm = Select_User() # Getting the Select_User form and assigning it to deleteForm
    users = models.User.query.all() # Collecting all the User information from the DB
    deleteForm.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users] # assigning all the user id's and names to the choices for the deleteForm.
    return render_template('admin.html', page_title = 'Admin', deleteForm = deleteForm)

@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    if request.form:
        new_name = request.form.get('name')
        new_address = request.form.get('address')
        new_password = request.form.get('password')
        new_credits = 1000

        # Hashing method
        hashed_password = hashlib.sha256()
        hashed_password.update(new_password.encode())
        new_password = hashed_password.hexdigest()

        # Creating a new User object - to add to the database.
        new_user = models.User(name=new_name, address=new_address, password=new_password, credits = new_credits)
        db.session.add(new_user)
        db.session.commit()

        flash("Successfully created account!")
    return redirect(url_for('admin'))

@app.route('/credits', methods = ["GET","POST"])
def credits():
    user = models.User.query.filter_by(id=current_user.id).first()
    user_activities = models.User_Activities.query.filter_by(user_id = current_user.id).all()
    user_credits = user.credits
    all_activities = []
    for user_activity in user_activities:
        activity = models.Activities.query.filter_by(id = user_activity.activity_id).first()
        activity_value = activity.value
        user_credits += activity_value
        all_activities.append(activity)
    if request.method == "POST":
        return redirect(url_for("give_credits"))
    return(render_template('credits.html', page_title = 'Credits', user = user, user_credits = user_credits, all_activities = all_activities))

@app.route('/give_credits', methods = ["GET", "POST"])
def give_credits():
    form = Select_Activity()
    activities = models.Activities.query.all()
    form.activities.choices = [(activity.id, activity.type) for activity in activities]

    userform = Select_User()
    users = models.User.query.all()
    userform.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users]

    if request.method == "POST":
        if form.is_submitted():
            activity_id = form.activities.data
            activity = models.Activities.query.filter_by(id = activity_id).first()
            user_id = userform.user.data
            user = models.User.query.filter_by(id = user_id).first()

            user_id = user.id
            activity_id = activity.id
            new_user_activity = models.User_Activities(user_id = user_id, activity_id = activity_id)
            db.session.add(new_user_activity)
            try:
                db.session.commit()
                flash("Successfully updated user credits.")
            except:
                flash("Failed to update user's credits.")
        return redirect(url_for('credits'))
    return render_template('give_credits.html', page_title = 'Give Credits', form = form, userform = userform)

@app.route('/delete_user', methods = ["GET", "POST"])
def delete_user():
    deleteForm = Select_User()
    users = models.User.query.all()
    deleteForm.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users]
    if request.method == "POST":
        if deleteForm.is_submitted():
            user_id = deleteForm.user.data
            user = models.User.query.filter_by(id = user_id).first()

            db.Session = db.Session.object_session(user)
            db.Session.delete(user)#delete it
            db.Session.commit()#commit change to db
    return redirect(url_for('admin'))


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)