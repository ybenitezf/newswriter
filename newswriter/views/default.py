from newswriter.modules.editorjs import renderBlock
from newswriter.modules.imagetools import handleImageUpload, handleURL
from newswriter.models.content import Article, ImageModel, Board
from newswriter.models.permissions import ListarArticulosPermission
from newswriter.models.permissions import ActualizarArticulosPermission
from newswriter.models.permissions import PonerArticulosPermission
from newswriter.models.permissions import EnviarArticulosPermission
from newswriter.models import _gen_uuid
from newswriter.forms import UploadArticleForm
from newswriter import filetools, db, csrf
from newswriter.modules.export import export_article
from newswriter.modules.import_art import importItem, NotMetadataInFile
from newswriter.modules.import_art import NewVersionExits, NoAccessToBoard
from flask import Blueprint, render_template, request, current_app
from flask import send_from_directory, url_for, abort, json
from flask import Response, stream_with_context, flash
from flask_login import login_required, current_user
from flask_menu import register_menu, current_menu
import marshmallow.exceptions
from werkzeug.utils import redirect, secure_filename
from urllib.parse import urlparse
from webpreview import OpenGraph
from json.decoder import JSONDecodeError
from pathlib import Path
import datetime
import tempfile
import pathlib
import os
import zipfile

default = Blueprint('default', __name__, url_prefix='/escritorio')


@default.before_app_first_request
def setupMenus():
    # mis entradas en el sidebar
    actions = current_menu.submenu("actions.default")
    actions._text = "Escritorio"
    actions._endpoint = None
    actions._external_url = "#!"


@default.route('/', defaults={"board_name": None})
@default.route('/<board_name>')
@register_menu(default, "actions.default.index", "Mis trabajos")
@login_required
def index(board_name):
    page = request.args.get('page', 1, type=int)
    if board_name is None:
        board = Board.getUserBoard(current_user)
    else:
        board = Board.query.get_or_404(board_name)

        # asegurarse de que el usuario puede leer este board
        if ListarArticulosPermission(board.name).can() is False:
            flash(f"Usted no tiene acceso al board {board_name}")
            return redirect(url_for('.index'))

    articulos = Article.query.filter(
        Article.board_id == board.name).order_by(
            Article.created_on.desc()).paginate(page, per_page=4)

    return render_template(
        'default/index.html',
        results=articulos, board=board,
        is_personal=("_ub" in board.name)
    )


@default.route('/escribir', defaults={"pkid": None})
@default.route('/escribir/<pkid>')
@register_menu(default, "actions.default.write", "Escribir")
@login_required
def write(pkid):
    if pkid is None:
        pkid = _gen_uuid()

    article = Article.query.get(pkid)

    # Si el articulo exite el usuario necesita permisos para modificarlo
    if article:
        if ActualizarArticulosPermission(article.board_id).can() is False:
            flash("Usted no puede hacer cambios")
            return redirect(url_for('.index', board_name=article.board_id))
    # --

    return render_template('default/write.html', pkid=pkid, article=article)


@default.route('/importar', methods=['GET', 'POST'])
@register_menu(default, "actions.default.import_article", "Importar")
@login_required
def import_article():
    """Seleccionar paquete a importar"""
    form = UploadArticleForm()

    if form.validate_on_submit():
        f = form.archive.data
        filename = secure_filename(f.filename)
        fullname = os.path.join(tempfile.mkdtemp(), filename)
        f.save(fullname)

        try:
            art = importItem(
                fullname, current_app.config['UPLOAD_FOLDER'],
                current_user)
            flash("Articulo importado")
            return redirect(url_for(".preview", pkid=art.id))
        except marshmallow.exceptions.ValidationError as e:
            flash(f"Error en el formato del archivo {e}")
        except NoAccessToBoard:
            flash("No tienes permiso para reemplazar el articulo")
            current_app.logger.exception(
                "No tienes permiso para reemplazar el articulo")
        except NewVersionExits as e:
            url = url_for(".preview", pkid=e.article.id)
            current_app.logger.debug(
                f"Ya existe una versión más reciente de ese trabajo: {url}")
        except NotMetadataInFile:
            current_app.logger.exception(
                "No existe el archivo META-INFO.json")
            flash("META-INFO file missing or corruct")
        except zipfile.BadZipFile:
            current_app.logger.exception("Bad zip file")
            flash("El archivo esta corructo")
        except UnicodeDecodeError:
            current_app.logger.exception('MATA-INFO file missing or corruct')
            flash("No se puede leer el archivo")
        except JSONDecodeError:
            flash("No se puede leer el archivo")
            current_app.logger.exception('MATA-INFO file missing or corruct')
        finally:
            current_app.logger.debug("Removing uploaded file")
            filetools.safe_remove(fullname)

    return render_template('default/import_form.html', form=form)


