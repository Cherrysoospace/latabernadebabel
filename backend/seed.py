import random
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from config import get_db
from models.autor_model import Autor
from models.libro_model import Libro, GENEROS_VALIDOS, FORMATOS_VALIDOS, IDIOMAS_VALIDOS
from models.usuario_model import Usuario
from models.prestamo_model import Prestamo, DURACION_POR_MEMBRESIA, ESTADOS_VALIDOS
from models.resena_model import Resena

# ──────────────────────────────────────────────────────────────────────────────
# SEMILLA ALEATORIA  (reproducible)
# ──────────────────────────────────────────────────────────────────────────────
random.seed(42)

# ══════════════════════════════════════════════════════════════════════════════
# CATALOGOS DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

AUTORES_CATALOG = [
    # (nombre, biografia, nacionalidad, obras, premios)
    ("Gabriel Garcia Marquez", "Escritor colombiano, premio Nobel de Literatura 1982.", "Colombia",
     ["Cien anos de soledad", "El amor en los tiempos del colera", "Cronica de una muerte anunciada", "El coronel no tiene quien le escriba"],
     ["Premio Nobel de Literatura", "Premio Romulo Gallegos"]),
    ("Jane Austen", "Novelista inglesa, pionera de la novela moderna.", "Inglaterra",
     ["Orgullo y prejuicio", "Sentido y sensibilidad", "Emma", "Persuasion", "Northanger Abbey"],
     []),
    ("Isaac Asimov", "Escritor y bioquimico ruso-estadounidense, maestro de la ciencia ficcion.", "Estados Unidos",
     ["Fundacion", "Yo robot", "El fin de la eternidad", "Los propios dioses", "El hombre bicentenario"],
     ["Premio Hugo", "Premio Nebula", "Premio Locus"]),
    ("Isabel Allende", "Escritora chilena, autora de best-sellers internacionales.", "Chile",
     ["La casa de los espiritus", "Eva Luna", "Paula", "El viento conoce mi nombre", "Ripper"],
     ["Premio Nacional de Literatura de Chile", "Premio Gabriela Mistral"]),
    ("J.R.R. Tolkien", "Filologo y escritor britanico, padre de la literatura fantastica moderna.", "Inglaterra",
     ["El hobbit", "El senor de los anillos", "El Silmarillion", "Las dos torres", "El retorno del rey"],
     ["Medalla de la Orden del Imperio Britanico"]),
    ("George Orwell", "Novelista y ensayista britanico, conocido por sus distopias.", "Inglaterra",
     ["1984", "Rebelion en la granja", "Sin blanca en Paris y Londres", "Homenaje a Cataluna"],
     ["Premio Hugo Retrospectivo"]),
    ("Gabriela Mistral", "Poetisa chilena, premio Nobel de Literatura 1945.", "Chile",
     ["Desolacion", "Tala", "Lagar", "Sonetos de la muerte"],
     ["Premio Nobel de Literatura", "Premio Nacional de Literatura de Chile"]),
    ("Julio Verne", "Escritor frances, pionero de la ciencia ficcion moderna.", "Francia",
     ["Veinte mil leguas de viaje submarino", "Viaje al centro de la Tierra", "La vuelta al mundo en 80 dias", "De la Tierra a la Luna"],
     ["Gran Premio de la Sociedad Geografica de Francia"]),
    ("Laura Esquivel", "Escritora mexicana, conocida por su realismo magico culinario.", "Mexico",
     ["Como agua para chocolate", "La ley del amor", "Intimas suculencias"],
     ["ARIEL de Oro"]),
    ("Edgar Allan Poe", "Escritor y poeta estadounidense, maestro del relato de terror.", "Estados Unidos",
     ["El cuervo y otros poemas", "Los crimenes de la calle Morgue", "El gato negro", "La caida de la casa Usher"],
     []),
    ("Mario Vargas Llosa", "Escritor peruano, premio Nobel de Literatura 2010.", "Peru",
     ["La ciudad y los perros", "La fiesta del chivo", "Conversacion en la catedral", "El paraiso en la otra esquina"],
     ["Premio Nobel de Literatura", "Premio Cervantes"]),
    ("Pablo Neruda", "Poeta y diplomatico chileno, premio Nobel de Literatura 1971.", "Chile",
     ["Veinte poemas de amor", "Canto general", "Residencia en la tierra", "Odas elementales"],
     ["Premio Nobel de Literatura", "Premio Stalin de la Paz"]),
    ("Octavio Paz", "Escritor y diplomatico mexicano, premio Nobel de Literatura 1990.", "Mexico",
     ["El laberinto de la soledad", "Piedra de sol", "El arco y la lira", "Conjunciones y disyunciones"],
     ["Premio Nobel de Literatura", "Premio Cervantes"]),
    ("Fyodor Dostoevsky", "Escritor ruso del siglo XIX, maestro del realismo psicologico.", "Rusia",
     ["Crimen y castigo", "El idiota", "Los hermanos Karamazov", "El jugador", "Memorias del subsuelo"],
     []),
    ("Leo Tolstoi", "Escritor ruso, uno de los grandes maestros de la novela realista.", "Rusia",
     ["Guerra y paz", "Anna Karenina", "La muerte de Ivan Ilyich", "Resurreccion"],
     []),
    ("Franz Kafka", "Escritor checo de habla alemana, referente del absurdismo y el existencialismo.", "Republica Checa",
     ["La metamorfosis", "El proceso", "El castillo", "En la colonia penitenciaria"],
     []),
    ("Virginia Woolf", "Escritora britanica, figura central del modernismo literario.", "Inglaterra",
     ["Mrs Dalloway", "Al faro", "Las olas", "Una habitacion propia", "Orlando"],
     []),
    ("Ernest Hemingway", "Novelista estadounidense, premio Nobel de Literatura 1954.", "Estados Unidos",
     ["El viejo y el mar", "Por quien doblan las campanas", "Adios a las armas", "El sol tambien sale"],
     ["Premio Nobel de Literatura", "Premio Pulitzer"]),
    ("Haruki Murakami", "Escritor japones de fama mundial.", "Japon",
     ["Tokio Blues", "Kafka en la orilla", "La caza del carnero salvaje", "Cronica del pajaro que da cuerda al mundo"],
     ["Premio Franz Kafka", "Premio Jerusalem"]),
    ("Simone de Beauvoir", "Escritora y filosofa francesa, referente del feminismo.", "Francia",
     ["El segundo sexo", "Los mandarines", "La mujer rota", "Memorias de una joven formal"],
     ["Premio Goncourt"]),
    ("Gabriel Zaid", "Ensayista y poeta mexicano, figura de la cultura literaria latinoamericana.", "Mexico",
     ["Cuestionario", "Leer poesia", "Los demasiados libros", "El progreso improductivo"],
     ["Premio Xavier Villaurrutia"]),
    ("Albert Camus", "Escritor y filosofo frances, premio Nobel de Literatura 1957.", "Francia",
     ["El extranjero", "La peste", "El mito de Sisifo", "La caida", "El exilio y el reino"],
     ["Premio Nobel de Literatura"]),
    ("Jorge Luis Borges", "Escritor argentino, referente universal de la literatura fantastica.", "Argentina",
     ["Ficciones", "El Aleph", "El jardin de senderos que se bifurcan", "Laberintos"],
     ["Premio Cervantes", "Premio Internacional Formentor"]),
    ("Toni Morrison", "Novelista estadounidense, premio Nobel de Literatura 1993.", "Estados Unidos",
     ["Beloved", "La cancion de Solomon", "Ojo de pez", "Jazz", "Un don"],
     ["Premio Nobel de Literatura", "Premio Pulitzer"]),
    ("Chinua Achebe", "Novelista nigeriano, padre de la literatura africana moderna.", "Nigeria",
     ["Todo se desmorona", "La flecha de Dios", "No longer at ease", "Anthills of the Savannah"],
     ["Premio Man Booker Internacional"]),
    ("Gabriel Mistral", "Reconocida poetisa latinoamericana.", "Chile",
     ["Antologia poetica", "Recados", "Motivos de San Francisco"],
     ["Premio Nacional de Literatura"]),
    ("Carlos Fuentes", "Novelista y ensayista mexicano, figura del boom latinoamericano.", "Mexico",
     ["La muerte de Artemio Cruz", "Terra Nostra", "Cambio de piel", "Gringo viejo"],
     ["Premio Cervantes", "Premio Romulo Gallegos"]),
    ("Alejo Carpentier", "Escritor cubano, iniciador del realismo magico.", "Cuba",
     ["El reino de este mundo", "Los pasos perdidos", "El siglo de las luces", "Concierto barroco"],
     ["Premio Cervantes"]),
    ("Juan Rulfo", "Escritor mexicano, referente de la literatura hispanoamericana.", "Mexico",
     ["Pedro Paramo", "El llano en llamas", "El gallo de oro"],
     ["Premio Nacional de Literatura de Mexico", "Premio Principe de Asturias"]),
    ("Horacio Quiroga", "Cuentista uruguayo, maestro del relato de terror y la selva.", "Uruguay",
     ["Cuentos de amor de locura y de muerte", "Los desterrados", "Anaconda", "El desierto"],
     []),
    ("Jhumpa Lahiri", "Escritora estadounidense de origen indio, premio Pulitzer.", "Estados Unidos",
     ["El interprete de emociones", "La namesake", "El tren de la noche", "Inmeabile"],
     ["Premio Pulitzer", "PEN/Hemingway Award"]),
    ("Chimamanda Ngozi Adichie", "Escritora nigeriana, referente del feminismo contemporaneo.", "Nigeria",
     ["Americanah", "Medio sol amarillo", "La flor purpura", "El peligro de la historia unica"],
     ["Premio Orange", "Premio Commonwealth Writers"]),
    ("Italo Calvino", "Escritor italiano, maestro del realismo magico y la metaficcion.", "Italia",
     ["Si una noche de invierno un viajero", "Las ciudades invisibles", "El baron rampante", "El caballero inexistente"],
     ["Premio Bagutta", "Premio Feltrinelli"]),
    ("Umberto Eco", "Novelista y semiologo italiano.", "Italia",
     ["El nombre de la rosa", "El pendulo de Foucault", "La isla del dia de antes", "El cementerio de Praga"],
     ["Premio Strega"]),
    ("Yukio Mishima", "Novelista y dramaturgo japones.", "Japon",
     ["El pabellon de oro", "Confesiones de una mascara", "El mar de la fertilidad", "Sed de amor"],
     ["Premio Shincho"]),
    ("Naguib Mahfouz", "Novelista egipcio, premio Nobel de Literatura 1988.", "Egipto",
     ["La trilogia de El Cairo", "Hijos de nuestro barrio", "El callejon de los milagros"],
     ["Premio Nobel de Literatura"]),
    ("Clarice Lispector", "Escritora brasilena, figura del modernismo literario latinoamericano.", "Brasil",
     ["La pasion segun G.H.", "La hora de la estrella", "Agua viva", "Cerca del corazon salvaje"],
     ["Premio Golfinho de Ouro"]),
    ("Roberto Bolano", "Escritor chileno, referente de la literatura latinoamericana contemporanea.", "Chile",
     ["Los detectives salvajes", "2666", "Estrella distante", "La literatura nazi en America"],
     ["Premio Herralde", "Premio Romulo Gallegos"]),
    ("Elena Ferrante", "Novelista italiana de identidad desconocida.", "Italia",
     ["La amiga estupenda", "Un mal nombre", "Las deudas del cuerpo", "La nina perdida"],
     []),
    ("Patrick Modiano", "Novelista frances, premio Nobel de Literatura 2014.", "Francia",
     ["En el cafe de la juventud perdida", "La calle de las tiendas oscuras", "Dora Bruder"],
     ["Premio Nobel de Literatura", "Premio Goncourt"]),
    ("Mo Yan", "Novelista chino, premio Nobel de Literatura 2012.", "China",
     ["Sorgo rojo", "Grandes pechos amplias caderas", "La republica del vino", "El suplicio del aligator"],
     ["Premio Nobel de Literatura"]),
    ("Svetlana Alexievich", "Escritora bielorrusa, premio Nobel de Literatura 2015.", "Bielorrusia",
     ["Voces de Chernobil", "La guerra no tiene rostro de mujer", "Los ultimos testigos", "El fin del homo sovieticus"],
     ["Premio Nobel de Literatura"]),
    ("Kazuo Ishiguro", "Novelista britanico de origen japones, premio Nobel de Literatura 2017.", "Japon",
     ["Los restos del dia", "Nunca me abandones", "El gigante enterrado", "Un artista del mundo flotante"],
     ["Premio Nobel de Literatura", "Premio Man Booker"]),
    ("Olga Tokarczuk", "Novelista polaca, premio Nobel de Literatura 2018.", "Polonia",
     ["Los errantes", "Los libros de Jakob", "En el jardin del ogro", "El alma perdida"],
     ["Premio Nobel de Literatura", "Premio Man Booker Internacional"]),
    ("Han Kang", "Escritora surcoreana, premio Nobel de Literatura 2024.", "Corea del Sur",
     ["La vegetariana", "Actos humanos", "La clase de griego", "Blanco"],
     ["Premio Nobel de Literatura", "Premio Man Booker Internacional"]),
    ("Donna Tartt", "Novelista estadounidense.", "Estados Unidos",
     ["El secreto", "El jilguero", "La leyenda del maestro"],
     ["Premio Pulitzer"]),
    ("Colm Toibin", "Novelista irlandes.", "Irlanda",
     ["Brooklyn", "El testamento de Maria", "El nido"],
     ["Premio Costa Novel Award", "Premio IMPAC Dublin"]),
    ("Jonathan Franzen", "Novelista estadounidense.", "Estados Unidos",
     ["Las correcciones", "Libertad", "Pureza", "Crossroads"],
     ["Premio National Book Award"]),
    ("Zadie Smith", "Novelista y ensayista britanica.", "Inglaterra",
     ["Dientes blancos", "NW", "El salon de belleza de bano", "El estado de libertad"],
     ["Premio Whitbread Novel Award", "Premio Orange"]),
    ("Salman Rushdie", "Novelista britanico-indio, premio del Booker of Bookers.", "India",
     ["Hijos de la medianoche", "Los versos satanicos", "La ultima suspension", "El moro"],
     ["Premio Man Booker", "Premio Whitbread"]),
]

