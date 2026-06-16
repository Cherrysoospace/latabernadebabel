"""
autor_routes.py — Blueprint de rutas para la colección 'autores'.

Prefijo registrado en app.py: /api/autores
"""

from flask import Blueprint
from controllers.autor_controller import (
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

autor_bp = Blueprint("autores", __name__)

# ── Estadísticas ───────────────────────────────────────────────────────────────
autor_bp.route("/estadisticas/nacionalidades", methods=["GET"])(estadisticas_nacionalidades)
autor_bp.route("/estadisticas/top-obras",      methods=["GET"])(top_autores_obras)

# ── Colección ──────────────────────────────────────────────────────────────────
autor_bp.route("/", methods=["POST"])(crear_autor)
autor_bp.route("/", methods=["GET"])(obtener_autores)

# ── Documento individual ───────────────────────────────────────────────────────
autor_bp.route("/<autor_id>",         methods=["GET"])(obtener_autor)
autor_bp.route("/<autor_id>",         methods=["PUT"])(actualizar_autor)
autor_bp.route("/<autor_id>",         methods=["DELETE"])(eliminar_autor)

# ── Gestión de listas (obras y premios) ────────────────────────────────────────
autor_bp.route("/<autor_id>/obras",   methods=["PATCH"])(agregar_obra)
autor_bp.route("/<autor_id>/obras",   methods=["DELETE"])(remover_obra)
autor_bp.route("/<autor_id>/premios", methods=["PATCH"])(agregar_premio)
