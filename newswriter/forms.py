from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from wtforms.widgets.html5 import EmailInput


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')


class ProfileForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    credit_line = StringField('Creditos', validators=[DataRequired()])
    email = StringField(
        'Correo', validators=[Email()],
        widget=EmailInput())
