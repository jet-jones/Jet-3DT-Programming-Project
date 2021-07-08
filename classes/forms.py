from wtforms import Form, validators, StringField, TextAreaField, PasswordField
from wtforms.fields.core import FieldList, FormField


class RegisterForm(Form):

    username = StringField("Username", [validators.length(min=4, max=15)])
    email = StringField("Email", [validators.Length(min=6, max=25)])
    password = PasswordField("Password", [
        validators.DataRequired(),
        validators.EqualTo("confirm", message="Passwords do not match.")
    ])
    confirm = PasswordField("Confirm Password", [validators.DataRequired()])

class LoginForm(Form):

    username = StringField("Username", [validators.length(min=4, max=15),validators.DataRequired()])
    password = PasswordField("Password", [validators.DataRequired()])

class ListForm(Form):
    name = StringField("Name",[validators.length(min=3, max=35),validators.DataRequired()])
    description = StringField("Description")
    sites = TextAreaField("Sites")

class SearchForm(Form):
    search = StringField("Search")

class EditForm(Form):
    site = StringField("Add new site")