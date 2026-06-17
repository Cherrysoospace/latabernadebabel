"""
routes/__init__.py
Exporta todos los blueprints de la aplicación para facilitar su importación.
"""

from .libro_routes    import libro_bp
from .usuario_routes  import usuario_bp
from .prestamo_routes import prestamo_bp
from .resena_routes   import resena_bp
from .autor_routes    import autor_bp
from .nosql_routes    import nosql_bp

__all__ = ["libro_bp", "usuario_bp", "prestamo_bp", "resena_bp", "autor_bp", "nosql_bp"]
