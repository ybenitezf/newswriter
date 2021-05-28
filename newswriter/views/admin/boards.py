"""Boards CRUD for admin"""
from newswriter.models import content
from flask_diced import Diced
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class BoardCreateForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired()])
    submit = SubmitField('Crear')

class BoardDiced(Diced):
    model = content.Board

    # forms
    create_form_class = BoardCreateForm