LIBROS_CATALOG = [
    # (titulo, nombre_autor, genero, editorial, anio, idioma, formato, descripcion)
    ("Cien anos de soledad", "Gabriel Garcia Marquez", "ficcion", "Editorial Sudamericana", 1967, "es", "fisico",
     "La historia de la familia Buendia en el pueblo de Macondo a lo largo de siete generaciones."),
    ("El amor en los tiempos del colera", "Gabriel Garcia Marquez", "romance", "Oveja Negra", 1985, "es", "fisico",
     "Un amor que espera mas de medio siglo para consumarse."),
    ("Cronica de una muerte anunciada", "Gabriel Garcia Marquez", "misterio", "La Oveja Negra", 1981, "es", "fisico",
     "Un asesinato que todos sabian que ocurriria pero nadie pudo evitar."),
    ("El coronel no tiene quien le escriba", "Gabriel Garcia Marquez", "ficcion", "Era", 1961, "es", "digital",
     "Un viejo coronel espera durante anos una pension que nunca llega."),
    ("Orgullo y prejuicio", "Jane Austen", "romance", "Thomas Egerton", 1813, "en", "fisico",
     "Elizabeth Bennet y el senor Darcy navegan el amor en la Inglaterra rural del siglo XIX."),
    ("Sentido y sensibilidad", "Jane Austen", "romance", "Thomas Egerton", 1811, "en", "digital",
     "Las hermanas Dashwood y su busqueda del amor y la estabilidad economica."),
    ("Emma", "Jane Austen", "romance", "John Murray", 1815, "en", "fisico",
     "Emma Woodhouse, una casamentera que siempre se equivoca en sus propios asuntos del corazon."),
    ("Persuasion", "Jane Austen", "romance", "John Murray", 1817, "en", "digital",
     "Anne Elliot y el capitan Wentworth se reencuentran anos despues de una separacion dolorosa."),
    ("Northanger Abbey", "Jane Austen", "ficcion", "John Murray", 1818, "en", "fisico",
     "Una joven apasionada por las novelas goticas visita una abadia y deja volar su imaginacion."),
    ("Fundacion", "Isaac Asimov", "ciencia ficcion", "Gnome Press", 1951, "en", "fisico",
     "El fin del Imperio Galactico y el nacimiento de la Fundacion para preservar el conocimiento."),
    ("Yo robot", "Isaac Asimov", "ciencia ficcion", "Gnome Press", 1950, "en", "digital",
     "Historias sobre robots y las tres leyes de la robotica que definieron un genero."),
    ("El fin de la eternidad", "Isaac Asimov", "ciencia ficcion", "Doubleday", 1955, "en", "digital",
     "Una organizacion controla el tiempo para maximizar el bienestar de la humanidad."),
    ("Los propios dioses", "Isaac Asimov", "ciencia ficcion", "Doubleday", 1972, "en", "fisico",
     "Tres universos paralelos y la amenaza de una fuente de energia aparentemente perfecta."),
    ("El hombre bicentenario", "Isaac Asimov", "ciencia ficcion", "Doubleday", 1976, "en", "audiolibro",
     "Un robot anhela convertirse en humano a lo largo de dos siglos."),
    ("La casa de los espiritus", "Isabel Allende", "ficcion", "Plaza & Janes", 1982, "es", "fisico",
     "La saga de la familia Trueba a traves de generaciones marcadas por la magia y la historia."),
    ("Eva Luna", "Isabel Allende", "ficcion", "Plaza & Janes", 1987, "es", "digital",
     "Eva Luna cuenta su historia de amor y libertad en un pais latinoamericano ficticio."),
    ("Paula", "Isabel Allende", "biografia", "Plaza & Janes", 1994, "es", "fisico",
     "Autobiografia escrita como carta a su hija Paula, quien yacia en coma."),
    ("El viento conoce mi nombre", "Isabel Allende", "ficcion", "Plaza & Janes", 2023, "es", "digital",
     "Una novela sobre el exilio y la esperanza que une el Vienna de 1938 con el presente."),
    ("El hobbit", "J.R.R. Tolkien", "fantasia", "George Allen & Unwin", 1937, "en", "fisico",
     "Bilbo Bolson y su inesperada aventura con enanos y el dragon Smaug."),
    ("El senor de los anillos", "J.R.R. Tolkien", "fantasia", "George Allen & Unwin", 1954, "en", "fisico",
     "La comunidad del anillo emprende su viaje para destruir el Anillo Unico en la Tierra Media."),
    ("El Silmarillion", "J.R.R. Tolkien", "fantasia", "George Allen & Unwin", 1977, "en", "fisico",
     "La mitologia completa de la Tierra Media y los origenes de los elfos, humanos y enanos."),
    ("Las dos torres", "J.R.R. Tolkien", "fantasia", "George Allen & Unwin", 1954, "en", "fisico",
     "Segunda parte de El senor de los anillos, donde la comunidad se divide."),
    ("El retorno del rey", "J.R.R. Tolkien", "fantasia", "George Allen & Unwin", 1955, "en", "audiolibro",
     "Conclusion epica de la trilogia con la batalla de los Campos del Pelennor."),
    ("1984", "George Orwell", "ciencia ficcion", "Secker & Warburg", 1949, "en", "fisico",
     "Winston Smith vive bajo el yugo del Gran Hermano en una sociedad totalitaria."),
    ("Rebelion en la granja", "George Orwell", "ficcion", "Secker & Warburg", 1945, "en", "digital",
     "Los animales de una granja se rebelan contra el granjero Jones en esta satira politica."),
    ("Desolacion", "Gabriela Mistral", "poesia", "Instituto de las Espanas", 1922, "es", "fisico",
     "Primer gran poemario de Gabriela Mistral, lleno de dolor, amor y espiritualidad."),
    ("Tala", "Gabriela Mistral", "poesia", "Editorial Sur", 1938, "es", "fisico",
     "Poemario que consolida la voz lirica inconfundible de Gabriela Mistral."),
    ("Lagar", "Gabriela Mistral", "poesia", "Editorial del Pacifico", 1954, "es", "digital",
     "Su ultimo libro de poemas publicado en vida, de profunda meditacion espiritual."),
    ("Veinte mil leguas de viaje submarino", "Julio Verne", "ciencia ficcion", "Pierre-Jules Hetzel", 1870, "fr", "digital",
     "El capitan Nemo y su submarino el Nautilus recorren los oceanos del mundo."),
    ("Viaje al centro de la Tierra", "Julio Verne", "ciencia ficcion", "Pierre-Jules Hetzel", 1864, "fr", "fisico",
     "El profesor Lidenbrock y su sobrino descienden al interior de la Tierra."),
    ("La vuelta al mundo en 80 dias", "Julio Verne", "ficcion", "Pierre-Jules Hetzel", 1872, "fr", "fisico",
     "Phileas Fogg apuesta que puede dar la vuelta al mundo en 80 dias."),
    ("De la Tierra a la Luna", "Julio Verne", "ciencia ficcion", "Pierre-Jules Hetzel", 1865, "fr", "audiolibro",
     "El Gun Club de Baltimore construye un canon gigante para enviar un proyectil a la Luna."),
    ("Como agua para chocolate", "Laura Esquivel", "romance", "Planeta", 1989, "es", "fisico",
     "Tita cocina con sus emociones y sus platos afectan magicamente a quienes los comen."),
    ("La ley del amor", "Laura Esquivel", "ficcion", "Planeta", 1995, "es", "digital",
     "Una novela con multimedia que mezcla ciencia ficcion, romance y musica."),
    ("El cuervo y otros poemas", "Edgar Allan Poe", "poesia", "Wiley & Putnam", 1845, "en", "digital",
     "Poemas oscuros del maestro del terror, encabezados por el celebre El Cuervo."),
    ("Los crimenes de la calle Morgue", "Edgar Allan Poe", "misterio", "Graham's Magazine", 1841, "en", "fisico",
     "El primer relato de detectives moderno de la historia, con C. Auguste Dupin."),
    ("El gato negro", "Edgar Allan Poe", "terror", "United States Magazine", 1843, "en", "digital",
     "Un hombre asesina a su esposa y a su gato, obsesionado por la culpa."),
    ("La caida de la casa Usher", "Edgar Allan Poe", "terror", "Burton's Magazine", 1839, "en", "fisico",
     "Una visita a la lugubre mansion de los Usher termina en tragedia y horror."),
    ("La ciudad y los perros", "Mario Vargas Llosa", "ficcion", "Seix Barral", 1963, "es", "fisico",
     "La vida brutal en un colegio militar de Lima y la destruccion de la inocencia."),
    ("La fiesta del chivo", "Mario Vargas Llosa", "historia", "Alfaguara", 2000, "es", "fisico",
     "La caida de la dictadura de Trujillo en Republica Dominicana."),
    ("Conversacion en la catedral", "Mario Vargas Llosa", "ficcion", "Seix Barral", 1969, "es", "digital",
     "Una conversacion de cuatro horas que recorre la corrupcion del Peru bajo Odria."),
    ("Veinte poemas de amor", "Pablo Neruda", "poesia", "Editorial Nascimento", 1924, "es", "fisico",
     "El poemario mas vendido de la literatura en lengua espanola."),
    ("Canto general", "Pablo Neruda", "poesia", "Talleres Graficos de la Nacion", 1950, "es", "fisico",
     "Una epica poetica sobre America Latina desde sus origenes hasta el siglo XX."),
    ("El laberinto de la soledad", "Octavio Paz", "filosofia", "Cuadernos Americanos", 1950, "es", "digital",
     "Ensayo sobre la identidad del mexicano y su soledad existencial."),
    ("Piedra de sol", "Octavio Paz", "poesia", "Tezontle", 1957, "es", "fisico",
     "Poema circular basado en el ciclo del planeta Venus en el calendario azteca."),
    ("Crimen y castigo", "Fyodor Dostoevsky", "ficcion", "The Russian Messenger", 1866, "ru", "fisico",
     "Raskolnikov comete un crimen y lucha con su conciencia en San Petersburgo."),
    ("El idiota", "Fyodor Dostoevsky", "ficcion", "The Russian Messenger", 1869, "ru", "digital",
     "El principe Myshkin regresa a Rusia y choca con la corrupcion de la sociedad."),
    ("Los hermanos Karamazov", "Fyodor Dostoevsky", "ficcion", "The Russian Messenger", 1880, "ru", "fisico",
     "El parricidio y sus consecuencias en una familia rusa del siglo XIX."),
    ("Guerra y paz", "Leo Tolstoi", "historia", "The Russian Messenger", 1869, "ru", "fisico",
     "La sociedad rusa durante las guerras napoleonicas narrada a traves de varias familias."),
    ("Anna Karenina", "Leo Tolstoi", "romance", "The Russian Messenger", 1878, "ru", "fisico",
     "La tragica historia de amor de Anna Karenina y el conde Vronsky en la Rusia zarista."),
    ("La metamorfosis", "Franz Kafka", "ficcion", "Kurt Wolff Verlag", 1915, "de", "digital",
     "Gregor Samsa se despierta convertido en un insecto gigante."),
    ("El proceso", "Franz Kafka", "ficcion", "Verlag Die Schmiede", 1925, "de", "fisico",
     "Josef K. es arrestado y juzgado sin conocer el cargo que se le imputa."),
    ("El castillo", "Franz Kafka", "ficcion", "Kurt Wolff Verlag", 1926, "de", "digital",
     "K. llega a una aldea para trabajar como agrimensor pero no puede acceder al castillo."),
    ("Mrs Dalloway", "Virginia Woolf", "ficcion", "Hogarth Press", 1925, "en", "fisico",
     "Un dia en la vida de Clarissa Dalloway mientras prepara una fiesta en el Londres de 1923."),
    ("Al faro", "Virginia Woolf", "ficcion", "Hogarth Press", 1927, "en", "digital",
     "La familia Ramsay y sus huespedes durante dos visitas a su casa en las Islas Hebrides."),
    ("Una habitacion propia", "Virginia Woolf", "no ficcion", "Hogarth Press", 1929, "en", "digital",
     "Ensayo sobre las condiciones necesarias para que la mujer pueda escribir ficcion."),
    ("El viejo y el mar", "Ernest Hemingway", "ficcion", "Scribner", 1952, "en", "fisico",
     "Santiago, un pescador cubano anciano, lucha durante dias con un gran pez espada."),
    ("Por quien doblan las campanas", "Ernest Hemingway", "historia", "Scribner", 1940, "en", "fisico",
     "Robert Jordan lucha con los republicanos durante la Guerra Civil Espanola."),
    ("Tokio Blues", "Haruki Murakami", "romance", "Kodansha", 1987, "ja", "fisico",
     "Watanabe recuerda su juventud en Tokio y los amores perdidos de su vida universitaria."),
    ("Kafka en la orilla", "Haruki Murakami", "fantasia", "Shinchosha", 2002, "ja", "digital",
     "Dos historias paralelas que se entrelazan de forma magica e inesperada."),
    ("El segundo sexo", "Simone de Beauvoir", "no ficcion", "Gallimard", 1949, "fr", "fisico",
     "Analisis existencialista de la opresion de la mujer y la construccion del genero femenino."),
    ("El extranjero", "Albert Camus", "ficcion", "Gallimard", 1942, "fr", "fisico",
     "Meursault mata a un hombre y afronta su juicio con una indiferencia que escandaliza."),
    ("La peste", "Albert Camus", "ficcion", "Gallimard", 1947, "fr", "fisico",
     "Una epidemia de peste azota la ciudad de Oran y pone a prueba el alma humana."),
    ("El mito de Sisifo", "Albert Camus", "filosofia", "Gallimard", 1942, "fr", "digital",
     "Ensayo filosofico sobre el absurdo y la rebelion del hombre ante su condicion."),
    ("Ficciones", "Jorge Luis Borges", "ficcion", "Sur", 1944, "es", "fisico",
     "Coleccion de cuentos que exploran laberintos, espejos, tiempo y el infinito."),
    ("El Aleph", "Jorge Luis Borges", "ficcion", "Losada", 1949, "es", "fisico",
     "Cuentos fantasticos que reflexionan sobre el tiempo, el espacio y la identidad."),
    ("Beloved", "Toni Morrison", "ficcion", "Alfred A. Knopf", 1987, "en", "fisico",
     "Sethe, una esclava liberada, es perseguida por el fantasma de su hija muerta."),
    ("La cancion de Solomon", "Toni Morrison", "ficcion", "Alfred A. Knopf", 1977, "en", "digital",
     "Un hombre del sur de Estados Unidos busca un tesoro familiar y su propia identidad."),
    ("Todo se desmorona", "Chinua Achebe", "ficcion", "William Heinemann", 1958, "en", "fisico",
     "La vida de Okonkwo, un guerrero igbo, durante la llegada del colonialismo britanico."),
    ("La muerte de Artemio Cruz", "Carlos Fuentes", "ficcion", "Fondo de Cultura Economica", 1962, "es", "fisico",
     "Un hombre poderoso recuerda su vida en sus ultimas horas, revelando la corrupcion del Mexico posrevolucionario."),
    ("Terra Nostra", "Carlos Fuentes", "ficcion", "Seix Barral", 1975, "es", "digital",
     "Vasta novela que recorre la historia de Espana y America Latina."),
    ("El reino de este mundo", "Alejo Carpentier", "ficcion", "Seix Barral", 1949, "es", "fisico",
     "La revolucion haitiana narrada con el realismo magico de lo real maravilloso."),
    ("Los pasos perdidos", "Alejo Carpentier", "ficcion", "Ediapsa", 1953, "es", "digital",
     "Un musicologo viaja al Amazonas y reflexiona sobre la civilizacion y la barbarie."),
    ("Pedro Paramo", "Juan Rulfo", "ficcion", "Fondo de Cultura Economica", 1955, "es", "fisico",
     "Juan Preciado viaja a Comala a buscar a su padre y encuentra un pueblo de muertos."),
    ("El llano en llamas", "Juan Rulfo", "ficcion", "Fondo de Cultura Economica", 1953, "es", "fisico",
     "Cuentos que retratan la violencia, la pobreza y el paisaje de Jalisco."),
    ("Cuentos de amor de locura y de muerte", "Horacio Quiroga", "terror", "Cooperativa Editorial Limitada", 1917, "es", "fisico",
     "Cuentos crudos y magistrales sobre la naturaleza salvaje y la muerte en la selva."),
    ("El interprete de emociones", "Jhumpa Lahiri", "ficcion", "Houghton Mifflin", 1999, "en", "fisico",
     "Nueve cuentos sobre la identidad y el dislocation de la diaspora india en Estados Unidos."),
    ("Americanah", "Chimamanda Ngozi Adichie", "ficcion", "Alfred A. Knopf", 2013, "en", "digital",
     "Ifemelu y Obinze se enamoran en Nigeria y luego sus vidas se separan por la emigracion."),
    ("Medio sol amarillo", "Chimamanda Ngozi Adichie", "historia", "Alfred A. Knopf", 2006, "en", "fisico",
     "La guerra de Biafra narrada a traves de tres personajes en los anos sesenta."),
    ("Si una noche de invierno un viajero", "Italo Calvino", "ficcion", "Einaudi", 1979, "it", "fisico",
     "El lector se convierte en personaje de esta novela experimental sobre la lectura."),
    ("Las ciudades invisibles", "Italo Calvino", "ficcion", "Einaudi", 1972, "it", "digital",
     "Marco Polo describe a Kublai Khan ciudades imaginarias de inquietante belleza."),
    ("El nombre de la rosa", "Umberto Eco", "misterio", "Bompiani", 1980, "it", "fisico",
     "Una serie de crimenes ocurre en una abadia medieval, investigada por el fraile Guillermo de Baskerville."),
    ("El pendulo de Foucault", "Umberto Eco", "ficcion", "Bompiani", 1988, "it", "digital",
     "Tres editores inventan una conspiracion universal y acaban creyendola ellos mismos."),
    ("El pabellon de oro", "Yukio Mishima", "ficcion", "Shincho", 1956, "ja", "fisico",
     "Un joven novicio quema el templo de oro de Kyoto, obsesionado por su belleza."),
    ("Los errantes", "Olga Tokarczuk", "ficcion", "Wydawnictwo Literackie", 2007, "de", "fisico",
     "Novela fragmentada sobre el viaje, el movimiento y la identidad humana."),
    ("La vegetariana", "Han Kang", "ficcion", "Changbi Publishers", 2007, "en", "fisico",
     "Una mujer decide dejar de comer carne con consecuencias devastadoras para su familia."),
    ("Actos humanos", "Han Kang", "historia", "Changbi Publishers", 2014, "en", "digital",
     "La masacre de Gwangju de 1980 narrada desde distintas perspectivas en el tiempo."),
    ("El jilguero", "Donna Tartt", "ficcion", "Little Brown", 2013, "en", "fisico",
     "Un nino sobrevive un atentado en un museo y escapa con un cuadro que cambia su vida."),
    ("El secreto", "Donna Tartt", "misterio", "Knopf", 1992, "en", "fisico",
     "Un grupo de estudiantes de griego en Vermont comete un crimen y guarda el secreto."),
    ("Brooklyn", "Colm Toibin", "ficcion", "Scribner", 2009, "en", "fisico",
     "Eilis Lacey emigra de Irlanda a Nueva York en los anos cincuenta y debe elegir entre dos mundos."),
    ("Las correcciones", "Jonathan Franzen", "ficcion", "Farrar Straus and Giroux", 2001, "en", "fisico",
     "La familia Lambert se reune una ultima Navidad y cada miembro enfrenta sus propias crisis."),
    ("Libertad", "Jonathan Franzen", "ficcion", "Farrar Straus and Giroux", 2010, "en", "digital",
     "La familia Berglund en el America del siglo XXI, atrapada entre ideales y deseos."),
    ("Dientes blancos", "Zadie Smith", "ficcion", "Hamish Hamilton", 2000, "en", "fisico",
     "Las familias Jones y Iqbal en el multicultural norte de Londres a lo largo de varias generaciones."),
    ("Hijos de la medianoche", "Salman Rushdie", "ficcion", "Jonathan Cape", 1981, "en", "fisico",
     "Los ninos nacidos en el momento de la independencia de India poseen poderes sobrenaturales."),
    ("Los versos satanicos", "Salman Rushdie", "ficcion", "Viking Press", 1988, "en", "digital",
     "Dos actores supervivientes de un atentado sufren transformaciones sobrenaturales."),
    ("El gigante enterrado", "Kazuo Ishiguro", "fantasia", "Faber and Faber", 2015, "en", "fisico",
     "Una pareja de ancianos en la Bretana Arturia busca a su hijo olvidado."),
    ("Los restos del dia", "Kazuo Ishiguro", "ficcion", "Faber and Faber", 1989, "en", "fisico",
     "Stevens, un mayordomo ingles, reflexiona sobre su vida de servicio durante un viaje."),
    ("Nunca me abandones", "Kazuo Ishiguro", "ciencia ficcion", "Faber and Faber", 2005, "en", "digital",
     "Los estudiantes de Hailsham descubren el oscuro proposito para el que fueron creados."),
    ("Voces de Chernobil", "Svetlana Alexievich", "no ficcion", "Ostozhye", 1997, "ru", "fisico",
     "Testimonios de supervivientes del desastre nuclear de Chernobil en 1986."),
    ("La guerra no tiene rostro de mujer", "Svetlana Alexievich", "no ficcion", "Mastatskaya Literatura", 1985, "ru", "digital",
     "Testimonios de las mujeres sovieticas que combatieron en la Segunda Guerra Mundial."),
    ("Los libros de Jakob", "Olga Tokarczuk", "historia", "Wydawnictwo Literackie", 2014, "de", "fisico",
     "La vida de Jakob Frank, un mesianismo del siglo XVIII en Europa Oriental."),
    ("La amiga estupenda", "Elena Ferrante", "ficcion", "E/O", 2011, "it", "fisico",
     "Elena y Lila crecen juntas en un barrio pobre de Naples en la posguerra italiana."),
    ("Un mal nombre", "Elena Ferrante", "ficcion", "E/O", 2012, "it", "digital",
     "Elena y Lila afrontan la adolescencia y la violencia del mundo de los hombres."),
    ("En el cafe de la juventud perdida", "Patrick Modiano", "ficcion", "Gallimard", 2007, "fr", "fisico",
     "Cuatro voces reconstruyen el paso de una misteriosa mujer llamada Louki por Paris."),
    ("Sorgo rojo", "Mo Yan", "historia", "People's Literature Publishing House", 1987, "zh", "fisico",
     "Una saga familiar en la China del siglo XX, marcada por la guerra y la pasion."),
    ("Grandes pechos amplias caderas", "Mo Yan", "historia", "People's Literature Publishing House", 1995, "zh", "digital",
     "La vida de una madre china a lo largo de las convulsiones del siglo XX."),
    ("La pasion segun GH", "Clarice Lispector", "ficcion", "Editora do Autor", 1964, "pt", "fisico",
     "Una mujer mata una cucaracha y el acto la lanza a una meditacion existencial."),
    ("La hora de la estrella", "Clarice Lispector", "ficcion", "Jose Olympio", 1977, "pt", "fisico",
     "La historia de Macabea, una joven nordestina pobre que vive en Rio de Janeiro."),
    ("Los detectives salvajes", "Roberto Bolano", "ficcion", "Anagrama", 1998, "es", "fisico",
     "Dos poetas mexicanos buscan a una poetisa desaparecida a traves de tres continentes."),
    ("2666", "Roberto Bolano", "ficcion", "Anagrama", 2004, "es", "fisico",
     "Novela monumental sobre los feminicidios en una ciudad fronteriza del norte de Mexico."),
    ("Estrella distante", "Roberto Bolano", "ficcion", "Anagrama", 1996, "es", "digital",
     "Un poeta aviador que escribe poemas en el cielo mientras comete crimenes de lesa humanidad."),
    ("La trilogia de El Cairo", "Naguib Mahfouz", "ficcion", "Dar Al-Hilal", 1956, "ar", "fisico",
     "La vida de la familia Al-Sayyid Ahmad Abd al-Jawad en El Cairo entre 1917 y 1944."),
    ("El callejon de los milagros", "Naguib Mahfouz", "ficcion", "Maktabat Misr", 1947, "ar", "fisico",
     "Las historias entrelazadas de los habitantes de un callejon del El Cairo historico."),
    ("Confesiones de una mascara", "Yukio Mishima", "ficcion", "Kawade Shobo", 1949, "ja", "digital",
     "Una novela autobiografica sobre un joven japones que oculta su homosexualidad."),
    ("Agua viva", "Clarice Lispector", "ficcion", "Artenova", 1973, "pt", "digital",
     "Un texto experimental a medio camino entre la pintura y la escritura."),
    ("La flecha de Dios", "Chinua Achebe", "ficcion", "William Heinemann", 1964, "en", "digital",
     "Ezeulu, sumo sacerdote de Ulu, enfrenta el colonialismo britanico en Nigeria."),
    ("No longer at ease", "Chinua Achebe", "ficcion", "William Heinemann", 1960, "en", "fisico",
     "Obi Okonkwo regresa de estudiar en Gran Bretana y no logra adaptarse a la sociedad nigeriana."),
    ("Residencia en la tierra", "Pablo Neruda", "poesia", "Cruz del Sur", 1933, "es", "fisico",
     "Poemas de gran densidad poetica escritos durante los anos de exilio de Neruda."),
    ("Odas elementales", "Pablo Neruda", "poesia", "Losada", 1954, "es", "digital",
     "Odas que celebran los objetos cotidianos con alegria y sencillez."),
    ("El arco y la lira", "Octavio Paz", "no ficcion", "Fondo de Cultura Economica", 1956, "es", "fisico",
     "Ensayo sobre la esencia de la poesia y la funcion del poeta en la sociedad."),
    ("El jardin de senderos que se bifurcan", "Jorge Luis Borges", "ficcion", "Sur", 1941, "es", "digital",
     "Cuentos que exploran el laberinto, el espionaje y los universos paralelos."),
    ("Laberintos", "Jorge Luis Borges", "ficcion", "New Directions", 1962, "es", "fisico",
     "Antologia de sus mejores cuentos y ensayos, traducidos para el publico anglosajono."),
    ("La flor purpura", "Chimamanda Ngozi Adichie", "ficcion", "Algonquin Books", 2003, "en", "fisico",
     "Kambili, una joven nigeriana, vive bajo el control obsesivo de un padre fanaticamente religioso."),
    ("El baron rampante", "Italo Calvino", "ficcion", "Einaudi", 1957, "it", "digital",
     "Cosimo Piovasco de Rondo decide subir a un arbol y no bajar nunca mas."),
    ("El caballero inexistente", "Italo Calvino", "ficcion", "Einaudi", 1959, "it", "fisico",
     "Agilulfo, un caballero sin cuerpo, sirve en el ejercito de Carlomagno."),
    ("Dora Bruder", "Patrick Modiano", "no ficcion", "Gallimard", 1997, "fr", "fisico",
     "Investigacion sobre la vida de una joven judia desaparecida durante la ocupacion nazi."),
    ("El fin del homo sovieticus", "Svetlana Alexievich", "no ficcion", "Vremya", 2013, "ru", "digital",
     "Testimonios de personas atrapadas entre el pasado sovietico y el presente catico."),
    ("Un artista del mundo flotante", "Kazuo Ishiguro", "ficcion", "Faber and Faber", 1986, "en", "fisico",
     "Un pintor japones reflexiona sobre su colaboracion con la propaganda imperialista."),
    ("El peligro de la historia unica", "Chimamanda Ngozi Adichie", "no ficcion", "Fourth Estate", 2009, "en", "digital",
     "Ensayo sobre los peligros de reducir a las personas y las culturas a una sola narrativa."),
    ("Jazz", "Toni Morrison", "ficcion", "Alfred A. Knopf", 1992, "en", "fisico",
     "Un hombre en el Harlem de los anos veinte mata a su joven amante por celos."),
    ("Ojo de pez", "Toni Morrison", "ficcion", "Alfred A. Knopf", 1970, "en", "digital",
     "Una nina negra anhela tener ojos azules en una sociedad que la hace sentir fea."),
    ("La casa de los espiritus II", "Isabel Allende", "ficcion", "Plaza & Janes", 1990, "es", "fisico",
     "Continuacion de los temas familiares y politicos de Isabel Allende."),
    ("Ripper", "Isabel Allende", "misterio", "Plaza & Janes", 2014, "es", "digital",
     "Una adolescente y sus amigos investigan una serie de crimenes en San Francisco."),
]