@default.route('/preview/<pkid>')
@login_required
def preview(pkid):
    article = Article.query.get_or_404(pkid)
    return render_template('default/preview.html', article=article)


@default.route('/download/<pkid>')
@login_required
def download_article(pkid):
    article = Article.query.get_or_404(pkid)
    file_name = export_article(article)
    file_handle = open(file_name, 'rb')

    def stream_and_remove():
        yield from file_handle
        file_handle.close()
        os.remove(file_name)

    return Response(
        stream_with_context(stream_and_remove()),
        headers={
            'Content-Type': 'application/zip',
            'Content-Disposition': 'attachment; filename="{}"'.format(
                Path(file_name).name)
        }
    )


@default.route('/assets/images/<filename>')
def uploaded_image(filename):
    folder = os.path.join(
        current_app.config['UPLOAD_FOLDER'], "images")
    return send_from_directory(folder, filename)


@default.route('/assets/<filename>')
def download_attach(filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'], filename)


@default.route('/upload/photoarchive', methods=['POST'])
@login_required
def upload_photoarchive():
    """Upload a photo from photostore"""
    # check if the post request has the file part
    if 'archive' not in request.files:
        current_app.logger.debug("No file in request")
        return {"success": 0}

    # if user does not select file, browser also
    # submit an empty part without filename
    file = request.files['archive']
    if file.filename == '':
        current_app.logger.debug("Empty file name")
        return {"success": 0}

    if file and filetools.allowed_file(file.filename, {'zip'}):
        # process the zip archive here.
        filename = secure_filename(file.filename)
        fullname = os.path.join(tempfile.mkdtemp(), filename)
        file.save(fullname)
        im = None

        workdir = tempfile.TemporaryDirectory()

        try:
            with zipfile.ZipFile(fullname, 'r') as zf:
                if 'META-INFO.json' in zf.namelist():
                    zf.extractall(workdir.name)
                    # import the image here
                    metainfo_file = os.path.join(
                        workdir.name, 'META-INFO.json')
                    image_data = json.load(open(metainfo_file, 'r'))
                    if 'Photo:v1' in image_data.get('version', ''):
                        file_in_package = image_data.get('filename', None)
                        if file_in_package is None:
                            # old package version, don't include the filename
                            # asume a jpeg image
                            image_file = os.path.join(
                                workdir.name, f"{image_data.get('md5')}.jpg")
                        else:
                            image_file = os.path.join(
                                workdir.name, file_in_package)
                        im = handleImageUpload(
                            image_data.get('md5'), image_file, current_user.id,
                            current_app.config['UPLOAD_FOLDER'])
                        if im.store_data is None:
                            im.store_data = json.dumps(image_data)
                        db.session.add(im)
                        db.session.commit()
                        # --
                    else:
                        # not a photo archive or version missing
                        current_app.logger.debug(
                            "not a photo archive or version missing")
                else:
                    # Error in zip file, is this a photostore archive?
                    current_app.logger.debug("Missing archive info file")
        except zipfile.BadZipFile:
            current_app.logger.debug("Bad zip file")
        except UnicodeDecodeError:
            current_app.logger.debug('MATA-INFO file missing or corruct')
        except JSONDecodeError:
            current_app.logger.debug('MATA-INFO file missing or corruct')
        finally:
            # remove temporary files
            current_app.logger.debug("Removing temporary files")
            workdir.cleanup()
            filetools.safe_remove(fullname)

        if im is not None:

            caption = ""
            if isinstance(im.getStoreData().get('excerpt'), dict):
                blocks = im.getStoreData().get('excerpt').get('blocks')
                caption = "".join([d.get('data').get('text') for d in blocks])
            else:
                caption = im.getStoreData().get('excerpt')
            return {
                "success": 1,
                "file": {
                    "url": url_for(
                        'default.uploaded_image',
                        filename=im.filename),
                    "filename": im.filename,
                    "md5sum": im.id,
                    "width": im.width or 0,
                    "height": im.height or 0,
                    "mode": im.orientation or "",
                    "store_data": image_data
                },
                "credit": im.getStoreData().get('credit_line', ''),
                "caption": caption
            }

    current_app.logger.debug("File not allowed")
    return {"success": 0}


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

    if file and filetools.allowed_file(
            file.filename, current_app.config.get('IMAGES_EXTENSIONS')):
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
                    filename=im.filename),
                "filename": im.filename,
                "width": im.width or 0,
                "height": im.height or 0,
                "mode": im.orientation or "",
                "md5sum": im.id,
            },
            "credit": "Foto de {}".format(im.uploader.name)
        }

    current_app.logger.debug("Filename not valid")
    return {"success": 0}


