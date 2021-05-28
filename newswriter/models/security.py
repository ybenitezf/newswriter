from newswriter import db
from newswriter.models import _gen_uuid
from newswriter.models.permissions import BOARD_ALL_PERMS
from flask_login import UserMixin, current_user
from flask_principal import Need, identity_loaded, RoleNeed, UserNeed, ItemNeed
from flask_diced import persistence_methods
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random

user_roles = db.Table(
    'user_roles',
    db.Column(
        'user_id', db.String(32), db.ForeignKey('user.id'),
        primary_key=True),
    db.Column(
        'role_id', db.String(32), db.ForeignKey('role.id'),
        primary_key=True)
)


@persistence_methods(db)
class Role(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))
    permissions = db.relationship('Permission', lazy='select', backref='role')

    def __repr__(self):
        return '<Role {}>'.format(self.name)

    def addPermission(self, name, record_id, model_name):
        p = Permission.query.filter_by(
            name=name, model_name=model_name,
            record_id=record_id, role_id=self.id).first()
        if p is None:
            p = Permission(
                name=name, model_name=model_name,
                record_id=record_id)
            self.permissions.append(p)
            self.query.session.add(p)
            self.query.session.add(self)
        else:
            self.permissions.append(p)
            self.query.session.add(self)

        return p

    def isPersonal(self) -> bool:
        return '_role' in self.name

    def getUsername(self) -> str:
        """Returns username for especial user roles"""
        if self.isPersonal() is False:
            raise ValueError

        return User.query.filter_by(
            username=self.name.split("_role")[0]
        ).first().username

    @classmethod
    def getUserEspecialRole(cls, user: 'User') -> 'Role':
        return cls.query.filter_by(
            name="{}_role".format(user.username)).first()

    @classmethod
    def createUserEspecialRole(cls, user: 'User'):
        rol = "{}_role".format(user.username)
        r = cls.getUserEspecialRole(user)

        if r is None:
            r = Role(
                name=rol,
                description="{} role".format(user.username)
            )
            user.roles.append(r)
            db.session.add(r)
            db.session.add(user)

        return r


@persistence_methods(db)
class Permission(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    # the machine readable permission name
    name = db.Column(db.String(120))
    # the model name if any
    model_name = db.Column(db.String(80))
    # the record id ... empty and the user has access to all record's
    record_id = db.Column(db.String(32))
    # group or role
    role_id = db.Column(db.String(32), db.ForeignKey('role.id'))

    def __repr__(self):
        return "::".join([self.name, self.model_name, self.record_id])


@persistence_methods(db)
class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(254), index=True)
    password_hash = db.Column(db.String(128))
    credit_line = db.Column(db.String(254), default='')
    roles = db.relationship(
        'Role', secondary=user_roles, lazy='select',
        backref=db.backref('users', lazy=True))

    def getUserRole(self):
        """Retorna grupo especial para el usuario"""
        return Role.getUserEspecialRole(self)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password_hash(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.email or self.username)

    def getCreditLine(self):
        return self.credit_line or self.name or self.username


def create_user(
    username: str,
    password: str,
    name='',
    email='',
    credit_line='',
    id=None
) -> User:
    """Crear un usuario"""
    if id is None:
        user = User()
    else:
        user = User(id=id)
    user.name = name
    user.set_password(password)
    user.username = username
    user.email = email
    user.credit_line = credit_line

    # crear grupo especial para el usuario
    user_rol = Role.createUserEspecialRole(user)

    # crear el board personal del usuario
    from newswriter.models import content  # avoid circular import
    user_board = content.Board.createUserBoard(user)
    # assing add user permissions on the board
    for p in BOARD_ALL_PERMS:
        user_rol.addPermission(p, user_board.name, 'board')
    # --

    return user


def password_generator(length=8):
    '''
    Generates a random password having the specified length
    :length -> length of password to be generated. Defaults to 8
        if nothing is specified.
    :returns string <class 'str'>
    '''
    LETTERS = string.ascii_letters
    NUMBERS = string.digits
    PUNCTUATION = string.punctuation

    # create alphanumerical from string constants
    printable = f'{LETTERS}{NUMBERS}{PUNCTUATION}'

    # convert printable from string to list and shuffle
    printable = list(printable)
    random.shuffle(printable)

    # generate random password and convert to string
    random_password = random.choices(printable, k=length)
    random_password = ''.join(random_password)
    return random_password


@identity_loaded.connect
def on_identity_loaded(sender, identity):

    # Set the identity user object
    identity.user = current_user

    if current_user.is_authenticated:
        # Add the UserNeed to the identity
        identity.provides.add(UserNeed(current_user.id))

        # Load the user roles to
        for rol in current_user.roles:
            identity.provides.add(RoleNeed(rol.name))
            # load the user's concrete permissions
            for p in rol.permissions:
                if p.record_id:
                    # permiso concreto sobre un objeto en particular
                    identity.provides.add(
                        ItemNeed(p.name, p.record_id, p.model_name))
                else:
                    # permiso sobre objetos del mismo tipo
                    identity.provides.add(Need(p.name, p.model_name))
            # --
