"""
libro_controller.py — Controlador para la colección 'libros'.

Responsabilidades:
    - Recibir los datos del request HTTP (query params, body, path params).
    - Llamar al LibroService con esos datos.
    - Construir y retornar la respuesta JSON con el código HTTP correcto.
    - Capturar errores y retornar mensajes claros al cliente.
"""

from flask import request, jsonify, current_app
from services.libro_service import LibroService


def _get_service() -> LibroService:
    """Obtiene una instancia del service usando la db inyectada en la app."""
    return LibroService(current_app.db)


# ── CREATE ────────────────────────────────────────────────────────────────────

def crear_libro():
    """
    POST /api/libros
    Crea un nuevo libro con los datos del body JSON.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        libro = _get_service().crear(datos)
        return jsonify({"mensaje": "Libro creado exitosamente.", "libro": libro}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


# ── READ ──────────────────────────────────────────────────────────────────────

def obtener_libros():
    """
    GET /api/libros
    Retorna lista paginada. Acepta query params: ?skip=0&limit=20
    Opcionalmente filtra con ?q=termino para búsqueda, ?genero=xxx, ?disponible=true
    """
    service = _get_service()

    # Filtro de búsqueda por texto
    termino = request.args.get("q")
    if termino:
        return jsonify(service.buscar(termino)), 200

    # Filtro por género
    genero = request.args.get("genero")
    if genero:
        return jsonify(service.obtener_por_genero(genero)), 200

    # Filtro de disponibles
    if request.args.get("disponible") == "true":
        return jsonify(service.obtener_disponibles()), 200

    # Listado paginado general
    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "Los parámetros 'skip' y 'limit' deben ser enteros."}), 400

    return jsonify(service.obtener_todos(skip=skip, limit=limit)), 200


def obtener_libro(libro_id: str):
    """
    GET /api/libros/<libro_id>
    Retorna el detalle completo de un libro por su ID.
    """
    try:
        libro = _get_service().obtener_por_id(libro_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if libro is None:
        return jsonify({"error": f"No se encontró el libro con ID '{libro_id}'."}), 404

    return jsonify(libro), 200


def estadisticas_generos():
    """
    GET /api/libros/estadisticas/generos
    Retorna el conteo de libros agrupados por género.
    """
    return jsonify(_get_service().contar_por_genero()), 200


# ── UPDATE ────────────────────────────────────────────────────────────────────

def actualizar_libro(libro_id: str):
    """
    PUT /api/libros/<libro_id>
    Actualiza los campos enviados en el body JSON.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        libro = _get_service().actualizar(libro_id, datos)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if libro is None:
        return jsonify({"error": f"No se encontró el libro con ID '{libro_id}'."}), 404

    return jsonify({"mensaje": "Libro actualizado exitosamente.", "libro": libro}), 200


def cambiar_disponibilidad(libro_id: str):
    """
    PATCH /api/libros/<libro_id>/disponibilidad
    Cambia únicamente el campo 'disponible'. Body: { "disponible": true|false }
    """
    datos = request.get_json(silent=True)
    if datos is None or "disponible" not in datos:
        return jsonify({"error": "Se requiere el campo 'disponible' (true/false)."}), 400

    try:
        libro = _get_service().cambiar_disponibilidad(libro_id, bool(datos["disponible"]))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if libro is None:
        return jsonify({"error": f"No se encontró el libro con ID '{libro_id}'."}), 404

    return jsonify({"mensaje": "Disponibilidad actualizada.", "libro": libro}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────

def eliminar_libro(libro_id: str):
    """
    DELETE /api/libros/<libro_id>
    Elimina un libro por su ID.
    """
    try:
        eliminado = _get_service().eliminar(libro_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not eliminado:
        return jsonify({"error": f"No se encontró el libro con ID '{libro_id}'."}), 404

    return jsonify({"mensaje": f"Libro '{libro_id}' eliminado exitosamente."}), 200
