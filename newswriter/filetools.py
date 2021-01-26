from flask import current_app
import hashlib
import os

def allowed_file(filename):
    ALLOWED_EXTENSIONS = current_app.config.get('IMAGES_EXTENSIONS')
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def safe_remove(name):
    try:
        os.remove(name)
    except OSError:
        pass
