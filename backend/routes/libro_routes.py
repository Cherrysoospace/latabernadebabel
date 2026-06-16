"""
libro_routes.py — Blueprint de rutas para la colección 'libros'.

Prefijo registrado en app.py: /api/libros
"""

from flask import Blueprint
from controllers.libro_controller import (
    crear_libro,
    obtener_libros,
    obtener_libro,
    actualizar_libro,
    cambiar_disponibilidad,
    eliminar_libro,
    estadisticas_generos,
)

libro_bp = Blueprint("libros", __name__)

# ── Estadísticas (deben ir ANTES de /<libro_id> para evitar conflictos) ───────
libro_bp.route("/estadisticas/generos", methods=["GET"])(estadisticas_generos)

# ── Colección ─────────────────────────────────────────────────────────────────
libro_bp.route("/",          methods=["POST"])(crear_libro)
libro_bp.route("/",          methods=["GET"])(obtener_libros)

# ── Documento individual ──────────────────────────────────────────────────────
libro_bp.route("/<libro_id>",                      methods=["GET"])(obtener_libro)
libro_bp.route("/<libro_id>",                      methods=["PUT"])(actualizar_libro)
libro_bp.route("/<libro_id>/disponibilidad",       methods=["PATCH"])(cambiar_disponibilidad)
libro_bp.route("/<libro_id>",                      methods=["DELETE"])(eliminar_libro)
