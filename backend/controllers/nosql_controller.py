"""
nosql_controller.py — Controlador para ejecutar comandos mongosh.
"""

from flask import request, jsonify, current_app
from services.nosql_service import NoSqlService


def _get_service() -> NoSqlService:
    return NoSqlService(current_app.db)


def ejecutar_consulta():
    """
    POST /api/nosql/ejecutar
    Body: { "comando": "db.libros.findOne()" }
    """
    datos = request.get_json(silent=True)
    if not datos or "comando" not in datos:
        return jsonify({"error": "Se requiere el campo 'comando' en el body JSON."}), 400

    comando = datos["comando"].strip()
    if not comando:
        return jsonify({"error": "El comando no puede estar vacío."}), 400

    resultado = _get_service().ejecutar(comando)
    return jsonify(resultado), 200
