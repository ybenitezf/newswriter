"""CLI application for pyinstaller"""
from threading import Timer
from flask_migrate import upgrade
import newswriter
import webbrowser
import os
import logging

_l = logging.getLogger()

def open_browser():
    webbrowser.open('http://127.0.0.1:6847/')

if __name__ == "__main__":
    try:
        app = newswriter.create_app()
        with app.app_context():
            migrations_dir = os.path.join(app.root_path, "migrations")
            upgrade(directory=migrations_dir)
        Timer(1, open_browser).start()
        app.run(port=6847, debug=False, use_reloader=False)
    except Exception as e:
        _l(f"paso algo raro {e}")
        raise e
