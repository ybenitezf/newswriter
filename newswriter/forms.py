from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
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


class RegisterForm(FlaskForm):
    username = StringField(
        'Usuario', validators=[DataRequired()])
    name = StringField('Nombre completo', validators=[DataRequired()])
    password1 = PasswordField(
        'Contraseña', validators=[
            DataRequired(),
            EqualTo('password2', message='Las contraseñas deben coincidir')
        ]
    )
    password2 = PasswordField(
        'Confirmar contraseña', validators=[DataRequired()])
