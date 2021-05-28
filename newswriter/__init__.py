from adelacommon.flask_logs import LogSetup
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ldap3_login import LDAP3LoginManager
from flask_principal import Principal
from flask_caching import Cache
from flask_static_digest import FlaskStaticDigest
from flask_menu import register_menu, Menu
from flask_menu.classy import register_flaskview
from flask_wtf import CSRFProtect
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask import Flask, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import pathlib
import os
import datetime
import sys

__version__ = '0.1.0'

logs = LogSetup()
db = SQLAlchemy()
migrate = Migrate()
login_mgr = LoginManager()
ldap_mgr = LDAP3LoginManager()
principal = Principal()
cache = Cache()
flask_statics = FlaskStaticDigest()
apifairy = APIFairy()
ma = Marshmallow()
csrf = CSRFProtect()
# celery = Celery(__name__)
# Breadcrumbs is a subclass of flask_menu.Menu
menu = Menu()


def create_app(config='newswriter.config.Config'):
    """Inicializar la aplicación"""
    if getattr(sys, 'frozen', False):
        # para pyinstaller
        instance_path = os.path.join(os.path.expanduser("~"), "newswriter")
        app = Flask(
            __name__, 
            instance_path=instance_path)
        app.config['PYINSTALLER'] = True
    else:
        app = Flask(__name__)
        app.config['PYINSTALLER'] = False
    app.config.from_object(config)
    if os.getenv('APP_CONFIG') and (not app.config.get('TESTING')):
        app.config.from_object(os.getenv('APP_CONFIG'))

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    if app.config.get('SQLALCHEMY_DATABASE_URI') == 'appdb.db':
        # en dev config sqlite
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(
            os.path.join(app.instance_path, 'appdb.db'))
    if app.config.get('UPLOAD_FOLDER') == 'uploads':
        # en dev crear carpeta para los uploads
        app.config['UPLOAD_FOLDER'] = os.path.join(
            app.instance_path, 'uploads')
        pathlib.Path(os.path.join(app.instance_path, 'uploads')).mkdir(
            parents=True, exist_ok=True)
    if app.config.get('INDEX_BASE_DIR') == 'myindexes':
        # crear directorio para indices
        app.config['INDEX_BASE_DIR'] = os.path.join(
            app.instance_path, 'myindexes')
        pathlib.Path(os.path.join(app.instance_path, 'myindexes')).mkdir(
            parents=True, exist_ok=True)
    # crear directorio para imagenes
    pathlib.Path(
        os.path.join(
            app.config['UPLOAD_FOLDER'], 'images')
        ).mkdir(parents=True, exist_ok=True)
    logs.init_app(app)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1,
        x_prefix=1)

    # inicializar otros plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login_mgr.init_app(app)
    if app.config.get('PYINSTALLER') is True:
        login_mgr.login_message = "Inicie sesión o registrarse"
    else:
        login_mgr.login_message = "Inicie sesión para acceder a esta página"
    if app.config.get('LDAP_AUTH'):
        ldap_mgr.init_app(app)
    principal.init_app(app)
    cache.init_app(app)
    flask_statics.init_app(app)
    ma.init_app(app)
    menu.init_app(app)
    csrf.init_app(app)
    apifairy.init_app(app)

    # the dummy thing
    @app.route("/")
    @register_menu(app, '.', "Inicio")
    def home():
        """Registrar una raiz commun para los menus"""
        return redirect(url_for('default.index'))

    # incluir modulos y rutas
    from newswriter.views.default import default
    from newswriter.views.users import users_bp
    from newswriter.views.admin import admin_role, admin_permissions
    from newswriter.views.admin import admin_boards, AdminLinks
    from newswriter.searchcommands import cmd as search_cmd
    from newswriter.admin_commands import users_cmds
    from adelacommon.deploy import deploy_cmd

    # registrar los blueprints
    app.register_blueprint(default)
    app.register_blueprint(users_bp)
    # admin crud
    AdminLinks.register(app)
    register_flaskview(app, AdminLinks)
    app.register_blueprint(admin_role)
    app.register_blueprint(admin_permissions)
    app.register_blueprint(admin_boards)
    # --
    app.register_blueprint(search_cmd)
    app.register_blueprint(users_cmds)
    app.register_blueprint(deploy_cmd)
    login_mgr.login_view = 'users.login'

    @app.context_processor
    def inject_version():
        return {
            "version": __version__,
            "now": datetime.datetime.now
        }

    @app.before_first_request
    def setupMenus():
        """Crear las entradas virtuales del menu"""
        m = menu.root()

        # actions, para el sidebar, registrar submenus debajo
        # de este menu
        actions = m.submenu("actions")
        actions._external_url = "#!"
        actions._endpoint = None
        actions._text = "NAVBAR"

        # admin menu section
        actions = m.submenu("actions.admin")
        actions._text = "Administración"
        actions._endpoint = None
        actions._external_url = "#!"

    return app

