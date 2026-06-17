from datetime import datetime, timezone
from pymongo.database import Database

from models.prestamo_model import Prestamo, DURACION_POR_MEMBRESIA
from models.libro_model import Libro
from models.usuario_model import Usuario
from config import generar_id


def _serializar(doc: dict) -> dict:
    if doc:
        if "_id" in doc:
            doc["_id"] = str(doc["_id"])
    return doc


class PrestamoService:

    def __init__(self, db: Database):
        self.db = db
        self.col = db[Prestamo.COLECCION]
        self.col_libros = db[Libro.COLECCION]
        self.col_usuarios = db[Usuario.COLECCION]

    def crear(self, datos: dict) -> dict:
        usuario_id = datos.get("usuario_id", "")
        libro_id = datos.get("libro_id", "")

        libro_doc = self.col_libros.find_one({"libro_id": libro_id})
        if not libro_doc:
            raise ValueError("El libro especificado no existe.")
        if not libro_doc.get("disponible", False):
            raise ValueError(f"El libro '{libro_doc.get('titulo')}' no esta disponible.")

        usuario_doc = self.col_usuarios.find_one({"usuario_id": usuario_id})
        if not usuario_doc:
            raise ValueError("El usuario especificado no existe.")
        if not usuario_doc.get("activo", False):
            raise ValueError("La cuenta del usuario no esta activa.")

        usuario = {
            "usuario_id": usuario_doc["usuario_id"],
            "nombre": usuario_doc["nombre"],
            "correo": usuario_doc["correo"],
        }

        libro = {
            "libro_id": libro_doc["libro_id"],
            "titulo": libro_doc["titulo"],
            "autor": libro_doc["autor"],
        }

        membresia = usuario_doc.get("membresia", "basica")
        dias = datos.get("dias") or DURACION_POR_MEMBRESIA.get(membresia, 14)

        prestamo = Prestamo.crear_con_duracion(
            usuario=usuario,
            libro=libro,
            dias=int(dias),
        )

        errores = prestamo.validar()
        if errores:
            raise ValueError(errores)

        prestamo.prestamo_id = generar_id("PRE", "prestamos", self.db)
        doc = prestamo.to_dict()
        self.col.insert_one(doc)

        self.col_libros.update_one({"libro_id": libro_id}, {"$set": {"disponible": False}})

        self.col_usuarios.update_one(
            {"usuario_id": usuario_id},
            {"$addToSet": {"historial": prestamo.prestamo_id}},
        )

        return _serializar(doc)

    def obtener_todos(self, skip: int = 0, limit: int = 20) -> list[dict]:
        docs = self.col.find({}).sort("fecha_inicio", -1).skip(skip).limit(limit)
        return [_serializar(d) for d in docs]

    def obtener_por_id(self, prestamo_id: str) -> dict | None:
        doc = self.col.find_one({"prestamo_id": prestamo_id})
        return _serializar(doc) if doc else None

    def obtener_por_usuario(self, usuario_id: str) -> list[dict]:
        docs = self.col.find({"usuario.usuario_id": usuario_id})
        return [_serializar(d) for d in docs]

    def obtener_activos(self) -> list[dict]:
        docs = self.col.find({"estado": "activo"})
        return [_serializar(d) for d in docs]

    def obtener_vencidos(self) -> list[dict]:
        ahora = datetime.now(timezone.utc)
        filtro = {"estado": "activo", "fecha_fin": {"$lt": ahora}}

        self.col.update_many(filtro, {"$set": {"estado": "vencido"}})

        docs = self.col.find({"estado": "vencido"})
        return [_serializar(d) for d in docs]

    def devolver(self, prestamo_id: str) -> dict | None:
        prestamo = self.col.find_one({"prestamo_id": prestamo_id})

        if not prestamo:
            raise ValueError("El prestamo especificado no existe.")
        if prestamo.get("estado") == "devuelto":
            raise ValueError("Este prestamo ya fue devuelto.")

        ahora = datetime.now(timezone.utc)

        resultado = self.col.find_one_and_update(
            {"prestamo_id": prestamo_id},
            {"$set": {"estado": "devuelto", "fecha_devolucion": ahora}},
            return_document=True,
        )

        self.col_libros.update_one(
            {"libro_id": prestamo["libro"]["libro_id"]},
            {"$set": {"disponible": True}},
        )

        return _serializar(resultado) if resultado else None

    def actualizar_estado(self, prestamo_id: str, estado: str) -> dict | None:
        estados_validos = {"activo", "devuelto", "vencido"}
        if estado not in estados_validos:
            raise ValueError(f"Estado no valido. Opciones: {sorted(estados_validos)}")

        resultado = self.col.find_one_and_update(
            {"prestamo_id": prestamo_id},
            {"$set": {"estado": estado}},
            return_document=True,
        )
        return _serializar(resultado) if resultado else None

    def eliminar(self, prestamo_id: str) -> bool:
        resultado = self.col.delete_one({"prestamo_id": prestamo_id})
        return resultado.deleted_count > 0

    def contar_por_estado(self) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$estado", "total": {"$sum": 1}}},
            {"$sort": {"total": -1}},
            {"$project": {"estado": "$_id", "total": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))

    def usuarios_con_mas_prestamos(self, top: int = 5) -> list[dict]:
        pipeline = [
            {"$group": {"_id": "$usuario.usuario_id", "total_prestamos": {"$sum": 1}}},
            {"$sort": {"total_prestamos": -1}},
            {"$limit": top},
            {"$project": {"usuario_id": "$_id", "total_prestamos": 1, "_id": 0}},
        ]
        return list(self.col.aggregate(pipeline))
