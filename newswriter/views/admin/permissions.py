'''CRUD en permisos'''
from wtforms import validators
from newswriter.models import security
from newswriter.models import permissions as perms
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, HiddenField
from wtforms.validators import DataRequired
from flask_diced import Diced
from flask import url_for, render_template, flash, redirect


def _pl(k):
    return (k, perms.BOARD_PERMS_DESCRIPTIONS[k])


class PermissionCreateForm(FlaskForm):
    name = SelectField(
        "Permiso", choices=[_pl(k) for k in perms.BOARD_PERMS_DESCRIPTIONS])
    model_name = SelectField(
        "Modelo", choices=[('board', 'Board')])
    record_id = StringField("Objeto")
    role_id = HiddenField("Role", validators=[DataRequired()])


class PermissionDiced(Diced):
    model = security.Permission
    exclude_views = ('detail',)

    # rules
    index_rule = '/<role_id>/'
    create_rule = '/<role_id>/create/'

    # forms
    create_form_class = PermissionCreateForm

    # properties

    def index_view(self, role_id):
        """index view function"""
        role = security.Role.query.get_or_404(role_id)
        context = self.index_view_context({
            self.object_list_name: self.query_all(role),
            "role": role
        })
        return render_template(self.index_template, **context)

    def query_all(self, role: security.Role):
        """returns all objects"""
        return role.permissions

    def create_view(self, role_id):
        """create view function"""
        role = security.Role.query.get_or_404(role_id)

        form = self.create_form_class()
        if form.validate_on_submit():
            obj = self.model()
            form.populate_obj(obj)
            obj.save()
            message = self.create_flash_message
            if message is None:
                message = self.object_name + ' created'
            if message:
                flash(message)
            return redirect(url_for('.index', role_id=role.id))

        context = self.create_view_context({
            self.create_form_name: form,
            "role": role
        })
        return render_template(self.create_template, **context)
