'''CRUD en permisos'''
from newswriter.models import security
from flask_diced import Diced


class PermissionDiced(Diced):
    model = security.Permission

    def index_view_context(self, context):
        def getRole(role_id: str) -> security.Role:
            return security.Role.query.get(role_id)

        context['getRole'] = getRole
        return context
