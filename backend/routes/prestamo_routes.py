"""
prestamo_routes.py — Blueprint de rutas para la colección 'prestamos'.

Prefijo registrado en app.py: /api/prestamos
"""

from flask import Blueprint
from controllers.prestamo_controller import (
    crear_prestamo,
    obtener_prestamos,
    obtener_prestamo,
    devolver_prestamo,
    actualizar_estado_prestamo,
    eliminar_prestamo,
    estadisticas_estados,
    top_usuarios_prestamos,
)

prestamo_bp = Blueprint("prestamos", __name__)

# ── Estadísticas ───────────────────────────────────────────────────────────────
prestamo_bp.route("/estadisticas/estados",      methods=["GET"])(estadisticas_estados)
prestamo_bp.route("/estadisticas/top-usuarios", methods=["GET"])(top_usuarios_prestamos)

# ── Colección ──────────────────────────────────────────────────────────────────
prestamo_bp.route("/", methods=["POST"])(crear_prestamo)
prestamo_bp.route("/", methods=["GET"])(obtener_prestamos)

# ── Documento individual ───────────────────────────────────────────────────────
prestamo_bp.route("/<prestamo_id>",          methods=["GET"])(obtener_prestamo)
prestamo_bp.route("/<prestamo_id>/devolver", methods=["PATCH"])(devolver_prestamo)
prestamo_bp.route("/<prestamo_id>/estado",   methods=["PATCH"])(actualizar_estado_prestamo)
prestamo_bp.route("/<prestamo_id>",          methods=["DELETE"])(eliminar_prestamo)
