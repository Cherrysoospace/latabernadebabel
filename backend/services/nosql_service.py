"""
nosql_service.py — Ejecuta comandos mongosh directamente sobre MongoDB.

Traduce comandos estilo mongosh (ej: db.libros.findOne({genero: "ficcion"}))
a operaciones PyMongo y retorna los resultados serializables.
"""

import json
import re
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId
from bson.json_util import dumps
from pymongo.database import Database


MONGOSH_TO_PYMONGO = {
    'find': 'find',
    'findOne': 'find_one',
    'find_one': 'find_one',
    'countDocuments': 'count_documents',
    'count_documents': 'count_documents',
    'estimatedDocumentCount': 'estimated_document_count',
    'insertOne': 'insert_one',
    'insert_one': 'insert_one',
    'insertMany': 'insert_many',
    'insert_many': 'insert_many',
    'updateOne': 'update_one',
    'update_one': 'update_one',
    'updateMany': 'update_many',
    'update_many': 'update_many',
    'deleteOne': 'delete_one',
    'delete_one': 'delete_one',
    'deleteMany': 'delete_many',
    'delete_many': 'delete_many',
    'aggregate': 'aggregate',
    'distinct': 'distinct',
    'bulkWrite': 'bulk_write',
    'bulk_write': 'bulk_write',
    'createIndex': 'create_index',
    'create_index': 'create_index',
    'drop': 'drop',
    'rename': 'rename',
}

ESCAPED_COLLECTIONS = {'admin', 'config', 'local', 'system'}


def _serializar_resultado(resultado):
    """Convierte cualquier resultado a JSON-serializable usando bson.json_util."""
    return json.loads(dumps(resultado))


def _partir_args(s):
    """Divide string de argumentos por coma respetando anidamiento y strings."""
    depth = 0
    in_str = False
    char_str = None
    partes = []
    actual = []
    for c in s:
        if in_str:
            actual.append(c)
            if c == char_str:
                in_str = False
        elif c in ('"', "'"):
            in_str = True
            char_str = c
            actual.append(c)
        elif c in '({[':
            depth += 1
            actual.append(c)
        elif c in ')}]':
            depth -= 1
            actual.append(c)
        elif c == ',' and depth == 0:
            partes.append(''.join(actual).strip())
            actual = []
            continue
        else:
            actual.append(c)
    resto = ''.join(actual).strip()
    if resto:
        partes.append(resto)
    return partes


def _js_a_python(valor):
    """Convierte un valor JS (string) a objeto Python."""
    v = valor.strip()

    if not v:
        return None

    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]

    if v in ('true', 'True'):
        return True
    if v in ('false', 'False'):
        return False
    if v in ('null', 'None', 'undefined'):
        return None

    try:
        if '.' in v:
            return float(v)
        return int(v)
    except ValueError:
        pass

    m = re.match(r'ObjectId\([\'"]([^\'"]+)[\'"]\)', v)
    if m:
        try:
            return ObjectId(m.group(1))
        except InvalidId:
            return v

    m = re.match(r'ISODate\([\'"]([^\'"]+)[\'"]\)', v)
    if m:
        try:
            return datetime.fromisoformat(m.group(1))
        except ValueError:
            return v

    if v.startswith('[') and v.endswith(']'):
        inner = v[1:-1]
        items = _partir_args(inner) if inner.strip() else []
        return [_js_a_python(item) for item in items]

    if v.startswith('{') and v.endswith('}'):
        inner = v[1:-1]
        if not inner.strip():
            return {}
        pares = _partir_args(inner)
        obj = {}
        for par in pares:
            if ':' not in par:
                continue
            llave, val = par.split(':', 1)
            llave = llave.strip().strip('"').strip("'")
            obj[llave] = _js_a_python(val.strip())
        return obj

    m = re.match(r'Number(Int|Long|Decimal)\(([^)]+)\)', v)
    if m:
        return int(m.group(2)) if m.group(1) != 'Decimal' else float(m.group(2))

    return v


