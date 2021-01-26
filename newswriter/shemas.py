from newswriter import ma
from newswriter.models.security import User
from newswriter.models.security import Role


class UserSchema(ma.SQLAlchemySchema):

    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    username = ma.auto_field()
    


class RoleSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Role

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()
