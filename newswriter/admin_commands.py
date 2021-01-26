from newswriter.models.security import Role, User, create_user as CreateUser
from newswriter.shemas import UserSchema, RoleSchema
from newswriter import db
from flask import Blueprint
from flask.cli import cli
from pprint import pprint
import click

admin_cmds = Blueprint("admin", __name__)
users_cmds = Blueprint("security", __name__)


@users_cmds.cli.command('createuser')
@click.option('--email', default='', help='email')
@click.option('--name', default='', help='Nombre')
@click.argument('username')
@click.argument('password')
def create_user(username, password, email, name):
    """Crear un usuario.
    
    \b
    USERNAME: nombre de usuario, no debe existir
    PASSWORD: contraseña del usuario
    """
    u = User.query.filter_by(username=username).first()
    if u is not None:
        raise click.ClickException("Ya existe el usuario")
    
    u = CreateUser(username, password, email=email, name=name)
    db.session.add(u)
    db.session.commit()
    click.echo("Usuario creado")


@users_cmds.cli.command("users")
@click.option('--rol', default=None, help='Rol especifico')
def listar_usuarios(rol):
    """Listar los usuarios."""
    click.echo("Usarios registrados:")
    s = UserSchema()
    if rol is None:
        pprint(s.dump(User.query.all(), many=True), indent=2, compact=True)
    else:
        grp = Role.query.filter_by(name=rol).first()
        if grp.users:
            pprint(s.dump(grp.users, many=True), indent=2, compact=True)
        else:
            click.echo("No hay usuarios con rol {}".format(rol))


@users_cmds.cli.command('createrol')
@click.argument('rolname')
def create_group(rolname):
    """Crear grupo de usuarios.
    
    \b
    ROLNAME: nombre del rol, debe ser unico en el sistema
    """
    grp = Role.query.filter_by(name=rolname).first()
    if grp is None:
        grp = Role(name=rolname)
        db.session.add(grp)
        db.session.commit()
        click.echo("Rol creado")
    else:
        click.echo("Ya existe ese rol")


@users_cmds.cli.command('asignrol')
@click.argument("user")
@click.argument("rol")
def asignar_rol(user, rol):
    """Asignar rol a usuario.

    \b
    USER: nombre del usuario
    ROL: nombre del rol
    """
    u = User.query.filter_by(username=user).first()
    grp = Role.query.filter_by(name=rol).first()

    if u is None or grp is None:
        raise click.ClickException("El usuario o el rol no existen")

    if grp in u.roles:
        raise click.ClickException("El usuario ya tiene el rol")

    u.roles.append(grp)
    db.session.add(u)
    db.session.commit()
    click.echo("Realizado {} tiene el rol {}".format(user, rol))


@users_cmds.cli.command('roles')
def listar_roles():
    """Listar los roles."""
    click.echo("Listado de roles")
    s = RoleSchema()
    pprint(s.dump(Role.query.all(), many=True), indent=2)
