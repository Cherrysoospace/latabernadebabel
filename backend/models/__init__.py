"""
models/__init__.py
Exporta todos los modelos de la aplicación para facilitar su importación.
"""

from .libro_model import Libro
from .usuario_model import Usuario
from .prestamo_model import Prestamo
from .resena_model import Resena
from .autor_model import Autor

__all__ = ["Libro", "Usuario", "Prestamo", "Resena", "Autor"]
