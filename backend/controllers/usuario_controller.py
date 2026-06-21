"""
usuario_controller.py — Controlador para la colección 'usuarios'.

Responsabilidades:
    - Recibir los datos del request HTTP.
    - Llamar al UsuarioService con esos datos.
    - Construir y retornar la respuesta JSON con el código HTTP correcto.
    - Capturar errores y retornar mensajes claros al cliente.
"""

from flask import request, jsonify, current_app
from services.usuario_service import UsuarioService


def _get_service() -> UsuarioService:
    """Obtiene una instancia del service usando la db inyectada en la app."""
    return UsuarioService(current_app.db)


# ── CREATE ────────────────────────────────────────────────────────────────────

def crear_usuario():
    """
    POST /api/usuarios
    Crea un nuevo usuario con los datos del body JSON.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        usuario = _get_service().crear(datos)
        return jsonify({"mensaje": "Usuario creado exitosamente.", "usuario": usuario}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


# ── READ ──────────────────────────────────────────────────────────────────────

def obtener_usuarios():
    """
    GET /api/usuarios
    Retorna lista paginada. Acepta query params:
        ?skip=0&limit=20
        ?correo=xxx       → busca por correo exacto
        ?membresia=xxx    → filtra por tipo de membresía
        ?activos=true     → solo usuarios activos
    """
    service = _get_service()

    correo = request.args.get("correo")
    if correo:
        usuario = service.obtener_por_correo(correo)
        if not usuario:
            return jsonify({"error": f"No se encontró usuario con correo '{correo}'."}), 404
        return jsonify(usuario), 200

    membresia = request.args.get("membresia")
    if membresia:
        return jsonify(service.obtener_por_membresia(membresia)), 200

    if request.args.get("activos") == "true":
        return jsonify(service.obtener_activos()), 200

    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "Los parámetros 'skip' y 'limit' deben ser enteros."}), 400

    resultado = service.obtener_todos(skip=skip, limit=limit)
    return jsonify({
        "usuarios": resultado["items"],
        "total":    resultado["total"],
        "skip":     resultado["skip"],
        "limit":    resultado["limit"],
    }), 200


def obtener_usuario(usuario_id: str):
    """
    GET /api/usuarios/<usuario_id>
    Retorna el detalle completo de un usuario por su ID.
    """
    try:
        usuario = _get_service().obtener_por_id(usuario_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if usuario is None:
        return jsonify({"error": f"No se encontró el usuario con ID '{usuario_id}'."}), 404

    return jsonify(usuario), 200


def estadisticas_membresias():
    """
    GET /api/usuarios/estadisticas/membresias
    Retorna el conteo de usuarios agrupados por membresía.
    """
    return jsonify(_get_service().contar_por_membresia()), 200


# ── UPDATE ────────────────────────────────────────────────────────────────────

def actualizar_usuario(usuario_id: str):
    """
    PUT /api/usuarios/<usuario_id>
    Actualiza los campos enviados en el body JSON.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        usuario = _get_service().actualizar(usuario_id, datos)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if usuario is None:
        return jsonify({"error": f"No se encontró el usuario con ID '{usuario_id}'."}), 404

    return jsonify({"mensaje": "Usuario actualizado exitosamente.", "usuario": usuario}), 200


def desactivar_usuario(usuario_id: str):
    """
    PATCH /api/usuarios/<usuario_id>/desactivar
    Realiza un soft-delete del usuario (activo = False).
    """
    try:
        usuario = _get_service().desactivar(usuario_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if usuario is None:
        return jsonify({"error": f"No se encontró el usuario con ID '{usuario_id}'."}), 404

    return jsonify({"mensaje": "Usuario desactivado.", "usuario": usuario}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────

def eliminar_usuario(usuario_id: str):
    """
    DELETE /api/usuarios/<usuario_id>
    Elimina permanentemente un usuario por su ID.
    """
    try:
        eliminado = _get_service().eliminar(usuario_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not eliminado:
        return jsonify({"error": f"No se encontró el usuario con ID '{usuario_id}'."}), 404

    return jsonify({"mensaje": f"Usuario '{usuario_id}' eliminado exitosamente."}), 200
