from newswriter import ma
from newswriter.models.security import User
from newswriter.models.security import Role
from newswriter.models.content import Article
from newswriter.models.content import ImageModel
from marshmallow import fields


class UserSchema(ma.SQLAlchemySchema):

    class Meta:
        model = User

    id = ma.auto_field()
    name = ma.auto_field()
    username = ma.auto_field()
    email = ma.auto_field()
    credit_line = ma.auto_field()
    


class RoleSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Role

    id = ma.auto_field()
    name = ma.auto_field()
    description = ma.auto_field()


class ArticleExportSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Article

    id = ma.auto_field()
    headline = ma.auto_field()
    keywords = fields.Method('get_keywords')
    credit_line = ma.auto_field()
    excerpt = ma.auto_field()
    content = fields.Method('get_content')
    created_on = ma.auto_field()
    modified_on = ma.auto_field()
    author = fields.Nested(UserSchema)

    def get_keywords(self, obj: Article):
        return obj.keywords

    def get_content(self, obj: Article):
        return obj.getDecodedContent()


class ImageModelExportSchema(ma.SQLAlchemySchema):
    
    class Meta:
        model = ImageModel

    id = ma.auto_field()
    filename = ma.auto_field()
    uploader = fields.Nested(UserSchema)
    store_data = fields.Method(
        'serialize_photostore', 
        deserialize='deserialize_photostore')
    width = ma.auto_field()
    height = ma.auto_field()
    orientation = ma.auto_field()

    def serialize_photostore(self, obj: ImageModel):
        return obj.getStoreData()

    def deserialize_photostore(self, value):
        return value
