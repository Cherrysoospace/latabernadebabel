"""
prestamo_controller.py — Controlador para la colección 'prestamos'.

Responsabilidades:
    - Recibir los datos del request HTTP.
    - Llamar al PrestamoService con esos datos.
    - Construir y retornar la respuesta JSON con el código HTTP correcto.
    - Capturar errores y retornar mensajes claros al cliente.
"""

from flask import request, jsonify, current_app
from services.prestamo_service import PrestamoService


def _get_service() -> PrestamoService:
    """Obtiene una instancia del service usando la db inyectada en la app."""
    return PrestamoService(current_app.db)


# ── CREATE ────────────────────────────────────────────────────────────────────

def crear_prestamo():
    """
    POST /api/prestamos
    Registra un nuevo préstamo.
    Body requerido: { "usuario_id": "...", "libro_id": "..." }
    Body opcional:  { "dias": 21 }  → sobreescribe la duración por membresía.
    """
    datos = request.get_json(silent=True)
    if not datos:
        return jsonify({"error": "Se esperaba un body JSON válido."}), 400

    if not datos.get("usuario_id") or not datos.get("libro_id"):
        return jsonify({"error": "Se requieren los campos 'usuario_id' y 'libro_id'."}), 400

    try:
        prestamo = _get_service().crear(datos)
        return jsonify({"mensaje": "Préstamo registrado exitosamente.", "prestamo": prestamo}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 422


# ── READ ──────────────────────────────────────────────────────────────────────

def obtener_prestamos():
    """
    GET /api/prestamos
    Retorna lista paginada. Acepta query params:
        ?skip=0&limit=20
        ?usuario_id=xxx  → préstamos de un usuario específico
        ?estado=activo   → filtra por estado (activo | devuelto | vencido)
        ?vencidos=true   → detecta y retorna préstamos vencidos
    """
    service = _get_service()

    usuario_id = request.args.get("usuario_id")
    if usuario_id:
        try:
            return jsonify(service.obtener_por_usuario(usuario_id)), 200
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

    if request.args.get("vencidos") == "true":
        return jsonify(service.obtener_vencidos()), 200

    estado = request.args.get("estado")
    if estado == "activo":
        return jsonify(service.obtener_activos()), 200

    try:
        skip = int(request.args.get("skip", 0))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return jsonify({"error": "Los parámetros 'skip' y 'limit' deben ser enteros."}), 400

    resultado = service.obtener_todos(skip=skip, limit=limit)
    return jsonify({
        "prestamos": resultado["items"],
        "total":     resultado["total"],
        "skip":      resultado["skip"],
        "limit":     resultado["limit"],
    }), 200


def obtener_prestamo(prestamo_id: str):
    """
    GET /api/prestamos/<prestamo_id>
    Retorna el detalle completo de un préstamo por su ID.
    """
    try:
        prestamo = _get_service().obtener_por_id(prestamo_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if prestamo is None:
        return jsonify({"error": f"No se encontró el préstamo con ID '{prestamo_id}'."}), 404

    return jsonify(prestamo), 200


def estadisticas_estados():
    """
    GET /api/prestamos/estadisticas/estados
    Retorna el conteo de préstamos agrupados por estado.
    """
    return jsonify(_get_service().contar_por_estado()), 200


def top_usuarios_prestamos():
    """
    GET /api/prestamos/estadisticas/top-usuarios
    Retorna los usuarios con más préstamos.
    Acepta query param: ?top=5
    """
    try:
        top = int(request.args.get("top", 5))
    except ValueError:
        return jsonify({"error": "El parámetro 'top' debe ser un entero."}), 400

    return jsonify(_get_service().usuarios_con_mas_prestamos(top=top)), 200


# ── UPDATE ────────────────────────────────────────────────────────────────────

def devolver_prestamo(prestamo_id: str):
    """
    PATCH /api/prestamos/<prestamo_id>/devolver
    Procesa la devolución de un préstamo:
        - Cambia estado a 'devuelto'.
        - Registra fecha_devolucion.
        - Marca el libro como disponible.
    """
    try:
        prestamo = _get_service().devolver(prestamo_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    if prestamo is None:
        return jsonify({"error": f"No se encontró el préstamo con ID '{prestamo_id}'."}), 404

    return jsonify({"mensaje": "Libro devuelto exitosamente.", "prestamo": prestamo}), 200


def actualizar_estado_prestamo(prestamo_id: str):
    """
    PATCH /api/prestamos/<prestamo_id>/estado
    Actualiza manualmente el estado de un préstamo.
    Body requerido: { "estado": "activo" | "devuelto" | "vencido" }
    """
    datos = request.get_json(silent=True)
    if not datos or "estado" not in datos:
        return jsonify({"error": "Se requiere el campo 'estado'."}), 400

    try:
        prestamo = _get_service().actualizar_estado(prestamo_id, datos["estado"])
    except ValueError as e:
        return jsonify({"error": str(e)}), 422

    if prestamo is None:
        return jsonify({"error": f"No se encontró el préstamo con ID '{prestamo_id}'."}), 404

    return jsonify({"mensaje": "Estado actualizado.", "prestamo": prestamo}), 200


# ── DELETE ────────────────────────────────────────────────────────────────────

def eliminar_prestamo(prestamo_id: str):
    """
    DELETE /api/prestamos/<prestamo_id>
    Elimina un registro de préstamo por su ID.
    """
    try:
        eliminado = _get_service().eliminar(prestamo_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    if not eliminado:
        return jsonify({"error": f"No se encontró el préstamo con ID '{prestamo_id}'."}), 404

    return jsonify({"mensaje": f"Préstamo '{prestamo_id}' eliminado exitosamente."}), 200
