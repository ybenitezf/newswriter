from newswriter.modules.editorjs import renderBlock
from newswriter.modules.imagetools import handleImageUpload, handleURL
from newswriter.modules.imagetools import handleFromPhotoStore
from newswriter.models.content import Article
from newswriter.models import _gen_uuid
from newswriter import filetools, db
from flask import Blueprint, render_template, request, current_app
from flask import send_from_directory, url_for, abort, json
from flask_login import login_required, current_user
from flask_breadcrumbs import register_breadcrumb
from flask_menu import register_menu, current_menu
from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from webpreview import OpenGraph
import tempfile
import os
import re


default = Blueprint('default', __name__, url_prefix='/escritorio')

@default.before_app_first_request
def setupMenus():
    # mis entradas en el navbar
    navbar = current_menu.submenu("navbar.default")
    navbar._external_url = "#!"
    navbar._endpoint = None
    navbar._text = "NAVBAR"

    # mis entradas en el sidebar
    actions = current_menu.submenu("actions.default")
    actions._text = "Escritorio"
    actions._endpoint = None
    actions._external_url = "#!"

@default.route('/')
@register_breadcrumb(default, '.', 'Mis trabajos')
@register_menu(default, "navbar.default.index", "Mis trabajos")
@register_menu(default, "actions.default.index", "Mis trabajos")
@login_required
def index():
    page = request.args.get('page', 1, type=int)

    articulos = Article.query.filter(
        Article.author_id == current_user.id).order_by(
            Article.created_on.desc()).paginate(page, per_page=4)

    return render_template(
        'default/index.html', results=articulos)


@default.route('/escribir', defaults={"pkid": None})
@default.route('/escribir/<pkid>')
@register_breadcrumb(default, '.write', 'Escribir')
@register_menu(default, "actions.default.write", "Escribir")
@login_required
def write(pkid):
    if pkid is None:
        pkid = _gen_uuid()

    article = Article.query.get(pkid)

    return render_template('default/write.html', pkid=pkid, article=article)


@default.route('/assets/images/<filename>')
def uploaded_image(filename):
    folder = os.path.join(
        current_app.config['UPLOAD_FOLDER'], "images")
    return send_from_directory(folder, filename)


def processInternalPhoto(p, photo_data):
    # ok, this is an internal image
    _l = current_app.logger.debug

    _l("ok, this is an internal image")
    try:
        im = handleFromPhotoStore(
            p.md5, p.fspath, 
            current_app.config['UPLOAD_FOLDER'])
        if not im.upload_by:
            im.upload_by = p.upload_by
        if not im.store_data:
            im.store_data = json.dumps(photo_data)
        db.session.add(im)
        db.session.commit()
    except Exception:
        current_app.logger.exception(
            "Error proccessing {}".format(p.md5))
        return {"success": 0}

    return {
        "success": 1,
        "file": {
            "url": url_for(
                'default.uploaded_image', 
                filename=im.filename, 
                _external=True),
            "md5sum": p.md5,
            "photostore": photo_data
        },
        "credit": p.credit_line,
        "caption": render_template(
            'photostore/editorjs/photo_excerpt.html',
            data=photo_data.get('excerpt'),
            block_renderer=renderBlock
        )
    }


@default.route('/upload-image', methods=['POST'])
@login_required
def upload_image():
    """Handler editorjs images"""

    # check if the post request has the file part
    if 'image' not in request.files:
        current_app.logger.debug("No file in request")
        return {"success": 0}

    # if user does not select file, browser also
    # submit an empty part without filename
    file = request.files['image']
    if file.filename == '':
        current_app.logger.debug("Empty file name")
        return {"success": 0}

    if file and filetools.allowed_file(file.filename):
        # do the actual thing
        filename = secure_filename(file.filename)
        fullname = os.path.join(tempfile.mkdtemp(), filename)
        file.save(fullname)
        md5sum = filetools.md5(fullname)

        im = handleImageUpload(
            md5sum, fullname, current_user.id, 
            current_app.config['UPLOAD_FOLDER'])
        db.session.add(im)
        db.session.commit()
        # remove temporary file
        filetools.safe_remove(fullname)

        return {
            "success": 1,
            "file": {
                "url": url_for(
                    'default.uploaded_image', 
                    filename=im.filename, 
                    _external=True),
                "md5sum": im.id,
            },
            "credit": "Foto de {}".format(im.uploader.name)
        }
    
    current_app.logger.debug("Filename not valid")
    return {"success": 0}


