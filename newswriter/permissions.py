from flask_principal import RoleNeed, Permission

AdminRolNeed = RoleNeed('admin')
admin_perm = Permission(AdminRolNeed)
