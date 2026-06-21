from pymongo.database import Database

from models.autor_model import Autor
from models.libro_model import Libro
from models.prestamo_model import Prestamo
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc and "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


class AutorService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Autor.COLECCION]
        self.col_libros = db[Libro.COLECCION]
        self.col_prestamos = db[Prestamo.COLECCION]

    def crear(self, datos: dict) -> dict:
        nombre = datos.get("nombre", "").strip()
        if not nombre:
            raise ValueError("El campo 'nombre' es requerido.")

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

        autor.autor_id = generar_id("AUT", "autores", self.db)
        doc = autor.to_dict()
        self.col.insert_one(doc)
        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> dict:
        filtro = {}
        total = self.col.count_documents(filtro)
        docs = self.col.find(filtro, {"_id": 1, "autor_id": 1, "nombre": 1, "nacionalidad": 1,
                                      "obras": 1, "premios": 1})
        docs = docs.sort("autor_id", 1).skip(skip).limit(limit)
        return {
            "items": [_serializar(d) for d in docs],
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def obtener_por_id(self, autor_id: str) -> dict | None:
        doc = self.col.find_one({"autor_id": autor_id})
        return _serializar(doc) if doc else None

    def buscar_por_nombre(self, nombre: str) -> list[dict]:
        docs = self.col.find(
            {"nombre": {"$regex": nombre, "$options": "i"}}
        )
        return [_serializar(d) for d in docs]

    def obtener_por_nacionalidad(self, nacionalidad: str) -> list[dict]:
        docs = self.col.find(
            {"nacionalidad": {"$regex": f"^{nacionalidad}$", "$options": "i"}}
        )
        return [_serializar(d) for d in docs]

    def obtener_con_premios(self) -> list[dict]:
        docs = self.col.find(
            {"premios": {"$exists": True, "$not": {"$size": 0}}},
            {"autor_id": 1, "nombre": 1, "nacionalidad": 1, "premios": 1},
        )
        return [_serializar(d) for d in docs]

    def _propagar_cambios(self, autor_id: str, actualizacion: dict):
        if "nombre" in actualizacion:
            self.col_libros.update_many(
                {"autor.autor_id": autor_id},
                {"$set": {"autor.name": actualizacion["nombre"]}},
            )
            self.col_prestamos.update_many(
                {"libro.autor.autor_id": autor_id},
                {"$set": {"libro.autor.name": actualizacion["nombre"]}},
            )
        if "nacionalidad" in actualizacion:
            self.col_libros.update_many(
                {"autor.autor_id": autor_id},
                {"$set": {"autor.nacionalidad": actualizacion["nacionalidad"]}},
            )
            self.col_prestamos.update_many(
                {"libro.autor.autor_id": autor_id},
                {"$set": {"libro.autor.nacionalidad": actualizacion["nacionalidad"]}},
            )

    def actualizar(self, autor_id: str, datos: dict) -> dict | None:
        campos_permitidos = {"nombre", "biografia", "nacionalidad"}
        actualizacion = {k: v for k, v in datos.items() if k in campos_permitidos}

        if not actualizacion:
            raise ValueError("No se proporcionaron campos validos para actualizar.")

        resultado = self.col.find_one_and_update(
            {"autor_id": autor_id},
            {"$set": actualizacion},
            return_document=True,
        )
        if resultado:
            self._propagar_cambios(autor_id, actualizacion)
        return _serializar(resultado) if resultado else None

    def agregar_obra(self, autor_id: str, titulo: str) -> dict | None:
        titulo = titulo.strip()
        if not titulo:
            raise ValueError("El titulo de la obra no puede estar vacio.")

        resultado = self.col.find_one_and_update(
            {"autor_id": autor_id},
            {"$addToSet": {"obras": titulo}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def agregar_premio(self, autor_id: str, premio: str) -> dict | None:
        premio = premio.strip()
        if not premio:
            raise ValueError("El nombre del premio no puede estar vacio.")

        resultado = self.col.find_one_and_update(
            {"autor_id": autor_id},
            {"$addToSet": {"premios": premio}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def remover_obra(self, autor_id: str, titulo: str) -> dict | None:
        titulo = titulo.strip()
        resultado = self.col.find_one_and_update(
            {"autor_id": autor_id},
            {"$pull": {"obras": titulo}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def eliminar(self, autor_id: str) -> bool:
        n_libros = self.col_libros.count_documents({"autor.autor_id": autor_id})
        if n_libros:
            raise ValueError(
                f"No se puede eliminar el autor: está referenciado en {n_libros} libro(s)."
            )
        resultado = self.col.delete_one({"autor_id": autor_id})
        return resultado.deleted_count > 0

    def contar_por_nacionalidad(self) -> list[dict]:
        pipeline = [
            {"$match": {"nacionalidad": {"$ne": None}}},
            {"$group": {"_id": "$nacionalidad", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"nacionalidad": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))

    def autores_con_mas_obras(self, top: int = 5) -> list[dict]:
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
