# NewsWriter

A news redaction app for adelante.cu:

![NewsWriter UI](newswriter.png)

## development

You need `yarn` and `node >= 12`

```bash
git clone https://github.com/ybenitezf/newswriter
cd newswriter
python3 -m venv env
. env/bin/activate
make dev
```

After changes make a new dist release with:

```bash
$ bump2version patch # possible: major / minor / patch
$ git push
$ git push --tags
```

## tests

```bash
make test
```

Or with coverage

```bash
make coverage
```

## Install

```bash
python3 -m venv env
. env/bin/activate
pip install https://github.com/ybenitezf/newswriter/releases/download/v0.0.5/newswriter-0.0.5-py2.py3-none-any.whl
```

You need to configure the instance, either by environment variables or a `.env` file:

- `SECRET_KEY`: application secret key, should be a random string
- `SQLALCHEMY_DATABASE_URI`: the database to use, see [database urls](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls) in SQLAlchemy documentation site. Defaults to SQLite and `appdb.db` in the instance folder
- `UPLOAD_FOLDER`: directory to store the users uploads, should be a full path, defaults to instalce foler + `/uploads`
- `INDEX_BASE_DIR`: directory to store indexing data for the searches

After run the databases upgrade

```bash
flask deploy db-upgrade
```

## Generar instalador

```bash
pyinstaller --onefile --hiddenimport=celery.fixups.django --hiddenimport='celery.fixups' --add-data 'newswriter/templates:newswriter/templates' --add-data 'newswriter/static:newswriter/static' --add-data 'newswriter/migrations:newswriter/migrations' --hiddenimport=newswriter.config newswritercli.py
```
