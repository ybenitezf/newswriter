from newswriter.models import security
from flask_diced import Diced
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError
from flask_wtf import FlaskForm
from flask import redirect, flash, render_template
from typing import List


class RoleCreateForm(FlaskForm):
    name = StringField('Nombre del rol', validators=[DataRequired()])
    description = StringField('Descripción')
    submit = SubmitField("Crear rol")


class RoleDeleteForm(FlaskForm):
    submit = SubmitField('Eliminar rol')


class RevokeRoleForm(FlaskForm):
    submit = SubmitField('Quitar del grupo')


class AddMememberForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    submit = SubmitField('Agregar')

    def validate_username(form, field):
        chk_usr = security.User.query.filter_by(
            username=field.data).first()

        if chk_usr is None:
            raise ValidationError('No existe el usuario')


class RoleDiced(Diced):
    model = security.Role
    create_form_class = RoleCreateForm
    edit_form_class = RoleCreateForm
    delete_form_class = RoleDeleteForm

    edit_rule = '/<pk>/edit'
    delete_rule = '/<pk>/delete'
    detail_rule = '/<pk>/members'

    def edit_view(self, pk):
        """edit view function

        :param pk:
            the primary key of the model to be edited.
        """
        obj = self.query_object(pk)
        form = self.edit_form_class(obj=obj)
        if form.validate_on_submit():
            form.populate_obj(obj)
            obj.save()
            message = self.edit_flash_message
            if message is None:
                message = self.object_name + ' updated'
            if message:
                flash(message)
            return redirect(self.edit_redirect_url)
        context = self.edit_view_context({
            self.edit_form_name: form,
            self.object_name: obj
        })
        return render_template(self.edit_template, **context)

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
            if message:
                flash(message)
            return redirect(self.delete_redirect_url)
        context = self.delete_view_context({
            self.delete_form_name: form,
            self.object_name: obj
        })
        return render_template(self.delete_template, **context)
