from newswriter import celery, db
from whoosh.searching import Hit, ResultsPage
from whoosh.filedb.filestore import FileStorage
from flask import current_app

def index_document(indice: str, data: dict):
    store = FileStorage(indice)
    ix = store.open_index()
    current_app.logger.debug('Writing {} to {}'.format(data, indice))
    with ix.writer() as writer:
        writer.update_document(**data)

@celery.task
def index_document_async(*args, **kwargs):
    index_document(*args, **kwargs)


class PaginaBusqueda(object):

    def __init__(self, results: ResultsPage):
        self._res = results
        self._objects = []
        if self.is_empty() is False:
            self._objects = self._getObjectsFromResults()
        self.pagenum = self._res.pagenum

    def next(self):       
        return self.pagenum + 1 if self.has_next() else self.pagenum
    
    def prev(self):
        return self.pagenum - 1  if self.has_prev() else self.pagenum

    def is_empty(self):
        return self._res.results.is_empty()

    def groups(self, name=None):
        return self._res.results.groups(name=name)

    def has_next(self):
        return self._res.is_last_page() is False

    def has_prev(self):
        return self.pagenum > 1

    def getObjects(self):
        return self._objects

    def _getObjectFromResult(self, hit: Hit):
        return self.getObjectModel().query.get(
            hit.get(self.getObjectIdentifier()))

    def _getObjectsFromResults(self):
        return [self._getObjectFromResult(r) for r in self._res]

    def getObjectIdentifier(self) -> 'str':
        """Atributo en los resultados que identifica al objeto
        
        Para poder ser usando en getObjectsFromResults
        """
        raise NotImplementedError

    def getObjectModel(self) -> db.Model:
        """Retorna el modelo base"""
        raise NotImplementedError
