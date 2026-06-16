"""
resena_service.py — Lógica de negocio para la colección 'resenas'.

Responsabilidades:
    - Operaciones CRUD sobre la colección 'resenas'.
    - Regla: un usuario solo puede tener una reseña por libro.
    - Consultas: reseñas por libro, por usuario, filtro por calificación.
    - Cálculo del promedio de calificaciones de un libro.
    - Validación de modelo antes de persistir.
"""

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from models.resena_model import Resena
from models.libro_model import Libro
from models.usuario_model import Usuario


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _to_object_id(id_str: str) -> ObjectId:
    """Convierte un string a ObjectId. Lanza ValueError si es inválido."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"ID inválido: '{id_str}'")


def _serializar(doc: dict) -> dict:
    """Convierte ObjectId a string para que Flask pueda serializar a JSON."""
    if doc:
        for campo in ("_id", "usuario_id", "libro_id"):
            if campo in doc and isinstance(doc[campo], ObjectId):
                doc[campo] = str(doc[campo])
    return doc


# ─── Service ──────────────────────────────────────────────────────────────────

class ResenaService:
    """
    Capa de servicio para la colección 'resenas'.
    Recibe la instancia de base de datos (db) inyectada desde la app Flask.
    """

    def __init__(self, db: Database):
        self.col = db[Resena.COLECCION]
        self.col_libros = db[Libro.COLECCION]
        self.col_usuarios = db[Usuario.COLECCION]

    # ── CREATE ────────────────────────────────────────────────────────────────

    def crear(self, datos: dict) -> dict:
        """
        Crea una nueva reseña aplicando las siguientes reglas:
            1. Verifica que el libro exista.
            2. Verifica que el usuario exista y esté activo.
            3. Impide que el mismo usuario reseñe el mismo libro más de una vez.

        Args:
            datos: Debe contener 'usuario_id', 'libro_id' y 'calificacion'.
                   Opcionalmente 'comentario'.

        Returns:
            El documento de la reseña insertado.

        Raises:
            ValueError: Si no se cumplen las reglas de negocio.
        """
        usuario_oid = _to_object_id(datos.get("usuario_id", ""))
        libro_oid = _to_object_id(datos.get("libro_id", ""))

        # 1. Verificar que el libro existe
        if not self.col_libros.find_one({"_id": libro_oid}):
            raise ValueError("El libro especificado no existe.")

        # 2. Verificar que el usuario existe y está activo
        usuario = self.col_usuarios.find_one({"_id": usuario_oid})
        if not usuario:
            raise ValueError("El usuario especificado no existe.")
        if not usuario.get("activo", False):
            raise ValueError("La cuenta del usuario no está activa.")

        # 3. Un usuario solo puede dejar una reseña por libro
        if self.col.find_one({"usuario_id": usuario_oid, "libro_id": libro_oid}):
            raise ValueError("Este usuario ya tiene una reseña para este libro.")

        resena = Resena(
            usuario_id=usuario_oid,
            libro_id=libro_oid,
            calificacion=datos.get("calificacion"),
            comentario=datos.get("comentario"),
        )

        errores = resena.validar()
        if errores:
            raise ValueError(errores)

        doc = resena.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    # ── READ ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        """Retorna una lista paginada de todas las reseñas."""
        docs = self.col.find({}).skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, resena_id: str) -> dict | None:
        """Retorna una reseña completa por su _id."""
        oid = _to_object_id(resena_id)
        doc = self.col.find_one({"_id": oid})
        return _serializar(doc) if doc else None

    def obtener_por_libro(self, libro_id: str) -> list[dict]:
        """
        Retorna todas las reseñas de un libro específico,
        ordenadas de más reciente a más antigua.
        """
        oid = _to_object_id(libro_id)
        docs = self.col.find({"libro_id": oid}).sort("fecha", -1)
        return [_serializar(d) for d in docs]

    def obtener_por_usuario(self, usuario_id: str) -> list[dict]:
        """Retorna todas las reseñas escritas por un usuario específico."""
        oid = _to_object_id(usuario_id)
        docs = self.col.find({"usuario_id": oid}).sort("fecha", -1)
        return [_serializar(d) for d in docs]

    def obtener_por_calificacion_minima(self, minimo: int) -> list[dict]:
        """
        Retorna todas las reseñas con una calificación mayor o igual al mínimo dado.

        Args:
            minimo: Calificación mínima (1-5).
        """
        if not (1 <= int(minimo) <= 5):
            raise ValueError("La calificación mínima debe estar entre 1 y 5.")
        docs = self.col.find({"calificacion": {"$gte": int(minimo)}}).sort("calificacion", -1)
        return [_serializar(d) for d in docs]

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def actualizar(self, resena_id: str, datos: dict) -> dict | None:
        """
        Actualiza la calificación o el comentario de una reseña.
        Marca automáticamente el campo 'editada' como True.

        Args:
            resena_id: ID de la reseña a actualizar.
            datos:     Diccionario con 'calificacion' y/o 'comentario'.

        Returns:
            El documento actualizado o None si no se encontró la reseña.
        """
        from datetime import datetime, timezone

        oid = _to_object_id(resena_id)

        campos_permitidos = {"calificacion", "comentario"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("Se debe proporcionar 'calificacion' o 'comentario' para actualizar.")

        # Validar calificación si viene en la actualización
        if "calificacion" in actualizacion:
            cal = int(actualizacion["calificacion"])
            if not (1 <= cal <= 5):
                raise ValueError("La calificación debe estar entre 1 y 5.")
            actualizacion["calificacion"] = cal

        # Marcar como editada y registrar fecha de edición
        actualizacion["editada"] = True
        actualizacion["fecha_edicion"] = datetime.now(timezone.utc)

        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": actualizacion},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    # ── DELETE ────────────────────────────────────────────────────────────────

    def eliminar(self, resena_id: str) -> bool:
        """
        Elimina una reseña por su _id.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        oid = _to_object_id(resena_id)
        resultado = self.col.delete_one({"_id": oid})
        return resultado.deleted_count > 0

    # ── ESTADÍSTICAS ──────────────────────────────────────────────────────────

    def promedio_calificacion_libro(self, libro_id: str) -> dict:
        """
        Calcula el promedio de calificaciones y el total de reseñas de un libro.

        Returns:
            Dict con 'libro_id', 'promedio' y 'total_resenas'.
        """
        oid = _to_object_id(libro_id)
        pipeline = [
            {"$match": {"libro_id": oid}},
            {"$group": {
                "_id": "$libro_id",
                "promedio": {"$avg": "$calificacion"},
                "total_resenas": {"$sum": 1},
            }},
            {"$project": {
                "libro_id": {"$toString": "$_id"},
                "promedio": {"$round": ["$promedio", 2]},
                "total_resenas": 1,
                "_id": 0,
            }},
        ]
        resultado = list(self.col.aggregate(pipeline))
        if resultado:
            return resultado[0]
        return {"libro_id": libro_id, "promedio": None, "total_resenas": 0}

    def libros_mejor_calificados(self, top: int = 5) -> list[dict]:
        """
        Retorna los 'top' libros con mejor promedio de calificación
        (mínimo 1 reseña).
        """
        pipeline = [
            {"$group": {
                "_id": "$libro_id",
                "promedio": {"$avg": "$calificacion"},
                "total_resenas": {"$sum": 1},
            }},
            {"$sort": {"promedio": -1, "total_resenas": -1}},
            {"$limit": top},
            {"$project": {
                "libro_id": {"$toString": "$_id"},
                "promedio": {"$round": ["$promedio", 2]},
                "total_resenas": 1,
                "_id": 0,
            }},
        ]
        return list(self.col.aggregate(pipeline))
