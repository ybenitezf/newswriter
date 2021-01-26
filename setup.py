"""
NewsWriter
----------

Para redactar las noticias de adelante.cu
"""
from setuptools import find_packages, setup


setup(
    name='newswriter',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    long_description=__doc__,
    tests_require = ['pytest', 'pytest-cov'],
    install_requires=[
        'Flask',
        'Flask-Migrate',
        'Flask-SQLAlchemy',
        'Flask-Login',
        'Flask-WTF',
        'Flask-Admin',
        'flask-ldap3-login',
        'Flask-Breadcrumbs',
        'Flask-Menu',
        'Flask-Principal',
        'Flask-Caching',
        'Flask-Static-Digest',
        'email-validator',
        'PyMySQL',
        'python-dotenv',
        'webpreview',
        'redis',
        'cryptography',
        'Pillow',
        'IPTCInfo3',
        'apifairy',
        'marshmallow-sqlalchemy',
        'celery',
        'Whoosh'
    ],
)
