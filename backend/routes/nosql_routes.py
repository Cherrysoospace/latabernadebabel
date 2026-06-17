"""
nosql_routes.py — Blueprint de rutas para el panel de consultas NoSQL.

Prefijo registrado en app.py: /api/nosql
"""

from flask import Blueprint
from controllers.nosql_controller import ejecutar_consulta

nosql_bp = Blueprint("nosql", __name__)

nosql_bp.route("/ejecutar", methods=["POST"])(ejecutar_consulta)
