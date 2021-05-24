from newswriter.permissions import AdminRolNeed
from flask_principal import Permission, ItemNeed, Need
from typing import Any, List

# Boards
LISTAR_CONTENIDO = 'listar::articulo'
ACTUALIZAR_CONTENIDO = 'actualizar::articulo'
PONER_CONTENIDO = 'poner::articulo'
ENVIAR_CONTENIDO = 'enviar::articulo'
ELIMINAR_CONTENIDO = 'eliminar::articulo'

BOARD_ALL_PERMS = [
    LISTAR_CONTENIDO, ACTUALIZAR_CONTENIDO, PONER_CONTENIDO,
    ELIMINAR_CONTENIDO, ENVIAR_CONTENIDO
]

BOARD_PERMS_DESCRIPTIONS = {
    LISTAR_CONTENIDO: "Listar articulos en el board",
    ACTUALIZAR_CONTENIDO: "Editar articulos en el board",
    PONER_CONTENIDO: "Mover articulos a este board",
    ENVIAR_CONTENIDO: "Mover/sacar articulos desde este board a otro",
    ELIMINAR_CONTENIDO: "Eliminar articulo en el board"
}

# Needs y Permission generales a todos los boards
ActualizarArticulosNeed = Need(ACTUALIZAR_CONTENIDO, 'board')
ListarArticulosNeed = Need(LISTAR_CONTENIDO, 'board')
PonerArticulosNeed = Need(PONER_CONTENIDO, 'board')
EnviarAritulosNeed = Need(ENVIAR_CONTENIDO, 'board')

# Permisos concretos
class ActualizarArticulosPermission(Permission):
    """Permiso para editar un articulo en un Board"""

    def __init__(self, board_name):
        need = ItemNeed(ACTUALIZAR_CONTENIDO, board_name, 'board')
        super().__init__(need, AdminRolNeed, ActualizarArticulosNeed)

class ListarArticulosPermission(Permission):
    """Permiso de ver los articulos en un board"""

    def __init__(self, board_name):
        need = ItemNeed(ACTUALIZAR_CONTENIDO, board_name, 'board')
        super().__init__(need, AdminRolNeed, ListarArticulosNeed)

class PonerArticulosPermission(Permission):
    """Mover articulos a este board"""

    def __init__(self, board_name):
        need = ItemNeed(PONER_CONTENIDO, board_name, 'board')
        super().__init__(need, AdminRolNeed, PonerArticulosNeed)


class EnviarArticulosPermission(Permission):
    """Mover/sacar articulos desde este board a otro"""

    def __init__(self, board_name):
        need = ItemNeed(ENVIAR_CONTENIDO, board_name, 'board')
        super().__init__(need, AdminRolNeed, EnviarAritulosNeed)

class BoardPermissionHelpers(object):

    @classmethod
    def getPermissionLabel(cls, k: str) -> str:
        return BOARD_PERMS_DESCRIPTIONS[k]

    @classmethod
    def getFormChoices(cls) -> List[Any]:
        return [
            (k, cls.getPermissionLabel(k)) for k in BOARD_PERMS_DESCRIPTIONS
        ]