class NoSqlService:
    def __init__(self, db: Database):
        self.db = db

    def ejecutar(self, comando: str) -> dict:
        comando = comando.strip().rstrip(';')

        if not comando:
            return {'resultado': None, 'tipo': 'empty'}

        if comando == 'show collections' or comando == 'show tables':
            cols = self.db.list_collection_names()
            return {'resultado': cols, 'tipo': 'list'}

        if comando == 'show dbs':
            info = self.db.client.list_database_names()
            return {'resultado': info, 'tipo': 'list'}

        match = re.match(
            r'^db\.(\w+)\.(\w+)\(([\s\S]*?)\)\s*$',
            comando,
        )
        if not match:
            match = re.match(
                r'^db\.(\w+)\.(\w+)\(([\s\S]*?)\)\s*\.\s*toArray\(\)\s*$',
                comando,
            )

        if not match:
            return {
                'error': f'Comando no reconocido: "{comando}". Usa db.coleccion.metodo(args)',
                'tipo': 'error',
            }

        coleccion = match.group(1)
        metodo_mongosh = match.group(2)
        args_str = match.group(3).strip()

        pymongo_metodo = MONGOSH_TO_PYMONGO.get(metodo_mongosh)
        if not pymongo_metodo:
            return {
                'error': f'Método "{metodo_mongosh}" no soportado. Soportados: {", ".join(sorted(MONGOSH_TO_PYMONGO))}',
                'tipo': 'error',
            }

        if coleccion in ESCAPED_COLLECTIONS:
            return {
                'error': f'No puedes ejecutar comandos sobre la colección del sistema "{coleccion}"',
                'tipo': 'error',
            }

        col = self.db[coleccion]

        try:
            args_python = []
            if args_str:
                partes = _partir_args(args_str)
                args_python = [_js_a_python(p) for p in partes]

            # countDocuments sin args → filter vacío
            if pymongo_metodo == 'count_documents' and not args_python:
                args_python = [{}]

            if not hasattr(col, pymongo_metodo):
                return {
                    'error': f'El método "{pymongo_metodo}" no existe en PyMongo',
                    'tipo': 'error',
                }

            resultado = getattr(col, pymongo_metodo)(*args_python)
            return self._procesar_resultado(resultado, metodo_mongosh, col)

        except Exception as e:
            return {
                'error': f'Error al ejecutar "{comando}": {str(e)}',
                'tipo': 'error',
            }

    def _procesar_resultado(self, resultado, metodo_mongosh, col):
        if metodo_mongosh in ('find', 'aggregate'):
            docs = list(resultado)
            count = len(docs)
            return {
                'resultado': _serializar_resultado(docs),
                'tipo': 'cursor',
                'total': count,
            }

        if metodo_mongosh == 'findOne':
            if resultado is None:
                return {'resultado': None, 'tipo': 'null'}
            return {
                'resultado': _serializar_resultado(resultado),
                'tipo': 'document',
            }

        if metodo_mongosh == 'countDocuments':
            return {
                'resultado': resultado,
                'tipo': 'number',
            }

        if metodo_mongosh == 'estimatedDocumentCount':
            return {
                'resultado': resultado,
                'tipo': 'number',
            }

        if metodo_mongosh == 'distinct':
            return {
                'resultado': list(resultado) if hasattr(resultado, '__iter__') and not isinstance(resultado, (str, bytes)) else resultado,
                'tipo': 'list',
            }

        if metodo_mongosh in ('insertOne', 'insert_one'):
            return {
                'resultado': str(resultado.inserted_id),
                'tipo': 'insert_result',
            }

        if metodo_mongosh in ('insertMany', 'insert_many'):
            return {
                'resultado': [str(oid) for oid in resultado.inserted_ids],
                'tipo': 'insert_result',
            }

        if metodo_mongosh in ('updateOne', 'update_one', 'updateMany', 'update_many'):
            return {
                'resultado': {
                    'matched_count': resultado.matched_count,
                    'modified_count': resultado.modified_count,
                    'upserted_id': str(resultado.upserted_id) if resultado.upserted_id else None,
                },
                'tipo': 'update_result',
            }

        if metodo_mongosh in ('deleteOne', 'delete_one', 'deleteMany', 'delete_many'):
            return {
                'resultado': {'deleted_count': resultado.deleted_count},
                'tipo': 'delete_result',
            }

        if metodo_mongosh == 'drop':
            return {'resultado': 'Colección eliminada', 'tipo': 'success'}

        if metodo_mongosh in ('createIndex', 'create_index'):
            return {
                'resultado': str(resultado),
                'tipo': 'success',
            }

        return {
            'resultado': _serializar_resultado(resultado),
            'tipo': 'raw',
        }
