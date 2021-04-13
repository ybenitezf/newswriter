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
