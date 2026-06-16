"""
usuario_service.py — Lógica de negocio para la colección 'usuarios'.

Responsabilidades:
    - Operaciones CRUD sobre la colección 'usuarios'.
    - Consultas específicas: búsqueda por correo, filtro por membresía.
    - Gestión del historial de préstamos del usuario.
    - Validación de modelo antes de persistir.
"""

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

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
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
        # El historial contiene ObjectIds de préstamos
        if "historial" in doc and isinstance(doc["historial"], list):
            doc["historial"] = [str(h) for h in doc["historial"]]
    return doc


# ─── Service ──────────────────────────────────────────────────────────────────

class UsuarioService:
    """
    Capa de servicio para la colección 'usuarios'.
    Recibe la instancia de base de datos (db) inyectada desde la app Flask.
    """

    def __init__(self, db: Database):
        self.col = db[Usuario.COLECCION]

    # ── CREATE ────────────────────────────────────────────────────────────────

    def crear(self, datos: dict) -> dict:
        """
        Crea un nuevo usuario en la base de datos.

        Args:
            datos: Diccionario con los campos del usuario (desde el request).

        Returns:
            El documento insertado con su _id como string.

        Raises:
            ValueError: Si la validación del modelo falla o el correo ya existe.
        """
        # Verificar correo único antes de insertar
        correo = datos.get("correo", "").strip().lower()
        if self.col.find_one({"correo": correo}):
            raise ValueError(f"Ya existe un usuario con el correo '{correo}'.")

        usuario = Usuario(
            nombre=datos.get("nombre", ""),
            correo=correo,
            membresia=datos.get("membresia", "basica"),
            historial=datos.get("historial", []),
            preferencias=datos.get("preferencias", []),
            activo=datos.get("activo", True),
        )

        errores = usuario.validar()
        if errores:
            raise ValueError(errores)

        doc = usuario.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    # ── READ ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        """
        Retorna una lista paginada de todos los usuarios.

        Args:
            skip:  Número de documentos a saltar (offset).
            limit: Máximo de documentos a retornar.
        """
        docs = self.col.find({}, {"_id": 1, "nombre": 1, "correo": 1,
                                   "membresia": 1, "activo": 1})
        docs = docs.skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, usuario_id: str) -> dict | None:
        """
        Retorna un usuario completo por su _id.

        Returns:
            El documento o None si no existe.
        """
        oid = _to_object_id(usuario_id)
        doc = self.col.find_one({"_id": oid})
        return _serializar(doc) if doc else None

    def obtener_por_correo(self, correo: str) -> dict | None:
        """Busca y retorna un usuario por su correo electrónico."""
        doc = self.col.find_one({"correo": correo.strip().lower()})
        return _serializar(doc) if doc else None

    def obtener_por_membresia(self, membresia: str) -> list[dict]:
        """Retorna todos los usuarios con un tipo de membresía específico."""
        docs = self.col.find({"membresia": membresia.lower()})
        return [_serializar(d) for d in docs]

    def obtener_activos(self) -> list[dict]:
        """Retorna todos los usuarios con cuenta activa."""
        docs = self.col.find({"activo": True},
                              {"nombre": 1, "correo": 1, "membresia": 1})
        return [_serializar(d) for d in docs]

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def actualizar(self, usuario_id: str, datos: dict) -> dict | None:
        """
        Actualiza los campos permitidos de un usuario existente.

        Args:
            usuario_id: ID del usuario a actualizar.
            datos:      Diccionario con los campos a modificar.

        Returns:
            El documento actualizado o None si no se encontró el usuario.
        """
        oid = _to_object_id(usuario_id)

        campos_permitidos = {"nombre", "correo", "membresia", "preferencias", "activo"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos válidos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": actualizacion},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def agregar_prestamo_al_historial(self, usuario_id: str, prestamo_id: ObjectId) -> bool:
        """
        Agrega el ObjectId de un préstamo al historial del usuario.

        Returns:
            True si se actualizó correctamente.
        """
        oid = _to_object_id(usuario_id)
        resultado = self.col.update_one(
            {"_id": oid},
            {"$addToSet": {"historial": prestamo_id}},  # addToSet evita duplicados
        )
        return resultado.modified_count > 0

    # ── DELETE ────────────────────────────────────────────────────────────────

    def eliminar(self, usuario_id: str) -> bool:
        """
        Elimina un usuario por su _id.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        oid = _to_object_id(usuario_id)
        resultado = self.col.delete_one({"_id": oid})
        return resultado.deleted_count > 0

    def desactivar(self, usuario_id: str) -> dict | None:
        """
        Desactiva (soft delete) la cuenta de un usuario en lugar de eliminarla.
        Conserva sus datos históricos.
        """
        return self.actualizar(usuario_id, {"activo": False})

    # ── ESTADÍSTICAS ──────────────────────────────────────────────────────────

    def contar_por_membresia(self) -> list[dict]:
        """
        Agrega y cuenta cuántos usuarios hay por tipo de membresía.
        Retorna la lista ordenada de mayor a menor.
        """
        pipeline = [
            {"$group": {"_id": "$membresia", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"membresia": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