@default.route('/upload-attach', methods=['POST'])
@login_required
@csrf.exempt
def upload_attach():
    """Editor.js AttachesTool backed"""
    # check if the post request has the file part
    if 'file' not in request.files:
        current_app.logger.debug("No file in request")
        return {"success": 0}

    # if user does not select file, browser also
    # submit an empty part without filename
    file = request.files['file']
    if file.filename == '':
        current_app.logger.debug("Empty file name")
        return {"success": 0}

    if file and filetools.allowed_file(
            file.filename, current_app.config.get('ATTACHES_EXTENSIONS')):
        # do the actual thing
        filename = secure_filename(file.filename)
        fullname = os.path.join(
            current_app.config['UPLOAD_FOLDER'], filename)
        file.save(fullname)
        md5sum = filetools.md5(fullname)

        return {
            "success": 1,
            "file": {
                "url": url_for('.download_attach', filename=filename),
                "size": pathlib.Path(fullname).stat().st_size,
                "name": filename,
                "extension": pathlib.Path(fullname).suffix.strip('.'),
                "md5sum": md5sum
            }
        }

    current_app.logger.debug(file.filename)
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
                filename=im.filename),
            "filename": im.filename,
            "width": im.width or 0,
            "height": im.height or 0,
            "mode": im.orientation or "",
            "md5sum": im.id,
        },
        "credit": credit
    }


