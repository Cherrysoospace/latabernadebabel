from pymongo.database import Database

from models.libro_model import Libro
from models.prestamo_model import Prestamo
from models.resena_model import Resena
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class LibroService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Libro.COLECCION]
        self.col_prestamos = db[Prestamo.COLECCION]
        self.col_resenas = db[Resena.COLECCION]

    def crear(self, datos: dict) -> dict:
        libro = Libro(
            titulo=datos.get("titulo", ""),
            autor=datos.get("autor", {}),
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

        libro.libro_id = generar_id("LIB", "libros", self.db)
        doc = libro.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> dict:
        filtro = {}
        total = self.col.count_documents(filtro)
        docs = self.col.find(filtro, {"_id": 1, "libro_id": 1, "titulo": 1, "autor": 1,
                                      "genero": 1, "disponible": 1, "anio": 1, "idioma": 1})
        docs = docs.sort("libro_id", 1).skip(skip).limit(limit)
        return {
            "items": [_serializar(d) for d in docs],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def obtener_por_id(self, libro_id: str) -> dict | None:
        doc = self.col.find_one({"libro_id": libro_id})
        return _serializar(doc) if doc else None

    def buscar(self, termino: str) -> list[dict]:
        regex = {"$regex": termino, "$options": "i"}
        docs = self.col.find({"$or": [{"titulo": regex}, {"autor.name": regex}]})
        return [_serializar(d) for d in docs]

    def obtener_disponibles(self) -> list[dict]:
        docs = self.col.find({"disponible": True})
        return [_serializar(d) for d in docs]

    def obtener_por_genero(self, genero: str) -> list[dict]:
        docs = self.col.find({"genero": genero.lower()})
        return [_serializar(d) for d in docs]

    def _propagar_cambios(self, libro_id: str, actualizacion: dict):
        if "titulo" in actualizacion:
            self.col_prestamos.update_many(
                {"libro.libro_id": libro_id},
                {"$set": {"libro.titulo": actualizacion["titulo"]}},
            )
            self.col_resenas.update_many(
                {"libro.libro_id": libro_id},
                {"$set": {"libro.titulo": actualizacion["titulo"]}},
            )
        if "autor" in actualizacion:
            self.col_prestamos.update_many(
                {"libro.libro_id": libro_id},
                {"$set": {"libro.autor": actualizacion["autor"]}},
            )

    def actualizar(self, libro_id: str, datos: dict) -> dict | None:
        campos_permitidos = {
            "titulo", "autor", "genero", "editorial",
            "anio", "idioma", "formato", "descripcion", "disponible"
        }
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos validos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"libro_id": libro_id},
            {"$set": actualizacion},
            return_document=True,
        )
        if resultado:
            self._propagar_cambios(libro_id, actualizacion)
        return _serializar(resultado) if resultado else None

    def cambiar_disponibilidad(self, libro_id: str, disponible: bool) -> dict | None:
        return self.actualizar(libro_id, {"disponible": disponible})

    def eliminar(self, libro_id: str) -> bool:
        refs = []
        n_prestamos = self.col_prestamos.count_documents({"libro.libro_id": libro_id})
        if n_prestamos:
            refs.append(f"{n_prestamos} préstamo(s)")
        n_resenas = self.col_resenas.count_documents({"libro.libro_id": libro_id})
        if n_resenas:
            refs.append(f"{n_resenas} reseña(s)")
        if refs:
            raise ValueError(f"No se puede eliminar el libro: está referenciado en {' y '.join(refs)}.")
        resultado = self.col.delete_one({"libro_id": libro_id})
        return resultado.deleted_count > 0

    def contar_por_genero(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$genero", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"genero": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
