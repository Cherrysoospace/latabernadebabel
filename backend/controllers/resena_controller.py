"""
resena_controller.py — Controlador para la colección 'resenas'.

Responsabilidades:
    - Recibir los datos del request HTTP.
    - Llamar al ResenaService con esos datos.
    - Construir y retornar la respuesta JSON con el código HTTP correcto.
    - Capturar errores y retornar mensajes claros al cliente.
"""

from flask import request, jsonify, current_app
from services.resena_service import ResenaService


def _get_service() -> ResenaService:
    """Obtiene una instancia del service usando la db inyectada en la app."""
    return ResenaService(current_app.db)


# ── CREATE ────────────────────────────────────────────────────────────────────

def crear_resena():
    """
    POST /api/resenas
    Crea una nueva reseña.
    Body requerido: { "usuario_id": "...", "libro_id": "...", "calificacion": 1-5 }
    Body opcional:  { "comentario": "..." }
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    campos_requeridos = ["usuario_id", "libro_id", "calificacion"]
    faltantes = [c for c in campos_requeridos if c not in datos]
    if faltantes:
        return jsonify({"error": f"Campos requeridos faltantes: {faltantes}"}), 400

    try:
        resena = _get_service().crear(datos)
        return jsonify({"mensaje": "Reseña creada exitosamente.", "resena": resena}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


# ── READ ──────────────────────────────────────────────────────────────────────

def obtener_resenas():
    """
    GET /api/resenas
    Retorna lista paginada. Acepta query params:
        ?skip=0&limit=20
        ?libro_id=xxx         → reseñas de un libro específico
        ?usuario_id=xxx       → reseñas de un usuario específico
        ?calificacion_min=4   → reseñas con calificación >= N
    """
    service = _get_service()

    libro_id = request.args.get("libro_id")
    if libro_id:
        try:
            return jsonify(service.obtener_por_libro(libro_id)), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    usuario_id = request.args.get("usuario_id")
    if usuario_id:
        try:
            return jsonify(service.obtener_por_usuario(usuario_id)), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    cal_min = request.args.get("calificacion_min")
    if cal_min:
        try:
            return jsonify(service.obtener_por_calificacion_minima(int(cal_min))), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 100))
    except ValueError:
        return jsonify({"error": "Los parámetros 'skip' y 'limit' deben ser enteros."}), 400

    return jsonify(service.obtener_todos(skip=skip, limit=limit)), 200


def obtener_resena(resena_id: str):
    """
    GET /api/resenas/<resena_id>
    Retorna el detalle completo de una reseña por su ID.
    """
    try:
        resena = _get_service().obtener_por_id(resena_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if resena is None:
        return jsonify({"error": f"No se encontró la reseña con ID '{resena_id}'."}), 404

    return jsonify(resena), 200


def promedio_libro(libro_id: str):
    """
    GET /api/resenas/promedio/<libro_id>
    Retorna el promedio de calificación y total de reseñas de un libro.
    """
    try:
        resultado = _get_service().promedio_calificacion_libro(libro_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(resultado), 200


def top_libros_calificados():
    """
    GET /api/resenas/estadisticas/top-libros
    Retorna los libros mejor calificados.
    Acepta query param: ?top=5
    """
    try:
        top = int(request.args.get("top", 5))
    except ValueError:
        return jsonify({"error": "El parámetro 'top' debe ser un entero."}), 400

    return jsonify(_get_service().libros_mejor_calificados(top=top)), 200


# ── UPDATE ────────────────────────────────────────────────────────────────────

def actualizar_resena(resena_id: str):
    """
    PUT /api/resenas/<resena_id>
    Actualiza la calificación o el comentario de una reseña.
    Body: { "calificacion": 4 } y/o { "comentario": "Nuevo texto..." }
    Marca automáticamente editada=True y registra fecha_edicion.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    try:
        resena = _get_service().actualizar(resena_id, datos)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    if resena is None:
        return jsonify({"error": f"No se encontró la reseña con ID '{resena_id}'."}), 404

    return jsonify({"mensaje": "Reseña actualizada exitosamente.", "resena": resena}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────

def eliminar_resena(resena_id: str):
    """
    DELETE /api/resenas/<resena_id>
    Elimina una reseña por su ID.
    """
    try:
        eliminado = _get_service().eliminar(resena_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not eliminado:
        return jsonify({"error": f"No se encontró la reseña con ID '{resena_id}'."}), 404

    return jsonify({"mensaje": f"Reseña '{resena_id}' eliminada exitosamente."}), 200