@default.route('/fetch-link', methods=['GET'])
@login_required
@csrf.exempt
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
            db.session.add(im)
            db.session.commit()
            return {
                'success': 1,
                'meta': {
                    'title': info.title,
                    'description': info.description,
                    'site_name': info.site_name,
                    'image': {
                        'url': url_for(
                            'default.uploaded_image',
                            filename=im.filename),
                        "filename": im.filename,
                        "width": im.width or 0,
                        "height": im.height or 0,
                        "mode": im.orientation or "",
                        'md5sum': im.id
                    }
                }
            }
        except Exception:
            _l.exception("Ocurrio un error procesando el enlace")
            return {'success': 0}

    return {"success": 0}


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
                'creditline': format(current_user.getCreditLine()),
                'summary': '',
                'keywords': [],
                'content': {}
            }
        else:
            # turn article into a json object and return
            return {
                'headline': article.headline,
                'creditline': article.credit_line,
                'keywords': article.keywords,
                'summary': article.excerpt,
                'content': article.getDecodedContent()
            }

    if request.method == 'POST':

        if article is None:
            # this is a new one and request.json['uuid'] is mandatory
            current_app.logger.debug("Creating a new Article")
            try:
                article = Article(
                    id=pkid,
                    headline=request.json['headline'],
                    credit_line=request.json['creditline'],
                    excerpt=request.json['summary'],
                    content=json.dumps(request.json['content']),
                    author_id=current_user.id,
                    board_id=Board.getUserBoard(current_user).name,
                    modified_on=datetime.datetime.utcnow()
                )
                article.keywords = request.json['keywords']
                db.session.add(article)
                db.session.commit()
            except Exception as e:
                current_app.logger.exception("Malo")
                raise e

            return {"success": 1}
        else:
            # save article changes
            if ActualizarArticulosPermission(article.board_id).can():
                current_app.logger.debug(f"Saving article {article.id}")
                article.headline = request.json['headline']
                article.credit_line = request.json['creditline']
                article.excerpt = request.json['summary']
                article.content = json.dumps(request.json['content'])
                article.keywords = request.json['keywords']
                article.modified_on = datetime.datetime.utcnow()
                db.session.add(article)
                db.session.commit()
            else:
                # no tiene permisos para modificiarlo
                return {"success": 0}, 403

            return {"success": 1}

    # something went worng
    return {"success": 0}, 500


@default.route('/boards')
@register_menu(
    default, "actions.default.boards", "Carpetas",
    visible_when=lambda: current_app.config.get('PYINSTALLER', False) is False)
def list_boards():
    """Lista de carpetas accesibles al usuario"""

    board_list = Board.query.all()
    return render_template(
        'default/boards.html',
        board_list=board_list,  # all the boards
        user_board=Board.getUserBoard(current_user)  # user board
    )


@default.route('/move/<artid>', defaults={'board_name': None})
@default.route('/move/<artid>/<board_name>')
def move_article(artid, board_name):
    """Mover trabajo a otro board

    artid: id del articulo a mover
    board_name: board a donde mover el articulo
    """
    article = Article.query.get_or_404(artid)
    source = article.board

    if EnviarArticulosPermission(article.board.name).can() is False:
        flash(f"Usted no puede sacar articules de {article.board.name}")
        return redirect(url_for('.index'))

    if board_name is not None:
        target = Board.query.get_or_404(board_name)
        if PonerArticulosPermission(target.name).can():
            source.articles.remove(article)
            target.articles.append(article)
            db.session.add(source)
            db.session.add(target)
            db.session.add(article)
            db.session.commit()

            # send the user to te source board
            flash(f"Articulo enviado a {target.name}")
            if source == Board.getUserBoard(current_user):
                return redirect(url_for('.index'))

            return redirect(url_for('.index', board_name=source.name))
        else:
            flash(f"Usted no puede mover articulos a {target.name}")
            return redirect(url_for('.index'))

    boards = []
    for b in Board.query.filter(Board.name != source.name).all():
        if PonerArticulosPermission(b.name).can() and (b != Board.getUserBoard(current_user)):
            boards.append(b)

    if len(boards) == 0:
        # no hay ningun board a donde enviar el articulo
        flash("No puedes mover a ninguna carpeta")
        if source == Board.getUserBoard(current_user):
            return redirect(url_for('.index'))

        return redirect(url_for('.index', board_name=source.name))

    return render_template(
        'default/move_article.html', board_list=boards, article=article)


@default.context_processor
def default_processors():
    def imageResolver(id):
        return ImageModel.query.get(id)

    return dict(
        renderBlock=renderBlock,
        imageResolver=imageResolver,
        local_install=(current_app.config.get('PYINSTALLER', False) is True),
        ListarArticulosPermission=ListarArticulosPermission,
        PonerArticulosPermission=PonerArticulosPermission,
        ActualizarArticulosPermission=ActualizarArticulosPermission,
        EnviarArticulosPermission=EnviarArticulosPermission
    )
