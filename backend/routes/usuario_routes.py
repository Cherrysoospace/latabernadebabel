"""
usuario_routes.py — Blueprint de rutas para la colección 'usuarios'.

Prefijo registrado en app.py: /api/usuarios
"""

from flask import Blueprint
from controllers.usuario_controller import (
    crear_usuario,
    obtener_usuarios,
    obtener_usuario,
    actualizar_usuario,
    desactivar_usuario,
    eliminar_usuario,
    estadisticas_membresias,
)

usuario_bp = Blueprint("usuarios", __name__)

# ── Estadísticas ───────────────────────────────────────────────────────────────
usuario_bp.route("/estadisticas/membresias", methods=["GET"])(estadisticas_membresias)

# ── Colección ──────────────────────────────────────────────────────────────────
usuario_bp.route("/", methods=["POST"])(crear_usuario)
usuario_bp.route("/", methods=["GET"])(obtener_usuarios)

# ── Documento individual ───────────────────────────────────────────────────────
usuario_bp.route("/<usuario_id>",            methods=["GET"])(obtener_usuario)
usuario_bp.route("/<usuario_id>",            methods=["PUT"])(actualizar_usuario)
usuario_bp.route("/<usuario_id>/desactivar", methods=["PATCH"])(desactivar_usuario)
usuario_bp.route("/<usuario_id>",            methods=["DELETE"])(eliminar_usuario)
