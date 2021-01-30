from flask import Blueprint, current_app
from pathlib import Path

cmd = Blueprint('index', __name__)


@cmd.cli.command('create')
def create():
    """Crea los indices de whoosh"""
    base = Path(current_app.config.get('INDEX_BASE_DIR'))
    base.mkdir(
        parents=True, exist_ok=True)


@cmd.cli.command('reindex')
def reindex():
    """Indexar todos los objetos"""
    pass
