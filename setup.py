"""
NewsWriter
----------

News redactor for adelante.cu
"""
from setuptools import find_packages, setup
import os


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='newswriter',
    version='0.0.4',
    url='https://github.com/ybenitezf/newswriter',
    license='GPL',
    author='Yoel Benítez Fonseca',
    author_email='ybenitezf@gmail.com',
    description='News redactor for adelante.cu',
    long_description=read('README.md'),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    setup_requires=['pytest-runner'],
    tests_require=[
        'pytest', 
        'pytest-cov'
    ],
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
        'Whoosh',
        'adelacommon @ https://github.com/ybenitezf/adela-common/archive/v0.0.2.tar.gz'
    ],
    classifiers=[
        'Environment :: Web Environment', 
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent', 
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary',
    ]
)
