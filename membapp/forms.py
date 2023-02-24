from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField
from flask_wtf.file import FileField, FileRequired,FileAllowed
from wtforms.validators import DataRequired,Email,Length,EqualTo

class ContactForm(FlaskForm):
    screenshot =FileField("Upload screenshot", validators=[FileRequired(),FileAllowed(['png','jpg','jpeg'],'the extention is not allowed')])
    email = StringField("Your Email:", validators=[Email( message="hello, your email should be valid"),DataRequired(message="we will need to have your email address in order to get back to you")])
    confirm_email = StringField('Confirm Email', validators=[EqualTo('email')])
    messages = TextAreaField("Message",validators=[DataRequired(),Length(min=10,message="this message is too small")])
    submit = SubmitField("Send Message")