NOMBRES_PILA = [
    "Carlos", "Maria", "Juan", "Ana", "Luis", "Sofia", "Diego", "Valentina",
    "Pedro", "Laura", "Miguel", "Carmen", "Jose", "Elena", "Ricardo", "Gabriela",
    "Fernando", "Patricia", "Andres", "Monica", "Roberto", "Lucia", "Eduardo", "Claudia",
    "Daniel", "Alejandra", "Francisco", "Isabel", "Pablo", "Natalia", "Alberto", "Silvia",
    "Jorge", "Rosa", "Hector", "Teresa", "Mario", "Angela", "Victor", "Paula",
    "Raul", "Diana", "Rafael", "Sara", "Manuel", "Eva", "Ernesto", "Pilar",
    "Arturo", "Irene", "Nicolas", "Lorena", "Sebastian", "Cristina", "Gonzalo", "Beatriz",
    "Ignacio", "Veronica", "Leonardo", "Martha", "Rodrigo", "Alicia", "Agustin", "Sandra",
]

APELLIDOS = [
    "Garcia", "Perez", "Lopez", "Gonzalez", "Rodriguez", "Fernandez", "Martinez",
    "Sanchez", "Ramirez", "Torres", "Flores", "Herrera", "Morales", "Jimenez",
    "Ramos", "Guerrero", "Cruz", "Ortiz", "Chavez", "Mendez", "Castillo", "Romero",
    "Vargas", "Aguilar", "Vega", "Castro", "Medina", "Blanco", "Molina", "Rios",
    "Fuentes", "Moreno", "Reyes", "Delgado", "Gutierrez", "Nunez", "Pena", "Diaz",
    "Santos", "Cabrera", "Carrillo", "Soto", "Dominguez", "Ruiz", "Valdes", "Espinoza",
    "Figueroa", "Alvarez", "Leon", "Serrano", "Montoya", "Alvarado", "Contreras", "Ibarra",
]

