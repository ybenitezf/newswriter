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
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from celery import Celery
from flask import Flask, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import pathlib
import os
import datetime

__version__ = '0.0.8'

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
celery = Celery(__name__)
# Breadcrumbs is a subclass of flask_menu.Menu
menu = Menu()


def create_app(config='newswriter.config.Config'):
    """Inicializar la aplicación"""
    app = Flask(__name__)
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
    logs.init_app(app)

    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1,
        x_prefix=1)

    # inicializar otros plugins
    db.init_app(app)
    migrate.init_app(app, db)
    login_mgr.init_app(app)
    login_mgr.login_message = "Inicie sesión para acceder a esta página"
    if app.config.get('LDAP_AUTH'):
        ldap_mgr.init_app(app)
    principal.init_app(app)
    cache.init_app(app)
    flask_statics.init_app(app)
    ma.init_app(app)
    menu.init_app(app)
    apifairy.init_app(app)
    if app.config.get('CELERY_ENABLED'):
        init_celery(celery, app)

    # incluir modulos y rutas
    from newswriter.views.default import default
    from newswriter.views.users import users_bp
    from newswriter.searchcommands import cmd as search_cmd
    from newswriter.admin_commands import users_cmds
    from adelacommon.deploy import deploy_cmd

    # registrar los blueprints
    app.register_blueprint(default)
    app.register_blueprint(users_bp)
    app.register_blueprint(search_cmd)
    app.register_blueprint(users_cmds)
    app.register_blueprint(deploy_cmd)
    login_mgr.login_view = 'users.login'

    # the dummy thing
    @app.route("/")
    @register_menu(app, '.', "Inicio")
    def home():
        """Registrar una raiz commun para los menus"""
        return redirect(url_for('default.index'))

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

    return app


def init_celery(instance, app):
    instance.conf.update(app.config)

    class ContextTask(instance.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    instance.Task = ContextTask
