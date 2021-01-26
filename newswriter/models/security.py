from newswriter import db, cache
from newswriter.models import _gen_uuid
from flask_login import UserMixin, current_user
from flask_admin import expose
from flask_principal import Need, identity_loaded, RoleNeed, UserNeed, ItemNeed
from werkzeug.security import generate_password_hash, check_password_hash


user_roles = db.Table(
    'user_roles',
    db.Column(
        'user_id', db.String(32), db.ForeignKey('user.id'), 
        primary_key=True),
    db.Column(
        'role_id', db.String(32), db.ForeignKey('role.id'),
        primary_key=True)
)


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


class Permission(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    # the machine readable permission name
    name = db.Column(db.String(120))
    # the model name if any
    model_name = db.Column(db.String(80))
    # the record id ... empty and the user has access to all record's
    record_id = db.Column(db.String(32))
    # group or role
    role_id =  db.Column(db.String(32), db.ForeignKey('role.id'))

    def __repr__(self):
        return "::".join([self.name, self.model_name, self.record_id])


class User(UserMixin, db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    name = db.Column(db.String(120))
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(254), index=True)
    password_hash = db.Column(db.String(128))
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


def create_user(username:str, password:str, name='', email='') -> User:
    """Crear un usuario"""
    user = User()
    user.name = name
    user.set_password(password)
    user.username = username
    user.email = email
    
    # crear grupo especial para el usuario
    Role.createUserEspecialRole(user)

    return user


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
