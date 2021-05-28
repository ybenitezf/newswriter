'''CRUD en permisos'''
from newswriter.models import security
from newswriter.models.permissions import BoardPermissionHelpers
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired
from flask_diced import Diced
from flask import url_for, render_template, flash, redirect


class PermissionCreateForm(FlaskForm):
    name = SelectField(
        "Permiso", choices=BoardPermissionHelpers.getFormChoices())
    model_name = SelectField(
        "Modelo", choices=[('board', 'Board')])
    record_id = StringField("Objeto")
    role_id = HiddenField("Role", validators=[DataRequired()])


class RevokePermissionForm(FlaskForm):
    submit = SubmitField('Rebocar permiso')


class PermissionDiced(Diced):
    model = security.Permission
    exclude_views = ('detail', 'edit')

    # rules
    index_rule = '/<role_id>/'
    create_rule = '/<role_id>/create/'
    delete_rule = '/<pk>/delete/'

    # forms
    create_form_class = PermissionCreateForm
    delete_form_class = RevokePermissionForm

    # properties

    # views
    def index_view(self, role_id):
        """index view function"""
        role = security.Role.query.get_or_404(role_id)
        context = self.index_view_context({
            self.object_list_name: self.query_all(role),
            "role": role,
            "get_permission_label": BoardPermissionHelpers.getPermissionLabel
        })
        return render_template(self.index_template, **context)

    def query_all(self, role: security.Role):
        """returns all objects"""
        return role.permissions

    def delete_view(self, pk):
        """delete view function

        :param pk:
            the primary key of the model to be deleted.
        """
        obj = self.query_object(pk)
        form = self.delete_form_class(obj=obj)
        if form.validate_on_submit():
            obj.delete()
            message = self.delete_flash_message
            if message is None:
                message = self.object_name + ' deleted'
            return {"message": message}
        context = self.delete_view_context({self.delete_form_name: form})
        return render_template(self.delete_template, **context)

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
