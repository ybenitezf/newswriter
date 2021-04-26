'''Vistas administrativas'''
from newswriter.views.admin.roles import RoleDiced
from newswriter.views.admin.permissions import PermissionDiced
from flask import Blueprint


admin_role = Blueprint('admin_role', __name__, url_prefix='/admin/role')
admin_permissions = Blueprint('admin_perms', __name__, url_prefix='/admin/permission')
RoleDiced().register(admin_role)
PermissionDiced().register(admin_permissions)
