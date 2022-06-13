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

# Activiting the login manager
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
            if user.permissions == "ADMINISTRATOR":
                flash ('Successfully logged in with administrative permissions!', 'success') #Letting admin users know they have correct admin perms
            else:
                flash('Successfully logged in!', 'success')
            #now current_user is set to this user- redirect back to home
            return redirect(url_for('root'))
        
        # Else flash an error message
        else:
            flash("Incorrect username or password. Please check your details and try again", 'error')
    return render_template("login.html", page_title = 'Login')

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    # log out the user
    logout_user()
    flash('Successfully logged out!', 'success')
    return redirect(url_for('root')) # This redirect goes back to the homepage - the '/' (root) route 

# Home page route
@app.route('/')
def root():
    return render_template('home.html', page_title = 'Home')

@app.route('/admin')
@login_required
def admin():
    if current_user.permissions == "ADMINISTRATOR":
        deleteForm = Select_User() # Getting the Select_User form and assigning it to deleteForm
        users = models.User.query.all() # Collecting all the User information from the DB
        deleteForm.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users] # assigning all the user id's and names to the choices for the deleteForm.

        deleteActivityForm = Select_Activity() # Assigning the Select_Activity form template
        activities = models.Activities.query.all() # Pulling all activities from the database
        deleteActivityForm.activity.choices = [(activity.id, f"{activity.id} - {activity.type}") for activity in activities] # Storing all the data into the form template.

        return render_template('admin.html', page_title = 'Admin', deleteForm = deleteForm, deleteActivityForm = deleteActivityForm) # Rendering the admin page, with the two dropdown box forms attached
    else:
        flash('you\'re not an admin, nice try', 'error')
        return redirect(url_for('root'))
        
@app.route('/add_user', methods = ['GET', 'POST'])
def add_user():
    if request.form:
        new_name = request.form.get('name')
        new_address = request.form.get('address')
        new_password = request.form.get('password')
        new_credits = 1000

        # Hashing method
        hashed_password = hashlib.sha256()
        hashed_password.update(new_password.encode()) # Encode the password
        new_password = hashed_password.hexdigest()

        # Creating a new User object - to add to the database.
        new_user = models.User(name=new_name, address=new_address, password=new_password, credits = new_credits)
        db.session.add(new_user)
        db.session.commit()

        flash("Successfully created account!", 'success')
    return redirect(url_for('admin'))

@app.route('/credits', methods = ["GET","POST"])
def credits():
    recommendedCredits = 5000 # The amount of credits that a "good citizen" should be at. Change this to make the "good citizen" value different.

    # Getting the user information from the database, filtering with the current signed in user.
    user = models.User.query.filter_by(id=current_user.id).first()
    user_activities = models.User_Activities.query.filter_by(user_id = current_user.id).all()
    # Getting the starting credits
    user_credits = user.credits
    # Creating an empty list to append the activities to
    all_activities = []
    # Every activity the user has completed
    for user_activity in user_activities:
        # Getting the activity completed from the database
        activity = models.Activities.query.filter_by(id = user_activity.activity_id).first()
        # Saving its value
        activity_value = activity.value
        # Totalling the credits
        user_credits += activity_value
        # Adding the activity to the list so it can be displayed in the table on the credits page. 
        all_activities.append(activity)
    percentageOfRecommended = user_credits/recommendedCredits # Getting the percentage of the recommended credits.
    if request.method == "POST":
        return redirect(url_for("give_credits"))
    return(render_template('credits.html', page_title = 'Credits', user = user, user_credits = user_credits, all_activities = all_activities, percentage = percentageOfRecommended))

@app.route('/give_credits', methods = ["GET", "POST"])
def give_credits():
    form = Select_Activity() # assigning the form to a variable
    activities = models.Activities.query.all() # pulling the data
    form.activity.choices = [(activity.id, activity.type) for activity in activities] # assigning the data to the form

    userform = Select_User() # assigning the form to a variable
    users = models.User.query.all() # pulling the data from the database
    userform.user.choices = [(user.id, f"{user.id} - {user.name}") for user in users] # assigning the data to the form

    if request.method == "POST": # if a form is submitted
        if form.is_submitted(): # and the form is the Select_Activity form for this specific purpose (done this way as there are multiple different forms using the "POST" method on the admin page)
            activity_id = form.activity.data # Getting the selected activity id from the submitted form
            activity = models.Activities.query.filter_by(id = activity_id).first() # Getting the activity information by putting the id into the database
            user_id = userform.user.data # Getting the selected user from the form
            user = models.User.query.filter_by(id = user_id).first() # Getting the user's information from the database

            user_id = user.id # Assigning the database user id to a variable
            activity_id = activity.id # Assigning the database activity id to the variable
            new_user_activity = models.User_Activities(user_id = user_id, activity_id = activity_id) # putting these into a database model
            db.session.add(new_user_activity) # adding it to the database session
            try: #do this first
                db.session.commit() # commit it to the database
                flash("Successfully updated user credits.", 'success') # flash the user with a success message
            except: # if this fails
                flash("Failed to update user's credits.", 'error') # flash the user with an error message
        return redirect(url_for('credits')) # redirect back to the home page
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
            flash('User successfully deleted!', 'success')
    return redirect(url_for('admin'))

@app.route('/add_activity', methods = ['POST'])
def add_activity():
    if request.form:
        new_type = request.form.get("type") # Getting the Activity Type (Name)
        new_value = request.form.get("value") # Getting the Activity Value (Credits Worth)

        new_activity = models.Activities(type = new_type, value = new_value) # Creating a new Activity object

        db.session.add(new_activity) # Adding the Activity object to the database session
        db.session.commit() # Commmiting the database session, saving it to the database, so it is saved and not just sitting in RAM.
        flash('Successfully added new activity!', 'success')
    return redirect(url_for('admin'))

@app.route('/delete_activity', methods = ['GET', 'POST'])
def delete_activity():
    deleteActivityForm = Select_Activity() # Assigning the Select_Activity form model
    activities = models.Activities.query.all() # Pulling the activities from the database
    deleteActivityForm.activity.choices = [(activity.id, f"{activity.id} - {activity.type}") for activity in activities] # Assigning them to the dropdownn form
    if request.method == "POST": # If the webpage request returns a response with a 'POST' method
        if deleteActivityForm.is_submitted(): # Ensuring the specific form is submitted, as multiple forms are present on the Admin page.
            activity_id = deleteActivityForm.activity.data # Assigning the user's selection to a variable
            activity = models.Activities.query.filter_by(id = activity_id).first() # Referencing it into the database to get all of the items' information

            db.Session = db.Session.object_session(activity) # Opening a new db Session in reference to the activity object
            db.Session.delete(activity) # Deleting the activity
            db.Session.commit() # Commiting it to the database
            flash('Successfully deleted the activity!', 'success') # This flashes the success message to the user, below the nav bar. The success attribute makes it green.
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5001)