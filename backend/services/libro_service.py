"""
libro_service.py — Lógica de negocio para la colección 'libros'.

Responsabilidades:
    - Operaciones CRUD sobre la colección 'libros'.
    - Consultas específicas del dominio (búsqueda, filtros, disponibilidad).
    - Validación de modelo antes de persistir.
"""

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from models.libro_model import Libro


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _to_object_id(id_str: str) -> ObjectId:
    """Convierte un string a ObjectId. Lanza ValueError si es inválido."""
    try:
        return ObjectId(id_str)
    except (InvalidId, TypeError):
        raise ValueError(f"ID inválido: '{id_str}'")


def _serializar(doc: dict) -> dict:
    """Convierte ObjectId a string para que Flask pueda serializar a JSON."""
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# ─── Service ──────────────────────────────────────────────────────────────────

class LibroService:
    """
    Capa de servicio para la colección 'libros'.
    Recibe la instancia de base de datos (db) inyectada desde la app Flask.
    """

    def __init__(self, db: Database):
        self.col = db[Libro.COLECCION]

    # ── CREATE ────────────────────────────────────────────────────────────────

    def crear(self, datos: dict) -> dict:
        """
        Crea un nuevo libro en la base de datos.

        Args:
            datos: Diccionario con los campos del libro (desde el request).

        Returns:
            El documento insertado con su _id como string.

        Raises:
            ValueError: Si la validación del modelo falla.
        """
        libro = Libro(
            titulo=datos.get("titulo", ""),
            autor=datos.get("autor", ""),
            genero=datos.get("genero", ""),
            editorial=datos.get("editorial"),
            year=datos.get("anio"),
            idioma=datos.get("idioma", "es"),
            formato=datos.get("formato", "fisico"),
            descripcion=datos.get("descripcion"),
            disponible=datos.get("disponible", True),
        )

        errores = libro.validar()
        if errores:
            raise ValueError(errores)

        doc = libro.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    # ── READ ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        """
        Retorna una lista paginada de todos los libros.

        Args:
            skip:  Número de documentos a saltar (offset).
            limit: Máximo de documentos a retornar.
        """
        docs = self.col.find({}, {"_id": 1, "titulo": 1, "autor": 1,
                                   "genero": 1, "disponible": 1, "anio": 1})
        docs = docs.skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, libro_id: str) -> dict | None:
        """
        Retorna un libro completo por su _id.

        Returns:
            El documento o None si no existe.
        """
        oid = _to_object_id(libro_id)
        doc = self.col.find_one({"_id": oid})
        return _serializar(doc) if doc else None

    def buscar(self, termino: str) -> list[dict]:
        """
        Búsqueda de libros por título o autor (insensible a mayúsculas/minúsculas).

        Args:
            termino: Texto parcial o completo a buscar.
        """
        regex = {"$regex": termino, "$options": "i"}
        docs = self.col.find({"$or": [{"titulo": regex}, {"autor": regex}]})
        return [_serializar(d) for d in docs]

    def obtener_disponibles(self) -> list[dict]:
        """Retorna todos los libros marcados como disponibles."""
        docs = self.col.find({"disponible": True},
                              {"titulo": 1, "autor": 1, "genero": 1, "formato": 1})
        return [_serializar(d) for d in docs]

    def obtener_por_genero(self, genero: str) -> list[dict]:
        """Retorna todos los libros de un género específico."""
        docs = self.col.find({"genero": genero.lower()})
        return [_serializar(d) for d in docs]

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def actualizar(self, libro_id: str, datos: dict) -> dict | None:
        """
        Actualiza los campos permitidos de un libro existente.

        Args:
            libro_id: ID del libro a actualizar.
            datos:    Diccionario con los campos a modificar.

        Returns:
            El documento actualizado o None si no se encontró el libro.
        """
        oid = _to_object_id(libro_id)

        # Solo se permiten actualizar estos campos
        campos_permitidos = {
            "titulo", "autor", "genero", "editorial",
            "anio", "idioma", "formato", "descripcion", "disponible"
        }
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos válidos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": actualizacion},
            return_document=True,  # retorna el documento DESPUÉS del update
        )
        return _serializar(resultado) if resultado else None

    def cambiar_disponibilidad(self, libro_id: str, disponible: bool) -> dict | None:
        """
        Cambia únicamente el campo 'disponible' de un libro.
        Útil para marcarlo como prestado o devuelto.
        """
        return self.actualizar(libro_id, {"disponible": disponible})

    # ── DELETE ────────────────────────────────────────────────────────────────

    def eliminar(self, libro_id: str) -> bool:
        """
        Elimina un libro por su _id.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        oid = _to_object_id(libro_id)
        resultado = self.col.delete_one({"_id": oid})
        return resultado.deleted_count > 0

    # ── ESTADÍSTICAS ──────────────────────────────────────────────────────────

    def contar_por_genero(self) -> list[dict]:
        """
        Agrega y cuenta cuántos libros hay por género.
        Retorna la lista ordenada de mayor a menor.
        """
        pipeline = [
            {"$group": {"_id": "$genero", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"genero": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