@default.route('/fetch-image', methods=['POST'])
@login_required
def fetch_image():
    """Download & handle images urls from editorjs"""
    if 'url' not in request.json:
        return {"success": 0}

    url = request.json['url']
    _l = current_app.logger.debug
    _l("Handling: {}".format(url))

    # try to get the remote image, not internal
    # extract the hostname from url
    if urlparse(url).netloc:
        credit = "Tomada de {}".format(urlparse(url).netloc)
    else:
        credit = "Tomada de Internet"

    try:
        im = handleURL(url, current_user.id, 
            current_app.config['UPLOAD_FOLDER'])
        db.session.add(im)
        db.session.commit()
    except Exception:
        current_app.logger.exception(
            "Can't get the url {}".format(url))
        return {"success": 0}

    return {
        "success": 1,
        "file": {
            "url": url_for(
                'default.uploaded_image', 
                filename=im.filename, 
                _external=True),
            "md5sum": im.id,
        },
        "credit": credit
    }


@default.route('/fetch-link', methods=['GET'])
@login_required
def fetch_link():
    _l = current_app.logger
    if request.args.get('url'):
        url = request.args.get('url')
        try:
            _l.debug("Retrieving: {}".format(url))
            info = OpenGraph(
                url, [
                    'og:title', 'og:description', 'og:image', 'og:site_name'])
            im = handleURL(
                info.image, current_user.id, 
                current_app.config['UPLOAD_FOLDER'])
            return {
                'success': 1,
                'meta': {
                    'title': info.title,
                    'description': info.description,
                    'site_name': info.site_name,
                    'image': {
                        'url': url_for(
                            'default.uploaded_image', 
                            filename=im.filename, 
                            _external=True),
                        'md5sum': im.id
                    }
                }
            }
        except Exception:
            _l.exception("Ocurrio un error procesando el enlace")
            return {'success': 0}

    return {"success" : 0}


@default.route('/article/<pkid>', methods=['GET', 'POST'])
@login_required
def articleEndPoint(pkid):
    if len(pkid) != 32:
        # bad request
        abort(400)

    article = Article.query.get(pkid)

    if request.method == 'GET':
        if article is None:
            # this is a new one, just generate de defaults
            # --
            return {
                'headline': '',
                'creditline': 'Por {}'.format(current_user.name),
                'keywords': [],
                'content': {}
            }
        else:
            # turn article into a json object and return
            return {
                'headline': article.headline,
                'creditline': article.credit_line,
                'keywords': article.keywords,
                'content': article.getDecodedContent()
            }

    if request.method == 'POST':
        if article is None:
            # this is a new one and request.json['uuid'] is mandatory
            current_app.logger.debug("Creating a new Article")
            article = Article(
                headline=request.json['headline'],
                credit_line=request.json['creditline'],
                content=json.dumps(request.json['content']),
                author_id=current_user.id,
            )
            article.keywords = request.json['keywords']
            db.session.add(article)
            db.session.commit()

            return {"success": 1}
        else:
            # save article changes
            current_app.logger.debug("Saving article {}".format(article.id))
            article.headline = request.json['headline']
            article.credit_line = request.json['creditline']
            article.content = json.dumps(request.json['content'])
            article.keywords = request.json['keywords']
            db.session.add(article)
            db.session.commit()

            return {"success": 1}

    # something went worng
    return {"success": 0}, 500
