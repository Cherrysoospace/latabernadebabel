"""
autor_service.py — Lógica de negocio para la colección 'autores'.

Responsabilidades:
    - Operaciones CRUD sobre la colección 'autores'.
    - Gestión de obras y premios (agregar/remover de listas).
    - Búsqueda por nombre y filtro por nacionalidad.
    - Validación de modelo antes de persistir.
"""

from bson import ObjectId
from bson.errors import InvalidId
from pymongo.database import Database

from models.autor_model import Autor


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

class AutorService:
    """
    Capa de servicio para la colección 'autores'.
    Recibe la instancia de base de datos (db) inyectada desde la app Flask.
    """

    def __init__(self, db: Database):
        self.col = db[Autor.COLECCION]

    # ── CREATE ────────────────────────────────────────────────────────────────

    def crear(self, datos: dict) -> dict:
        """
        Crea un nuevo autor en la base de datos.

        Args:
            datos: Diccionario con los campos del autor (desde el request).

        Returns:
            El documento insertado con su _id como string.

        Raises:
            ValueError: Si la validación del modelo falla o el nombre ya existe.
        """
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            raise ValueError("El campo 'nombre' es requerido.")

        # Verificar nombre único (insensible a mayúsculas)
        if self.col.find_one({"nombre": {"$regex": f"^{nombre}$", "$options": "i"}}):
            raise ValueError(f"Ya existe un autor con el nombre '{nombre}'.")

        autor = Autor(
            nombre=nombre,
            biografia=datos.get("biografia"),
            nacionalidad=datos.get("nacionalidad"),
            obras=datos.get("obras", []),
            premios=datos.get("premios", []),
        )

        errores = autor.validar()
        if errores:
            raise ValueError(errores)

        doc = autor.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    # ── READ ──────────────────────────────────────────────────────────────────

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        """
        Retorna una lista paginada de todos los autores.

        Args:
            skip:  Número de documentos a saltar (offset).
            limit: Máximo de documentos a retornar.
        """
        docs = self.col.find({}, {"_id": 1, "nombre": 1, "nacionalidad": 1,
                                   "obras": 1, "premios": 1})
        docs = docs.skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, autor_id: str) -> dict | None:
        """
        Retorna un autor completo por su _id.

        Returns:
            El documento o None si no existe.
        """
        oid = _to_object_id(autor_id)
        doc = self.col.find_one({"_id": oid})
        return _serializar(doc) if doc else None

    def buscar_por_nombre(self, nombre: str) -> list[dict]:
        """
        Búsqueda de autores por nombre (insensible a mayúsculas/minúsculas).

        Args:
            nombre: Texto parcial o completo a buscar.
        """
        docs = self.col.find(
            {"nombre": {"$regex": nombre, "$options": "i"}}
        )
        return [_serializar(d) for d in docs]

    def obtener_por_nacionalidad(self, nacionalidad: str) -> list[dict]:
        """Retorna todos los autores de una nacionalidad específica."""
        docs = self.col.find(
            {"nacionalidad": {"$regex": f"^{nacionalidad}$", "$options": "i"}}
        )
        return [_serializar(d) for d in docs]

    def obtener_con_premios(self) -> list[dict]:
        """Retorna todos los autores que tienen al menos un premio registrado."""
        docs = self.col.find(
            {"premios": {"$exists": True, "$not": {"$size": 0}}},
            {"nombre": 1, "nacionalidad": 1, "premios": 1},
        )
        return [_serializar(d) for d in docs]

    # ── UPDATE ────────────────────────────────────────────────────────────────

    def actualizar(self, autor_id: str, datos: dict) -> dict | None:
        """
        Actualiza los campos base de un autor (no las listas de obras/premios).
        Para modificar obras y premios usar los métodos específicos.

        Args:
            autor_id: ID del autor a actualizar.
            datos:    Diccionario con los campos a modificar.

        Returns:
            El documento actualizado o None si no se encontró el autor.
        """
        oid = _to_object_id(autor_id)

        campos_permitidos = {"nombre", "biografia", "nacionalidad"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos válidos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$set": actualizacion},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def agregar_obra(self, autor_id: str, titulo: str) -> dict | None:
        """
        Agrega un título a la lista de obras del autor si no existe ya.

        Args:
            autor_id: ID del autor.
            titulo:   Título de la obra a agregar.

        Returns:
            El documento actualizado.
        """
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El título de la obra no puede estar vacío.")

        oid = _to_object_id(autor_id)
        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$addToSet": {"obras": titulo}},  # addToSet evita duplicados
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def agregar_premio(self, autor_id: str, premio: str) -> dict | None:
        """
        Agrega un premio a la lista del autor si no existe ya.

        Args:
            autor_id: ID del autor.
            premio:   Nombre del premio a agregar.

        Returns:
            El documento actualizado.
        """
        premio = premio.strip()
        if not premio:
            raise ValueError("El nombre del premio no puede estar vacío.")

        oid = _to_object_id(autor_id)
        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$addToSet": {"premios": premio}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def remover_obra(self, autor_id: str, titulo: str) -> dict | None:
        """
        Elimina un título de la lista de obras del autor.

        Returns:
            El documento actualizado.
        """
        titulo = titulo.strip()
        oid = _to_object_id(autor_id)
        resultado = self.col.find_one_and_update(
            {"_id": oid},
            {"$pull": {"obras": titulo}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    # ── DELETE ────────────────────────────────────────────────────────────────

    def eliminar(self, autor_id: str) -> bool:
        """
        Elimina un autor por su _id.

        Returns:
            True si se eliminó, False si no se encontró.
        """
        oid = _to_object_id(autor_id)
        resultado = self.col.delete_one({"_id": oid})
        return resultado.deleted_count > 0

    # ── ESTADÍSTICAS ──────────────────────────────────────────────────────────

    def contar_por_nacionalidad(self) -> list[dict]:
        """
        Agrega y cuenta cuántos autores hay por nacionalidad.
        Retorna la lista ordenada de mayor a menor.
        """
        pipeline = [
            {"$match": {"nacionalidad": {"$ne": None}}},
            {"$group": {"_id": "$nacionalidad", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"nacionalidad": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))

    def autores_con_mas_obras(self, top: int = 5) -> list[dict]:
        """
        Retorna los 'top' autores con mayor cantidad de obras registradas.
        """
        pipeline = [
            {"$project": {
                "nombre": 1,
                "nacionalidad": 1,
                "total_obras": {"$size": "$obras"},
            }},
            {"$sort": {"total_obras": -1}},
            {"$limit": top},
        ]
        docs = list(self.col.aggregate(pipeline))
        return [_serializar(d) for d in docs]