COMENTARIOS_TEMPLATES = [
    "Absolutamente fascinante. No pude dejar de leerlo.",
    "Una obra que cambia la perspectiva del mundo.",
    "Prosa impecable y personajes inolvidables.",
    "Me dejo pensando durante semanas. Altamente recomendado.",
    "El autor logra lo imposible: hacer lo complejo accesible.",
    "Una lectura obligatoria para cualquier amante de la literatura.",
    "Magistral en cada pagina. Un clasico que no envejece.",
    "Los dialogos son brillantes y la trama engancha desde el primer capitulo.",
    "Una historia de profundo impacto emocional.",
    "La mejor novela que he leido en mucho tiempo.",
    "Entretenido e instructivo a la vez. Perfecto equilibrio.",
    "Un libro que te acompana mucho despues de terminarlo.",
    "La narrativa es tan vivida que sientes que estas ahi.",
    "Excelente desarrollo de personajes. Muy recomendable.",
    "Una joya de la literatura mundial que todos deberan leer.",
    "El ritmo de la historia es perfecto, nunca decae.",
    "Me hizo reir, llorar y reflexionar. Obra maestra.",
    "Construccion de mundo excepcional y originalidad sin par.",
    "Sutil, profundo y bellamente escrito.",
    "Una lectura que enriquece el alma y expande la mente.",
    "Historia conmovedora que deja una huella duradera.",
    "El final me dejo completamente sorprendido.",
    "Nunca pensé que un libro sobre este tema me emocionaria tanto.",
    "La autora captura la esencia humana con asombrosa precision.",
    "Un viaje literario que vale cada pagina.",
    "Merece todos los premios que ha recibido y mas.",
    "Una obra que desafia y enriquece en partes iguales.",
    "Los ultimos capitulos son de una intensidad brutal.",
    "Imprescindible para entender el siglo que vivimos.",
    "Sorprendentemente actual pese a los anos que tiene.",
    "Un clasico que supera todas las expectativas.",
    "Novela de una riqueza cultural impresionante.",
    "La mejor manera de pasar una tarde de lluvia.",
    "Recomendado sin reservas para cualquier tipo de lector.",
    "Una historia que te ata a sus paginas sin remedio.",
]


