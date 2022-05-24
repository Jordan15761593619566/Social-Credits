from flask_wtf import FlaskForm
from wtforms import SelectField
from wtforms.validators import DataRequired

class Select_Activity(FlaskForm):
    activity = SelectField('activities', validators=[DataRequired()], coerce=int)

class Select_User(FlaskForm):
    user = SelectField('user', validators=[DataRequired()], coerce=int)

