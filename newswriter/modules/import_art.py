"""Importa paquetes

Importar diferentes tipos de paquetes
"""
from newswriter import ma, db
from newswriter.schemas import ImageModelExportSchema
from newswriter.models.content import Article, ImageModel
from newswriter.models.security import User, Role, password_generator
from newswriter.models.security import create_user
from flask import current_app, json
from marshmallow import fields, validate
import tempfile
import zipfile
import os
import shutil

# Schemas & validación
class UserSchema(ma.Schema):
    id = fields.Str(required=True, validate=validate.Length(equal=32))
    name = fields.Str(required=True)
    username = fields.Str(required=True)
    email = fields.Email()
    credit_line = fields.Str(missing='')


class BlockData(fields.Field):
    """Generic editorjs block data"""

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


# Errores & excepciones
class NotMetadataInFile(Exception):
    pass

class NewVersionExits(Exception):

    def __init__(self, article: Article) -> None:
        self.article = article
        super().__init__("Existe una versión más reciente")


def importUserInfo(user_data) -> User:
    """Importar información de usuario"""
    # test with id
    u = User.query.get(user_data.get("id"))
    # test with username
    if u is None:
        byusername = User.query.filter(
            (User.username == user_data.get("username"))
        ).first()
        u = None if byusername is None else byusername

    if u:
        # Ya tengo este usuario en la BD
        return u
    else:
        u = create_user(
            user_data["username"], password_generator(),
            name=user_data["name"], 
            email=user_data["email"],
            credit_line=user_data["credit_line"],
            id=user_data.get('id')
        )

    return u


def importImage(filedir: str, importdata: dict, uploads_dir: str) -> None:
    """Import ImageModel data and image file"""
    _l = current_app.logger

    pkid = importdata.get("md5sum")
    im = ImageModel.query.get(pkid)
    if im is None:
        # importarla que no la tengo
        _l.debug(f"Importando imagen nueva {pkid}")

        work_dir = tempfile.TemporaryDirectory()
        zipname = os.path.join(filedir, f"{pkid}.zip")
        try:
            with zipfile.ZipFile(zipname, 'r') as zf:
                zf.extractall(work_dir.name)
                f_name = os.path.join(work_dir.name, 'META-INFO.json')
                with open(f_name) as f:
                    metainfo = json.load(f)
                # validar datos
                metadata = ImageModelExportSchema().load(metainfo)
                # cargar usuario
                usr = importUserInfo(metadata.get("uploader"))
                # copiar la imagen
                src = os.path.join(
                    work_dir.name, metadata.get("filename"))
                r = shutil.copy(src, os.path.join(uploads_dir, "images"))
                _l.debug(f"Copiado {r}")
                # crear el registro
                im = ImageModel(
                    id=metadata.get("id"),
                    filename=metadata.get("filename"),
                    upload_by=usr.id,
                    store_data=json.dumps(metadata.get("store_data")),
                    width=metadata.get("width"),
                    height=metadata.get("height"),
                    orientation=metadata.get("orientation")
                )
                db.session.add(im)
                _l.debug(f"Imagen importada {im.id}")
        finally:
            work_dir.cleanup()
    else:
        _l.debug(f"Ya tenia {im.id}")


def importAttaches(dirname: str, block_data: dict, uploads_dir: str) -> None:
    """Agregar archivo adjunto"""
    _l = current_app.logger
    filename = block_data['file']['name']
    src = os.path.join(dirname, filename)
    dest = shutil.copy(src, uploads_dir)
    _l.debug(f"Imported {filename} to {dest}")


def importItem(filename, uploads_dir):
    _l = current_app.logger

    work_dir = tempfile.TemporaryDirectory()
    _l.debug(f"importing {filename}")

    try:
        with zipfile.ZipFile(filename, 'r') as zf:
            if 'META-INFO.json' in zf.namelist():
                zf.extractall(work_dir.name)
                f_name = os.path.join(work_dir.name, 'META-INFO.json')
                with open(f_name) as f:
                    metainfo = json.load(f)

                # validar la información, ver si es un articulo
                sm = ArticleSchema().load(metainfo)
                # verificar si ya se tiene una copia del articulo
                actual = Article.query.get(sm.get('id'))
                if actual is not None:
                    # ummm el articulo ya estaba, verificar si el que tengo
                    # es más nuevo que el que estoy importando
                    if actual.created_on > sm.get('created_on'):
                        raise NewVersionExits(actual)

                    # actualizar el articulo existente
                    # TODO: ver el tema de los permisos y si esta en un board
                    # ver que el usuario que lo importa tenga permisos en el 
                    # board
                    # --
                    # actualizar el articulo
                    _l.debug(f"actualizando {actual.id}")
                    actual.headline = sm.get("headline")
                    actual.credit_line = sm.get("credit_line")
                    actual.excerpt = sm.get("excerpt")
                    actual.keywords = sm.get("keywords")
                    actual.content = json.dumps(sm.get("content"))
                    # --
                else:
                    art_usr = importUserInfo(sm.get('author'))
                    # importar nuevo articulo
                    _l.debug(f"Importando nuevo articulo {sm.get('id')}")
                    actual = Article()
                    actual.id = sm["id"]
                    actual.headline = sm["headline"]
                    actual.credit_line = sm["credit_line"]
                    actual.excerpt = sm["excerpt"]
                    actual.keywords = sm["keywords"]
                    actual.content = json.dumps(sm["content"])
                    actual.author = art_usr
                
                # importar imagenes en los bloques
                for cb in sm.get('content').get('blocks'):
                    if cb.get("type") in ["image", "photo"]:
                        # importar una imagen
                        importImage(
                            work_dir.name, cb.get("data")['file'],
                            uploads_dir)
                    elif cb.get("type") == "linkTool":
                        importImage(
                            work_dir.name, 
                            cb.get("data")['meta']['image'],
                            uploads_dir)
                    elif cb.get("type") == "attaches":
                        # importar los adjuntos
                        importAttaches(
                            work_dir.name, cb.get("data"),
                            uploads_dir)
                # -- 
                # crear y guardar el articulo
                db.session.add(actual)
                db.session.commit()
                return actual
            else:
                raise NotMetadataInFile
    finally:
        _l.debug(f"Cleaning up {work_dir.name}")
        work_dir.cleanup()