# ══════════════════════════════════════════════════════════════════════════════
# FUNCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

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
    # 1. AUTORES  — 50 documentos  (AUT-0001 al AUT-0050)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando autores...")
    autores_data = []
    for idx, (nombre, bio, nac, obras, premios) in enumerate(AUTORES_CATALOG, start=1):
        a = Autor(
            nombre=nombre,
            biografia=bio,
            nacionalidad=nac,
            obras=obras,
            premios=premios,
            autor_id=f"AUT-{idx:04d}",
        )
        errs = a.validar()
        if errs:
            print(f"  Error en autor '{a.nombre}': {errs}")
        autores_data.append(a)

    db.autores.insert_many([a.to_dict() for a in autores_data])
    print(f"  OK {len(autores_data)} autores insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 2. LIBROS  — 200 documentos  (LIB-0001 al LIB-0200)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando libros...")

    # Mapa: nombre_autor -> {autor_id, name, nacionalidad}
    AUTORES_MAP = {
        a.nombre: {"autor_id": a.autor_id, "name": a.nombre, "nacionalidad": a.nacionalidad}
        for a in autores_data
    }

    libros_data = []
    for idx, (titulo, nombre_autor, genero, editorial, anio, idioma, formato, desc) in enumerate(
        LIBROS_CATALOG, start=1
    ):
        autor_ref = AUTORES_MAP.get(nombre_autor)
        if autor_ref is None:
            # Autor no encontrado — asignar el primero como fallback
            print(f"  AVISO: autor '{nombre_autor}' no encontrado para libro '{titulo}'. Usando primer autor.")
            autor_ref = {"autor_id": autores_data[0].autor_id, "name": autores_data[0].nombre,
                         "nacionalidad": autores_data[0].nacionalidad}

        l = Libro(
            titulo=titulo,
            autor=autor_ref,
            genero=genero,
            editorial=editorial,
            year=anio,
            idioma=idioma,
            formato=formato,
            descripcion=desc,
            libro_id=f"LIB-{idx:04d}",
        )
        errs = l.validar()
        if errs:
            print(f"  Error en libro '{l.titulo}': {errs}")
        libros_data.append(l)

    # Generar libros adicionales hasta llegar a 200
    generos_list = sorted(GENEROS_VALIDOS - {"otro"})
    formatos_list = sorted(FORMATOS_VALIDOS)
    idiomas_list = list(IDIOMAS_VALIDOS.keys())
    editoriales_extra = [
        "Alfaguara", "Anagrama", "Seix Barral", "Planeta", "Tusquets",
        "Alianza Editorial", "FCE", "Gredos", "Grijalbo", "Lumen",
        "Penguin Random House", "HarperCollins", "Simon & Schuster",
        "Vintage Books", "Picador", "Faber & Faber",
    ]

    existing_count = len(libros_data)
    for extra in range(200 - existing_count):
        idx = existing_count + extra + 1
        autor_obj = random.choice(autores_data)
        autor_ref = {
            "autor_id": autor_obj.autor_id,
            "name": autor_obj.nombre,
            "nacionalidad": autor_obj.nacionalidad,
        }
        titulo = f"{random.choice(['El', 'La', 'Los', 'Las', 'Un', 'Una'])} {random.choice(['camino', 'umbral', 'horizonte', 'espejo', 'sombra', 'viento', 'tiempo', 'cielo', 'mar', 'fuego', 'tierra', 'luz', 'noche', 'alba', 'silencio', 'voz', 'memoria', 'sueno', 'destino', 'nombre'])} {random.choice(['perdido', 'eterno', 'oscuro', 'brillante', 'olvidado', 'secreto', 'invisible', 'imposible', 'ultimo', 'primero', 'infinito', 'sagrado'])}"
        genero = random.choice(generos_list)
        editorial = random.choice(editoriales_extra)
        anio = random.randint(1950, 2024)
        idioma = random.choice(idiomas_list)
        formato = random.choice(formatos_list)
        desc = f"Una obra de {autor_obj.nombre} que explora los temas de la {genero} con una perspectiva unica."

        l = Libro(
            titulo=titulo,
            autor=autor_ref,
            genero=genero,
            editorial=editorial,
            year=anio,
            idioma=idioma,
            formato=formato,
            descripcion=desc,
            libro_id=f"LIB-{idx:04d}",
        )
        errs = l.validar()
        if errs:
            print(f"  Error generando libro extra {idx}: {errs}")
        libros_data.append(l)

    db.libros.insert_many([l.to_dict() for l in libros_data])
    print(f"  OK {len(libros_data)} libros insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 3. USUARIOS  — 250 documentos  (USR-0001 al USR-0250)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando usuarios...")
    membresias = ["basica", "premium", "estudiante"]
    pesos_membresia = [0.4, 0.35, 0.25]

    dominios = ["gmail.com", "hotmail.com", "yahoo.com", "outlook.com",
                "correo.mx", "mail.co", "universidad.edu", "institito.edu.co"]

    usuarios_data = []
    correos_usados = set()
    for idx in range(1, 251):
        nombre = random.choice(NOMBRES_PILA)
        apellido1 = random.choice(APELLIDOS)
        apellido2 = random.choice(APELLIDOS)
        nombre_completo = f"{nombre} {apellido1} {apellido2}"

        base_correo = f"{nombre.lower()}.{apellido1.lower()}{idx}"
        dominio = random.choice(dominios)
        correo = f"{base_correo}@{dominio}"
        # Garantizar unicidad
        while correo in correos_usados:
            correo = f"{base_correo}_{random.randint(100, 999)}@{dominio}"
        correos_usados.add(correo)

        membresia = random.choices(membresias, weights=pesos_membresia, k=1)[0]
        num_prefs = random.randint(1, 4)
        preferencias = random.sample(generos_list, min(num_prefs, len(generos_list)))

        u = Usuario(
            nombre=nombre_completo,
            correo=correo,
            membresia=membresia,
            preferencias=preferencias,
            usuario_id=f"USR-{idx:04d}",
        )
        errs = u.validar()
        if errs:
            print(f"  Error en usuario USR-{idx:04d}: {errs}")
        usuarios_data.append(u)

    db.usuarios.insert_many([u.to_dict() for u in usuarios_data])
    print(f"  OK {len(usuarios_data)} usuarios insertados.")

    # ══════════════════════════════════════════════════════════════════
    # 4. PRESTAMOS  — 900 documentos  (PRE-0001 al PRE-0900)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando prestamos...")
    now = datetime.now(timezone.utc)

    user_map = {u.usuario_id: u for u in usuarios_data}
    libro_map = {l.libro_id: l for l in libros_data}

    estados_pesos = {"activo": 0.45, "devuelto": 0.45, "vencido": 0.10}
    estados_list = list(estados_pesos.keys())
    estados_weights = list(estados_pesos.values())

    libros_no_disponibles = set()
    prestamos_por_usuario = defaultdict(list)

    prestamos_data = []
    for idx in range(1, 901):
        usuario_obj = random.choice(usuarios_data)
        libro_obj = random.choice(libros_data)
        uid = usuario_obj.usuario_id
        lid = libro_obj.libro_id
        prestamo_id = f"PRE-{idx:04d}"
        membresia = usuario_obj.membresia
        duracion = DURACION_POR_MEMBRESIA.get(membresia, 14)

        estado = random.choices(estados_list, weights=estados_weights, k=1)[0]

        if estado == "vencido":
            inicio = now - timedelta(days=duracion + random.randint(2, 30))
            fin = inicio + timedelta(days=duracion)
            fecha_devolucion = None
        elif estado == "devuelto":
            dias_atras = random.randint(duracion + 1, duracion + 60)
            inicio = now - timedelta(days=dias_atras)
            fin = inicio + timedelta(days=duracion)
            # devolucion: puede ser antes o despues de la fecha fin
            dev_offset = random.randint(-duracion + 1, 10)
            fecha_devolucion = fin + timedelta(days=dev_offset)
        else:  # activo
            dias_atras = random.randint(0, duracion - 1)
            inicio = now - timedelta(days=dias_atras)
            fin = inicio + timedelta(days=duracion)
            fecha_devolucion = None

        usuario_ref = {
            "usuario_id": uid,
            "nombre": usuario_obj.nombre,
            "correo": usuario_obj.correo,
        }
        libro_ref = {
            "libro_id": lid,
            "titulo": libro_obj.titulo,
            "autor": libro_obj.autor,
        }

        prestamo = Prestamo(
            usuario=usuario_ref,
            libro=libro_ref,
            fecha_inicio=inicio,
            fecha_fin=fin,
            estado=estado,
            prestamo_id=prestamo_id,
        )
        if estado == "devuelto":
            prestamo.fecha_devolucion = fecha_devolucion

        errs = prestamo.validar()
        if errs:
            print(f"  Error en prestamo PRE-{idx:04d} (user {uid}, libro {lid}): {errs}")

        prestamos_data.append(prestamo)
        prestamos_por_usuario[uid].append(prestamo_id)

        if estado in ("activo", "vencido"):
            libros_no_disponibles.add(lid)

    db.prestamos.insert_many([p.to_dict() for p in prestamos_data])
    print(f"  OK {len(prestamos_data)} prestamos insertados.")

    # Actualizar historial de usuarios
    for uid, historial in prestamos_por_usuario.items():
        db.usuarios.update_one(
            {"usuario_id": uid},
            {"$set": {"historial": historial}},
        )

    # Marcar libros no disponibles
    if libros_no_disponibles:
        db.libros.update_many(
            {"libro_id": {"$in": list(libros_no_disponibles)}},
            {"$set": {"disponible": False}},
        )
        print(f"  OK {len(libros_no_disponibles)} libros marcados como no disponibles.")

    # ══════════════════════════════════════════════════════════════════
    # 5. RESENAS  — 600 documentos  (RES-0001 al RES-0600)
    # ══════════════════════════════════════════════════════════════════
    print("\nInsertando resenas...")

    resenas_data = []
    stats = defaultdict(lambda: {"suma": 0, "total": 0})
    pares_resena = set()  # evitar que un usuario repita resena del mismo libro

    idx = 1
    intentos = 0
    max_intentos = 10000

    while idx <= 600 and intentos < max_intentos:
        intentos += 1
        usuario_obj = random.choice(usuarios_data)
        libro_obj = random.choice(libros_data)
        uid = usuario_obj.usuario_id
        lid = libro_obj.libro_id
        par = (uid, lid)

        if par in pares_resena:
            continue
        pares_resena.add(par)

        resena_id = f"RES-{idx:04d}"
        calificacion = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.10, 0.15, 0.35, 0.35], k=1)[0]
        comentario = random.choice(COMENTARIOS_TEMPLATES)

        usuario_ref = {
            "usuario_id": uid,
            "nombre": usuario_obj.nombre,
            "correo": usuario_obj.correo,
        }
        libro_ref = {
            "libro_id": lid,
            "titulo": libro_obj.titulo,
        }

        # Fecha aleatoria en los ultimos 2 años
        dias_atras = random.randint(0, 730)
        fecha_resena = now - timedelta(days=dias_atras)

        resena = Resena(
            usuario=usuario_ref,
            libro=libro_ref,
            calificacion=calificacion,
            comentario=comentario,
            fecha=fecha_resena,
            resena_id=resena_id,
        )
        errs = resena.validar()
        if errs:
            print(f"  Error en resena RES-{idx:04d}: {errs}")
            continue

        resenas_data.append(resena)
        stats[lid]["suma"] += calificacion
        stats[lid]["total"] += 1
        idx += 1

    db.resenas.insert_many([r.to_dict() for r in resenas_data])
    print(f"  OK {len(resenas_data)} resenas insertadas.")

    # Calcular y actualizar estadisticas por libro
    for libro in libros_data:
        s = stats.get(libro.libro_id)
        if s and s["total"] > 0:
            estadisticas = {
                "promedioCalificacion": round(s["suma"] / s["total"], 1),
                "totalResenas": s["total"],
            }
        else:
            estadisticas = {"promedioCalificacion": 0, "totalResenas": 0}
        db.libros.update_one(
            {"libro_id": libro.libro_id},
            {"$set": {"estadisticas": estadisticas}},
        )

    print("  OK estadisticas de libros actualizadas.")

    # ══════════════════════════════════════════════════════════════════
    # CONTADORES
    # ══════════════════════════════════════════════════════════════════
    db.counters.insert_many([
        {"_id": "autores",   "seq": len(autores_data)},
        {"_id": "libros",    "seq": len(libros_data)},
        {"_id": "usuarios",  "seq": len(usuarios_data)},
        {"_id": "prestamos", "seq": len(prestamos_data)},
        {"_id": "resenas",   "seq": len(resenas_data)},
    ])
    print("  OK contadores inicializados.")

    # ══════════════════════════════════════════════════════════════════
    # RESUMEN FINAL
    # ══════════════════════════════════════════════════════════════════
    total = (
        db.autores.count_documents({}) +
        db.libros.count_documents({}) +
        db.usuarios.count_documents({}) +
        db.prestamos.count_documents({}) +
        db.resenas.count_documents({})
    )

    print("\n" + "=" * 60)
    print("  POBLACION COMPLETADA")
    print("=" * 60)
    print(f"  {db.autores.count_documents({}):>6} autores")
    print(f"  {db.libros.count_documents({}):>6} libros")
    print(f"  {db.usuarios.count_documents({}):>6} usuarios")
    print(f"  {db.prestamos.count_documents({}):>6} prestamos")
    print(f"  {db.resenas.count_documents({}):>6} resenas")
    print("  " + "-" * 30)
    print(f"  {total:>6} TOTAL de documentos")
    print("=" * 60)


if __name__ == "__main__":
    poblar()
