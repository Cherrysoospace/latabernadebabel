"""
controllers/__init__.py
Exporta todas las funciones de controlador para facilitar su importación en las rutas.
"""

from .libro_controller import (
    crear_libro,
    obtener_libros,
    obtener_libro,
    actualizar_libro,
    cambiar_disponibilidad,
    eliminar_libro,
    estadisticas_generos,
)

from .usuario_controller import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario,
    actualizar_usuario,
    desactivar_usuario,
    eliminar_usuario,
    estadisticas_membresias,
)

from .prestamo_controller import (
    crear_prestamo,
    obtener_prestamos,
    obtener_prestamo,
    devolver_prestamo,
    actualizar_estado_prestamo,
    eliminar_prestamo,
    estadisticas_estados,
    top_usuarios_prestamos,
)

from .resena_controller import (
    crear_resena,
    obtener_resenas,
    obtener_resena,
    actualizar_resena,
    eliminar_resena,
    promedio_libro,
    top_libros_calificados,
)

from .autor_controller import (
    crear_autor,
    obtener_autores,
    obtener_autor,
    actualizar_autor,
    agregar_obra,
    remover_obra,
    agregar_premio,
    eliminar_autor,
    estadisticas_nacionalidades,
    top_autores_obras,
)

from .nosql_controller import (
    ejecutar_consulta,
)

__all__ = [
    # Libros
    "crear_libro", "obtener_libros", "obtener_libro",
    "actualizar_libro", "cambiar_disponibilidad", "eliminar_libro",
    "estadisticas_generos",
    # Usuarios
    "crear_usuario", "obtener_usuarios", "obtener_usuario",
    "actualizar_usuario", "desactivar_usuario", "eliminar_usuario",
    "estadisticas_membresias",
    # Préstamos
    "crear_prestamo", "obtener_prestamos", "obtener_prestamo",
    "devolver_prestamo", "actualizar_estado_prestamo", "eliminar_prestamo",
    "estadisticas_estados", "top_usuarios_prestamos",
    # Reseñas
    "crear_resena", "obtener_resenas", "obtener_resena",
    "actualizar_resena", "eliminar_resena", "promedio_libro",
    "top_libros_calificados",
    # Autores
    "crear_autor", "obtener_autores", "obtener_autor",
    "actualizar_autor", "agregar_obra", "remover_obra",
    "agregar_premio", "eliminar_autor",
    "estadisticas_nacionalidades", "top_autores_obras",
    # NoSQL
    "ejecutar_consulta",
]
