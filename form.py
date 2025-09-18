from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Email, Length

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Must be an email. Need @")])
    password = StringField("Password", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(message="Must be an email. Need @")])
    password = StringField("Password", validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters long.")])
    name = StringField("Name", validators=[DataRequired()])
    submit = SubmitField("Register")

class MovieForm(FlaskForm):
    rating = DecimalField("Your Rating Out of 10 e.g 7.5", validators=[DataRequired(), NumberRange(min=1, max=10, message="Must be 1 to 10")])
    review = StringField("Your Review", validators=[DataRequired()])
    ranking = IntegerField("Your Ranking", validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField("Done")

class SearchMovie(FlaskForm):
    search = StringField("Search Movies", validators=[DataRequired()])
    submit = SubmitField("Search")
