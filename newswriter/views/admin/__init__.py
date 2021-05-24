'''Vistas administrativas'''
from newswriter.models.security import Role, User
from newswriter.views.admin.roles import AddMememberForm, RoleDiced
from newswriter.views.admin.roles import RevokeRoleForm
from newswriter.views.admin.permissions import PermissionDiced
from newswriter.views.admin.boards import BoardDiced
from newswriter.permissions import admin_perm
from flask_menu import current_menu, register_menu
from flask_menu.classy import classy_menu_item
from flask_classful import FlaskView
from flask import Blueprint, redirect, flash, render_template, url_for


# just a container for redirect to the concrete blueprints
admin_role = Blueprint('admin_role', __name__, url_prefix='/admin/role')
admin_permissions = Blueprint(
    'admin_perms', __name__, url_prefix='/admin/permission')
admin_boards = Blueprint('admin_boards', __name__, url_prefix='/admin/board')

decorators = [admin_perm.require(http_exception=403)]

RoleDiced(
    detail_decorators=decorators,
    index_decorators=decorators,
    create_decorators=decorators,
    edit_decorators=decorators,
    delete_decorators=decorators
).register(admin_role)
PermissionDiced(
    detail_decorators=decorators,
    index_decorators=decorators,
    create_decorators=decorators,
    edit_decorators=decorators,
    delete_decorators=decorators
).register(admin_permissions)
BoardDiced(
    detail_decorators=decorators,
    index_decorators=decorators,
    create_decorators=decorators,
    edit_decorators=decorators,
    delete_decorators=decorators
).register(admin_boards)



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


# Just for the sake of having a menu entry for administrators
class AdminLinks(FlaskView):
    route_base = '/admin'

    @classy_menu_item(
        "actions.admin.boards", "Boards", 
        visible_when=lambda: admin_perm.can())
    def admin_boards(self):
        return redirect(url_for('admin_boards.index'))

    @classy_menu_item(
        "actions.admin.roles", "Roles",
        visible_when=lambda: admin_perm.can())
    def admin_roles(self):
        return redirect(url_for('admin_role.index'))


