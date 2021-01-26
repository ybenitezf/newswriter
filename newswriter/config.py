from dotenv import load_dotenv
import os

# parse .env file if exists
load_dotenv()

class Config(object):
    ENV = 'development'
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'some-secret-of-my-own'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI') or 'appdb.db'
    LOG_TYPE = os.environ.get("LOG_TYPE", "stream")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER') or 'uploads'
    IMAGES_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'gif'}
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True
    }
    APIFAIRY_UI = 'swagger_ui'
    INDEX_BASE_DIR = os.getenv('INDEX_BASE_DIR') or 'myindexes'
    
    # ldap integration
    LDAP_AUTH = (os.getenv('LDAP_AUTH', 'False') == 'True')
    LDAP_HOST = os.getenv('LDAP_HOST', '')
    LDAP_BASE_DN = os.getenv('LDAP_BASE_DN', '')
    LDAP_USER_DN = os.getenv('LDAP_USER_DN', '')
    LDAP_GROUP_DN = os.getenv('LDAP_GROUP_DN', '')
    LDAP_USER_RDN_ATTR = os.getenv('LDAP_USER_RDN_ATTR', '')
    LDAP_USER_LOGIN_ATTR = os.getenv('LDAP_USER_LOGIN_ATTR', '')
    LDAP_BIND_USER_DN = os.getenv('LDAP_BIND_USER_DN', '')
    LDAP_BIND_USER_PASSWORD = os.getenv('LDAP_BIND_USER_PASSWORD', '')
    # --
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    # blueprints
    PHOTOSTORE_ENABLED = True
    DEFAULT_VOL_SIZE = int(os.getenv('DEFAULT_VOL_SIZE', 0)) or 107374182400
    DEFAULT_MEDIA_SIZE = int(os.getenv('DEFAULT_MEDIA_SIZE', 0)) or 4831838208
    # --
    CELERY_ENABLED = (os.getenv('CELERY_ENABLED', 'False') == 'True')
    broker_url = os.getenv('CELERY_BROKER_URL') or 'redis://localhost:6379'
    result_backend = os.getenv('CELERY_RESULT_BACKEND') or None

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/testdb.db'

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv('SECRET_KEY')
