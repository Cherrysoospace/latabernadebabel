"""
autor_controller.py — Controlador para la colección 'autores'.

Responsabilidades:
    - Recibir los datos del request HTTP.
    - Llamar al AutorService con esos datos.
    - Construir y retornar la respuesta JSON con el código HTTP correcto.
    - Capturar errores y retornar mensajes claros al cliente.
"""

from flask import request, jsonify, current_app
from services.autor_service import AutorService


def _get_service() -> AutorService:
    """Obtiene una instancia del service usando la db inyectada en la app."""
    return AutorService(current_app.db)


# ── CREATE ────────────────────────────────────────────────────────────────────

def crear_autor():
    """
    POST /api/autores
    Crea un nuevo autor con los datos del body JSON.
    Body requerido: { "nombre": "..." }
    Body opcional:  { "biografia": "...", "nacionalidad": "...",
                      "obras": [...], "premios": [...] }
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        autor = _get_service().crear(datos)
        return jsonify({"mensaje": "Autor creado exitosamente.", "autor": autor}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


# ── READ ──────────────────────────────────────────────────────────────────────

def obtener_autores():
    """
    GET /api/autores
    Retorna lista paginada. Acepta query params:
        ?skip=0&limit=20
        ?q=nombre           → búsqueda parcial por nombre
        ?nacionalidad=xxx   → filtra por nacionalidad exacta
        ?con_premios=true   → solo autores con premios registrados
    """
    service = _get_service()

    termino = request.args.get("q")
    if termino:
        return jsonify(service.buscar_por_nombre(termino)), 200

    nacionalidad = request.args.get("nacionalidad")
    if nacionalidad:
        return jsonify(service.obtener_por_nacionalidad(nacionalidad)), 200

    if request.args.get("con_premios") == "true":
        return jsonify(service.obtener_con_premios()), 200

    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "Los parámetros 'skip' y 'limit' deben ser enteros."}), 400

    resultado = service.obtener_todos(skip=skip, limit=limit)
    return jsonify({
        "autores": resultado["items"],
        "total":   resultado["total"],
        "skip":    resultado["skip"],
        "limit":   resultado["limit"],
    }), 200


def obtener_autor(autor_id: str):
    """
    GET /api/autores/<autor_id>
    Retorna el detalle completo de un autor por su ID.
    """
    try:
        autor = _get_service().obtener_por_id(autor_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if autor is None:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify(autor), 200


def estadisticas_nacionalidades():
    """
    GET /api/autores/estadisticas/nacionalidades
    Retorna el conteo de autores agrupados por nacionalidad.
    """
    return jsonify(_get_service().contar_por_nacionalidad()), 200


def top_autores_obras():
    """
    GET /api/autores/estadisticas/top-obras
    Retorna los autores con más obras registradas.
    Acepta query param: ?top=5
    """
    try:
        top = int(request.args.get("top", 5))
    except ValueError:
        return jsonify({"error": "El parámetro 'top' debe ser un entero."}), 400

    return jsonify(_get_service().autores_con_mas_obras(top=top)), 200


# ── UPDATE ────────────────────────────────────────────────────────────────────

def actualizar_autor(autor_id: str):
    """
    PUT /api/autores/<autor_id>
    Actualiza los campos base del autor (nombre, biografia, nacionalidad).
    Para obras y premios usar los endpoints específicos.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        autor = _get_service().actualizar(autor_id, datos)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if autor is None:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify({"mensaje": "Autor actualizado exitosamente.", "autor": autor}), 200


def agregar_obra(autor_id: str):
    """
    PATCH /api/autores/<autor_id>/obras
    Agrega un título a la lista de obras del autor.
    Body requerido: { "titulo": "..." }
    """
    datos = request.get_json(silent=True)
    if not datos or "titulo" not in datos:
        return jsonify({"error": "Se requiere el campo 'titulo'."}), 400

    try:
        autor = _get_service().agregar_obra(autor_id, datos["titulo"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if autor is None:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify({"mensaje": "Obra agregada exitosamente.", "autor": autor}), 200


def remover_obra(autor_id: str):
    """
    DELETE /api/autores/<autor_id>/obras
    Elimina un título de la lista de obras del autor.
    Body requerido: { "titulo": "..." }
    """
    datos = request.get_json(silent=True)
    if not datos or "titulo" not in datos:
        return jsonify({"error": "Se requiere el campo 'titulo'."}), 400

    try:
        autor = _get_service().remover_obra(autor_id, datos["titulo"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if autor is None:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify({"mensaje": "Obra removida exitosamente.", "autor": autor}), 200


def agregar_premio(autor_id: str):
    """
    PATCH /api/autores/<autor_id>/premios
    Agrega un premio a la lista del autor.
    Body requerido: { "premio": "..." }
    """
    datos = request.get_json(silent=True)
    if not datos or "premio" not in datos:
        return jsonify({"error": "Se requiere el campo 'premio'."}), 400

    try:
        autor = _get_service().agregar_premio(autor_id, datos["premio"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if autor is None:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify({"mensaje": "Premio agregado exitosamente.", "autor": autor}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────

def eliminar_autor(autor_id: str):
    """
    DELETE /api/autores/<autor_id>
    Elimina un autor por su ID.
    """
    try:
        eliminado = _get_service().eliminar(autor_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not eliminado:
        return jsonify({"error": f"No se encontró el autor con ID '{autor_id}'."}), 404

    return jsonify({"mensaje": f"Autor '{autor_id}' eliminado exitosamente."}), 200
