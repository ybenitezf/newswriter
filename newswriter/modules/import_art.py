"""Importa paquetes

Importar diferentes tipos de paquetes
"""
from newswriter import ma
from marshmallow import fields, validate


# Schemas & validación
class UserSchema(ma.Schema):
    id = fields.Str(required=True, validate=validate.Length(equal=32))
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Email()
    credit_line = fields.Str(missing='')


class BlockData(fields.Field):

    def _deserialize(self, value, attr, data, **kwargs):
        return value

    def _serialize(self, value, attr, obj, **kwargs):
        return ""


class ContentBlockSchema(ma.Schema):
    data = BlockData()
    type = fields.Str(required=True)


class ContentSchema(ma.Schema):
    blocks = fields.List(fields.Nested(ContentBlockSchema))
    time = fields.Int()
    version = fields.Str()


class ArticleSchema(ma.Schema):
    id = fields.Str(required=True, validate=validate.Length(equal=32))
    headline = fields.Str(required=True)
    keywords = fields.List(fields.Str(), required=True)
    credit_line = fields.Str(missing='')
    excerpt = fields.Str(missing='')
    created_on = fields.DateTime(required=True)
    author = fields.Nested(UserSchema, required=True)
    content = fields.Nested(ContentSchema, required=True)
