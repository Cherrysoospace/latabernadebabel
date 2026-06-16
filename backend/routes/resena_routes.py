"""
resena_routes.py — Blueprint de rutas para la colección 'resenas'.

Prefijo registrado en app.py: /api/resenas
"""

from flask import Blueprint
from controllers.resena_controller import (
    crear_resena,
    obtener_resenas,
    obtener_resena,
    actualizar_resena,
    eliminar_resena,
    promedio_libro,
    top_libros_calificados,
)

resena_bp = Blueprint("resenas", __name__)

# ── Estadísticas ───────────────────────────────────────────────────────────────
resena_bp.route("/estadisticas/top-libros",    methods=["GET"])(top_libros_calificados)
resena_bp.route("/promedio/<libro_id>",        methods=["GET"])(promedio_libro)

# ── Colección ──────────────────────────────────────────────────────────────────
resena_bp.route("/", methods=["POST"])(crear_resena)
resena_bp.route("/", methods=["GET"])(obtener_resenas)

# ── Documento individual ───────────────────────────────────────────────────────
resena_bp.route("/<resena_id>", methods=["GET"])(obtener_resena)
resena_bp.route("/<resena_id>", methods=["PUT"])(actualizar_resena)
resena_bp.route("/<resena_id>", methods=["DELETE"])(eliminar_resena)
