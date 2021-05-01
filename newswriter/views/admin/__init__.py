'''Vistas administrativas'''
from newswriter.models.security import Role, User
from newswriter.views.admin.roles import AddMememberForm, RoleDiced
from newswriter.views.admin.roles import RevokeRoleForm
from newswriter.views.admin.permissions import PermissionDiced
from flask.helpers import url_for
from flask import Blueprint, redirect, flash, render_template


admin_role = Blueprint('admin_role', __name__, url_prefix='/admin/role')
admin_permissions = Blueprint('admin_perms', __name__, url_prefix='/admin/permission')
RoleDiced().register(admin_role)
PermissionDiced().register(admin_permissions)


@admin_role.route('/<role>/<member>/revoke', methods=['GET', 'POST'])
def role_revoke(role, member):
    role_obj = Role.query.get_or_404(role)
    user = User.query.get_or_404(member)
    form = RevokeRoleForm()

    if form.validate_on_submit():
        user.roles.remove(role_obj)
        user.query.session.commit()
        flash(f"{user.name} quitado de {role_obj.name}")
        return redirect(url_for('.detail', pk=role_obj.id))

    return render_template('role/revoke.html', **locals())


@admin_role.route('/<pk>/add_member', methods=['GET', 'POST'])
def add_member(pk):
    role = Role.query.get_or_404(pk)
    
    form = AddMememberForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        user.roles.append(role)
        user.query.session.commit()
        flash(f"{user.name} asignado rol {role.name}")
        return redirect(url_for('.detail', pk=role.id))

    return render_template('role/addmember.html', **locals())
