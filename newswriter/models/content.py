"""Content related models"""
from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from newswriter import db
from newswriter.models import _gen_uuid
from newswriter.models.security import User
from datetime import datetime
import json

class Board(db.Model):
    name = db.Column(db.String(60), primary_key=True)
    articles = db.relationship('Article', backref='board', lazy=True)

    @classmethod
    def getUserBoard(cls, user: User) -> 'Board':
        return Board.query.filter_by(name=f"{user.username}_ub").first()

    @classmethod
    def createUserBoard(cls, user: User):
        b = cls.getUserBoard(user)
        if b is None:
            b = Board(name=f"{user.username}_ub")
            db.session.add(b)

        return b


class IsInComparator(Comparator):

    def contains(self, other, **kwargs):
        return self.__clause_element__().contains(other)


class Article(db.Model):
    id = db.Column(db.String(32), primary_key=True, default=_gen_uuid)
    headline = db.Column(db.String(512), default='')
    _kws = db.Column('keywords', db.Text(), default='')
    credit_line = db.Column(db.String(160), default='')
    excerpt = db.Column(db.Text(), default='')
    content = db.Column(db.Text(), default='')
    board_id = db.Column(
        db.String(60), db.ForeignKey('board.name'), nullable=True)
    created_on = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    modified_on = db.Column(db.DateTime)
    author_id = db.Column(
        db.String(32), db.ForeignKey('user.id'), nullable=True)
    author = db.relationship('User', lazy=True)

    def getDecodedContent(self):
        if not hasattr(self, '_decodedcontent'):
            self._decodedcontent = json.loads(self.content)
        return self._decodedcontent

    def getFirstTextBlock(self):
        blocks = self.getDecodedContent().get('blocks')
        if blocks is None:
            return ""

        for block in blocks:
            if block.get('type') == 'paragraph':
                if block.get('data'):
                    return block.get('data').get('text')

        return ""

    @hybrid_property
    def keywords(self):
        if self._kws is not None:
            return self._kws.split('|')
        
        return []
    
    @keywords.setter
    def keywords(self, value):
        self._kws = '|'.join(value)


    @keywords.comparator
    def keywords(cls):
        return IsInComparator(cls._kws)


class ImageModel(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    filename = db.Column(db.Text())
    upload_by = db.Column(
        db.String(32), db.ForeignKey('user.id'), nullable=True)
    uploader = db.relationship('User', lazy=True)
    store_data = db.Column(db.Text(), default='')
    width = db.Column(db.Integer(), default=0)
    height = db.Column(db.Integer(), default=0)
    orientation = db.Column(db.String(10), default='cuadrada')

    def getStoreData(self) -> dict:
        if self.store_data:
            return json.loads(self.store_data)
        
        return {}
