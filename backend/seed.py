import sys
from datetime import datetime, timezone, timedelta
from bson import ObjectId

from config import get_db, generar_id
from models.autor_model import Autor
from models.libro_model import Libro
from models.usuario_model import Usuario
from models.prestamo_model import Prestamo, DURACION_POR_MEMBRESIA
from models.resena_model import Resena


def poblar():
    db = get_db()

    print("Limpiando colecciones existentes...")
    db.autores.delete_many({})
    db.libros.delete_many({})
    db.usuarios.delete_many({})
    db.prestamos.delete_many({})
    db.resenas.delete_many({})
    db.counters.delete_many({})

    # ══════════════════════════════════════════════════════════════════
    # 1. AUTORES (AUT-0001 al AUT-0010)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando autores...")
    autores_data = [
        Autor("Gabriel Garcia Marquez", "Escritor colombiano, premio Nobel de Literatura 1982.", "Colombia",
              ["Cien anos de soledad", "El amor en los tiempos del colera", "Cronica de una muerte anunciada"],
              ["Premio Nobel de Literatura", "Premio Romulo Gallegos"], autor_id="AUT-0001"),
        Autor("Jane Austen", "Novelista inglesa, pionera de la novela moderna.", "Inglaterra",
              ["Orgullo y prejuicio", "Sentido y sensibilidad", "Emma", "Persuasion"],
              [], autor_id="AUT-0002"),
        Autor("Isaac Asimov", "Escritor y bioquimico ruso-estadounidense, maestro de la ciencia ficcion.", "Estados Unidos",
              ["Fundacion", "Yo, robot", "El fin de la eternidad", "Los propios dioses"],
              ["Premio Hugo", "Premio Nebula", "Premio Locus"], autor_id="AUT-0003"),
        Autor("Isabel Allende", "Escritora chilena, autora de best-sellers internacionales.", "Chile",
              ["La casa de los espiritus", "Eva Luna", "Paula", "El viento conoce mi nombre"],
              ["Premio Nacional de Literatura de Chile", "Premio Gabriela Mistral"], autor_id="AUT-0004"),
        Autor("J.R.R. Tolkien", "Filologo y escritor britanico, padre de la literatura fantastica moderna.", "Inglaterra",
              ["El hobbit", "El senor de los anillos", "El Silmarillion"],
              [], autor_id="AUT-0005"),
        Autor("George Orwell", "Novelista y ensayista britanico, conocido por sus distopias.", "Inglaterra",
              ["1984", "Rebelion en la granja"],
              ["Premio Hugo Retrospectivo"], autor_id="AUT-0006"),
        Autor("Gabriela Mistral", "Poetisa chilena, premio Nobel de Literatura 1945.", "Chile",
              ["Desolacion", "Tala", "Lagar"],
              ["Premio Nobel de Literatura"], autor_id="AUT-0007"),
        Autor("Julio Verne", "Escritor frances, pionero de la ciencia ficcion moderna.", "Francia",
              ["Veinte mil leguas de viaje submarino", "Viaje al centro de la Tierra", "La vuelta al mundo en 80 dias"],
              [], autor_id="AUT-0008"),
        Autor("Laura Esquivel", "Escritora mexicana, conocida por su realismo magico culinario.", "Mexico",
              ["Como agua para chocolate", "La ley del amor"],
              [], autor_id="AUT-0009"),
        Autor("Edgar Allan Poe", "Escritor y poeta estadounidense, maestro del relato de terror.", "Estados Unidos",
              ["El cuervo y otros poemas", "Los crimenes de la calle Morgue", "El gato negro"],
              [], autor_id="AUT-0010"),
    ]

    for a in autores_data:
        errs = a.validar()
        if errs:
            print(f"  Error en autor '{a.nombre}': {errs}")

    db.autores.insert_many([a.to_dict() for a in autores_data])
    print(f"  OK {len(autores_data)} autores insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 2. LIBROS (LIB-0001 al LIB-0025)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando libros...")

    AUTORES = {
        a.nombre: {"autor_id": a.autor_id, "name": a.nombre, "nacionalidad": a.nacionalidad}
        for a in autores_data
    }

    libros_data = [
        Libro("Cien anos de soledad", AUTORES["Gabriel Garcia Marquez"], "ficcion",
              "Editorial Sudamericana", 1967, "es", "fisico", "La historia de la familia Buendia en Macondo.", libro_id="LIB-0001"),
        Libro("El amor en los tiempos del colera", AUTORES["Gabriel Garcia Marquez"], "romance",
              "Oveja Negra", 1985, "es", "fisico", "Un amor que espera mas de medio siglo.", libro_id="LIB-0002"),
        Libro("Orgullo y prejuicio", AUTORES["Jane Austen"], "romance",
              "Thomas Egerton", 1813, "en", "fisico", "Elizabeth Bennet y el senor Darcy en la Inglaterra rural.", libro_id="LIB-0003"),
        Libro("Sentido y sensibilidad", AUTORES["Jane Austen"], "romance",
              "Thomas Egerton", 1811, "en", "digital", "Las hermanas Dashwood y el amor.", libro_id="LIB-0004"),
        Libro("Fundacion", AUTORES["Isaac Asimov"], "ciencia ficcion",
              "Gnome Press", 1951, "en", "fisico", "El imperio galactico y la psicohistoria.", libro_id="LIB-0005"),
        Libro("Yo, robot", AUTORES["Isaac Asimov"], "ciencia ficcion",
              "Gnome Press", 1950, "en", "digital", "Las tres leyes de la robotica en accion.", libro_id="LIB-0006"),
        Libro("La casa de los espiritus", AUTORES["Isabel Allende"], "ficcion",
              "Plaza & Janes", 1982, "es", "fisico", "La saga de la familia Trueba.", libro_id="LIB-0007"),
        Libro("El hobbit", AUTORES["J.R.R. Tolkien"], "fantasia",
              "George Allen & Unwin", 1937, "en", "fisico", "Bilbo Bolson y el tesoro del dragon Smaug.", libro_id="LIB-0008"),
        Libro("El senor de los anillos", AUTORES["J.R.R. Tolkien"], "fantasia",
              "George Allen & Unwin", 1954, "en", "fisico", "La comunidad del anillo en la Tierra Media.", libro_id="LIB-0009"),
        Libro("1984", AUTORES["George Orwell"], "ciencia ficcion",
              "Secker & Warburg", 1949, "en", "fisico", "El Gran Hermano te observa en Oceania.", libro_id="LIB-0010"),
        Libro("Rebelion en la granja", AUTORES["George Orwell"], "ficcion",
              "Secker & Warburg", 1945, "en", "digital", "Los animales se rebelan contra el granjero Jones.", libro_id="LIB-0011"),
        Libro("Desolacion", AUTORES["Gabriela Mistral"], "poesia",
              "Instituto de las Espanas", 1922, "es", "fisico", "Primer gran poemario de Gabriela Mistral.", libro_id="LIB-0012"),
        Libro("Veinte mil leguas de viaje submarino", AUTORES["Julio Verne"], "ciencia ficcion",
              "Pierre-Jules Hetzel", 1870, "fr", "digital", "El capitan Nemo y el Nautilus.", libro_id="LIB-0013"),
        Libro("Viaje al centro de la Tierra", AUTORES["Julio Verne"], "ciencia ficcion",
              "Pierre-Jules Hetzel", 1864, "fr", "fisico", "El profesor Lidenbrock y su expedicion.", libro_id="LIB-0014"),
        Libro("Como agua para chocolate", AUTORES["Laura Esquivel"], "romance",
              "Planeta", 1989, "es", "fisico", "Tita y su cocina magica en la Revolucion Mexicana.", libro_id="LIB-0015"),
        Libro("El cuervo y otros poemas", AUTORES["Edgar Allan Poe"], "poesia",
              "Wiley & Putnam", 1845, "en", "digital", "Poemas oscuros del maestro del terror.", libro_id="LIB-0016"),
        Libro("Los crimenes de la calle Morgue", AUTORES["Edgar Allan Poe"], "misterio",
              "Graham's Magazine", 1841, "en", "fisico", "El primer relato de detectives moderno.", libro_id="LIB-0017"),
        Libro("El fin de la eternidad", AUTORES["Isaac Asimov"], "ciencia ficcion",
              "Doubleday", 1955, "en", "digital", "El manipulador del tiempo y sus dilemas.", libro_id="LIB-0018"),
        Libro("Emma", AUTORES["Jane Austen"], "romance",
              "John Murray", 1815, "en", "fisico", "Emma Woodhouse, una casamentera en apuros.", libro_id="LIB-0019"),
        Libro("Cronica de una muerte anunciada", AUTORES["Gabriel Garcia Marquez"], "misterio",
              "La Oveja Negra", 1981, "es", "fisico", "Un asesinato que todos sabian que ocurriria.", libro_id="LIB-0020"),
        Libro("Eva Luna", AUTORES["Isabel Allende"], "ficcion",
              "Plaza & Janes", 1987, "es", "digital", "Eva Luna cuenta su historia de amor y libertad.", libro_id="LIB-0021"),
        Libro("El Silmarillion", AUTORES["J.R.R. Tolkien"], "fantasia",
              "George Allen & Unwin", 1977, "en", "fisico", "La mitologia completa de la Tierra Media.", libro_id="LIB-0022"),
        Libro("La vuelta al mundo en 80 dias", AUTORES["Julio Verne"], "ficcion",
              "Pierre-Jules Hetzel", 1872, "fr", "fisico", "Phileas Fogg y su apuesta alrededor del mundo.", libro_id="LIB-0023"),
        Libro("Persuasion", AUTORES["Jane Austen"], "romance",
              "John Murray", 1817, "en", "digital", "Anne Elliot y el capitan Wentworth.", libro_id="LIB-0024"),
        Libro("Tala", AUTORES["Gabriela Mistral"], "poesia",
              "Editorial Sur", 1938, "es", "fisico", "Poemario que consolida su voz lirica.", libro_id="LIB-0025"),
    ]

    for l in libros_data:
        errs = l.validar()
        if errs:
            print(f"  Error en libro '{l.titulo}': {errs}")

    db.libros.insert_many([l.to_dict() for l in libros_data])
    print(f"  OK {len(libros_data)} libros insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 3. USUARIOS (USR-0001 al USR-0008)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando usuarios...")
    usuarios_data = [
        Usuario("Carlos Mendoza", "carlos.mendoza@email.com", "premium",
                preferencias=["ciencia ficcion", "fantasia", "ficcion"], usuario_id="USR-0001"),
        Usuario("Maria Perez", "maria.perez@email.com", "basica",
                preferencias=["romance", "poesia"], usuario_id="USR-0002"),
        Usuario("Juan Gonzalez", "juan.gonzalez@email.com", "estudiante",
                preferencias=["fantasia", "ciencia ficcion", "terror"], usuario_id="USR-0003"),
        Usuario("Ana Romero", "ana.romero@email.com", "premium",
                preferencias=["misterio", "ficcion"], usuario_id="USR-0004"),
        Usuario("Luis Torres", "luis.torres@email.com", "basica",
                preferencias=["historia", "biografia"], usuario_id="USR-0005"),
        Usuario("Sofia Ramirez", "sofia.ramirez@email.com", "estudiante",
                preferencias=["poesia", "arte", "romance"], usuario_id="USR-0006"),
        Usuario("Diego Castillo", "diego.castillo@email.com", "premium",
                preferencias=["ciencia ficcion", "tecnologia", "filosofia"], usuario_id="USR-0007"),
        Usuario("Valentina Ortiz", "valentina.ortiz@email.com", "basica",
                preferencias=["terror", "misterio", "thriller"], usuario_id="USR-0008"),
    ]

    for u in usuarios_data:
        errs = u.validar()
        if errs:
            print(f"  Error en usuario '{u.nombre}': {errs}")

    db.usuarios.insert_many([u.to_dict() for u in usuarios_data])
    print(f"  OK {len(usuarios_data)} usuarios insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 4. PRESTAMOS (PRE-0001 al PRE-0015)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando prestamos...")
    now = datetime.now(timezone.utc)

    user_membresia = {u.usuario_id: u.membresia for u in usuarios_data}

    prestamos_config = [
        ("USR-0001", "LIB-0001", "activo", 0, None),
        ("USR-0001", "LIB-0006", "activo", 0, None),
        ("USR-0002", "LIB-0003", "devuelto", -2, -16),
        ("USR-0002", "LIB-0004", "activo", 0, None),
        ("USR-0003", "LIB-0008", "activo", 0, None),
        ("USR-0003", "LIB-0009", "activo", 0, None),
        ("USR-0004", "LIB-0020", "devuelto", -5, -35),
        ("USR-0004", "LIB-0017", "activo", 0, None),
        ("USR-0005", "LIB-0010", "vencido", -16, None),
        ("USR-0006", "LIB-0012", "activo", 0, None),
        ("USR-0006", "LIB-0015", "activo", 0, None),
        ("USR-0007", "LIB-0005", "activo", 0, None),
        ("USR-0007", "LIB-0018", "activo", 0, None),
        ("USR-0008", "LIB-0016", "devuelto", -10, -24),
        ("USR-0008", "LIB-0017", "devuelto", -3, -17),
    ]

    user_map = {u.usuario_id: u for u in usuarios_data}
    libro_map = {l.libro_id: l for l in libros_data}

    libros_no_disponibles = set()

    for i, (uid, lid, estado, dias_offset, dev_dias_offset) in enumerate(prestamos_config):
        membresia = user_membresia[uid]
        duracion = DURACION_POR_MEMBRESIA.get(membresia, 14)

        prestamo_id = f"PRE-{i + 1:04d}"

        if estado == "vencido":
            inicio = now - timedelta(days=duracion + 2)
            fin = inicio + timedelta(days=duracion)
        elif dias_offset < 0:
            inicio = now - timedelta(days=-dias_offset)
            fin = inicio + timedelta(days=duracion)
        else:
            inicio = now
            fin = inicio + timedelta(days=duracion)

        usuario_ref = {
            "usuario_id": uid,
            "nombre": user_map[uid].nombre,
            "correo": user_map[uid].correo,
        }
        libro_ref = {
            "libro_id": lid,
            "titulo": libro_map[lid].titulo,
            "autor": libro_map[lid].autor,
        }

        prestamo = Prestamo(
            usuario=usuario_ref, libro=libro_ref,
            fecha_inicio=inicio, fecha_fin=fin,
            estado=estado, prestamo_id=prestamo_id,
        )

        if estado == "devuelto" and dev_dias_offset is not None:
            prestamo.fecha_devolucion = fin + timedelta(days=dev_dias_offset)

        errs = prestamo.validar()
        if errs:
            print(f"  Error en prestamo (user {uid}, libro {lid}): {errs}")

        db.prestamos.insert_one(prestamo.to_dict())

        if estado in ("activo", "vencido"):
            libros_no_disponibles.add(lid)

        db.usuarios.update_one(
            {"usuario_id": uid},
            {"$addToSet": {"historial": prestamo_id}}
        )

    print(f"  OK {len(prestamos_config)} prestamos insertados.")

    if libros_no_disponibles:
        db.libros.update_many(
            {"libro_id": {"$in": list(libros_no_disponibles)}},
            {"$set": {"disponible": False}}
        )
        print(f"  OK {len(libros_no_disponibles)} libros marcados como no disponibles.")

    # ══════════════════════════════════════════════════════════════════
    # 5. RESENAS (RES-0001 al RES-0020)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando resenas...")
    resenas_config = [
        ("USR-0001", "LIB-0001", 5, "Una obra maestra absoluta. Garcia Marquez en su maximo esplendor."),
        ("USR-0001", "LIB-0002", 4, "Historia de amor conmovedora y atemporal."),
        ("USR-0001", "LIB-0006", 5, "Asimov define la ciencia ficcion moderna."),
        ("USR-0002", "LIB-0003", 5, "El romance mas iconico de la literatura inglesa."),
        ("USR-0002", "LIB-0004", 4, "Hermosa historia de hermanas y amor."),
        ("USR-0002", "LIB-0015", 5, "Realismo magico con sabores mexicanos."),
        ("USR-0003", "LIB-0008", 5, "El inicio de la mejor aventura fantastica."),
        ("USR-0003", "LIB-0009", 5, "La obra cumbre de la fantasia epica."),
        ("USR-0003", "LIB-0007", 4, "Una saga familiar fascinante."),
        ("USR-0004", "LIB-0020", 5, "Intriga, honor y tragedia en un pueblo costero."),
        ("USR-0004", "LIB-0017", 4, "El origen del genero detectivesco."),
        ("USR-0005", "LIB-0010", 5, "Profetica y escalofriante. Mas vigente que nunca."),
        ("USR-0005", "LIB-0011", 4, "Satira politica brillante y atemporal."),
        ("USR-0006", "LIB-0012", 5, "Poesia que rompe el alma. Gabriela Mistral es unica."),
        ("USR-0006", "LIB-0025", 4, "Madurez poetica de una voz inconfundible."),
        ("USR-0006", "LIB-0015", 5, "Tita cocina con amor y magia."),
        ("USR-0007", "LIB-0005", 5, "La psicohistoria es uno de los conceptos mas brillantes de la ciencia ficcion."),
        ("USR-0007", "LIB-0006", 5, "Las tres leyes de la robotica cambiaron todo."),
        ("USR-0008", "LIB-0016", 4, "Poe, el maestro de lo macabro en su mejor expresion."),
        ("USR-0008", "LIB-0017", 5, "El nacimiento de la novela detectivesca."),
    ]

    for i, (uid, lid, cal, com) in enumerate(resenas_config):
        resena_id = f"RES-{i + 1:04d}"
        usuario_ref = {
            "usuario_id": uid,
            "nombre": user_map[uid].nombre,
            "correo": user_map[uid].correo,
        }
        libro_ref = {
            "libro_id": lid,
            "titulo": libro_map[lid].titulo,
        }
        resena = Resena(
            usuario=usuario_ref, libro=libro_ref,
            calificacion=cal, comentario=com,
            resena_id=resena_id,
        )
        errs = resena.validar()
        if errs:
            print(f"  Error en resena (user {uid}, libro {lid}): {errs}")
        db.resenas.insert_one(resena.to_dict())

    print(f"  OK {len(resenas_config)} resenas insertadas.")

    # Calcular estadisticas de resenas por libro
    from collections import defaultdict
    stats = defaultdict(lambda: {"suma": 0, "total": 0})
    for _, lid, cal, _ in resenas_config:
        stats[lid]["suma"] += cal
        stats[lid]["total"] += 1

    for libro in libros_data:
        s = stats.get(libro.libro_id)
        if s and s["total"] > 0:
            libro.estadisticas = {
                "promedioCalificacion": round(s["suma"] / s["total"], 1),
                "totalResenas": s["total"]
            }
        else:
            libro.estadisticas = {"promedioCalificacion": 0, "totalResenas": 0}
        db.libros.update_one(
            {"libro_id": libro.libro_id},
            {"$set": {"estadisticas": libro.estadisticas}}
        )

    print("  OK estadisticas de libros actualizadas.")

    db.counters.insert_many([
        {"_id": "autores", "seq": 10},
        {"_id": "libros", "seq": 25},
        {"_id": "usuarios", "seq": 8},
        {"_id": "prestamos", "seq": 15},
        {"_id": "resenas", "seq": 20},
    ])
    print("  OK contadores inicializados.")

    print("\n" + "=" * 60)
    print("  POBLACION COMPLETADA")
    print("=" * 60)
    print(f"  {db.autores.count_documents({})} autores")
    print(f"  {db.libros.count_documents({})} libros")
    print(f"  {db.usuarios.count_documents({})} usuarios")
    print(f"  {db.prestamos.count_documents({})} prestamos")
    print(f"  {db.resenas.count_documents({})} resenas")
    print("=" * 60)


if __name__ == "__main__":
    poblar()
