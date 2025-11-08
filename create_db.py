import sqlite3
from config import DATABASE

# Conexión
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# ---------------- TABLAS ----------------
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    correo TEXT UNIQUE NOT NULL,
    contraseña TEXT NOT NULL,
    es_comprador INTEGER DEFAULT 1,
    es_vendedor INTEGER DEFAULT 1
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    artista TEXT NOT NULL,
    tipo TEXT NOT NULL, -- MP3 o Vinilo
    precio REAL NOT NULL,
    stock INTEGER DEFAULT 10,
    descripcion TEXT,
    imagen TEXT
)
''')

# ---------------- PRODUCTOS ----------------
cursor.execute("SELECT COUNT(*) FROM productos")
if cursor.fetchone()[0] == 0:
    productos = [
        ("Thriller", "Michael Jackson", "Vinilo", 59.99, 15, "Álbum icónico con Billie Jean y Beat It.", "img/thriller.jpg"),
        ("Back in Black", "AC/DC", "Vinilo", 49.99, 10, "Clásico del hard rock.", "img/back_in_black.jpg"),
        ("Abbey Road", "The Beatles", "Vinilo", 69.99, 8, "Legendario álbum de The Beatles.", "img/abbey_road.jpg"),
        ("The Dark Side of the Moon", "Pink Floyd", "Vinilo", 64.99, 12, "Uno de los discos más influyentes de la historia.", "img/dark_side.jpg"),
        ("Rumours", "Fleetwood Mac", "Vinilo", 54.99, 10, "Con Go Your Own Way y Dreams.", "img/rumours.jpg"),
        ("Nevermind", "Nirvana", "Vinilo", 59.99, 14, "Contiene Smells Like Teen Spirit.", "img/nevermind.jpg"),
        ("Random Access Memories", "Daft Punk", "MP3", 9.99, 100, "Con Get Lucky.", "img/ram.jpg"),
        ("Discovery", "Daft Punk", "MP3", 7.99, 120, "Incluye One More Time.", "img/discovery.jpg"),
        ("Homework", "Daft Punk", "MP3", 6.99, 90, "Primer álbum de Daft Punk.", "img/homework.jpg"),
        ("Born This Way", "Lady Gaga", "MP3", 8.99, 150, "Incluye Born This Way y Judas.", "img/born_this_way.jpg"),
        ("Artpop", "Lady Gaga", "MP3", 7.49, 130, "Álbum experimental de Gaga.", "img/artpop.jpg"),
        ("1989", "Taylor Swift", "Vinilo", 52.99, 20, "Álbum con Shake It Off.", "img/1989.jpg"),
        ("Red", "Taylor Swift", "Vinilo", 49.99, 18, "Incluye All Too Well.", "img/red.jpg"),
        ("Folklore", "Taylor Swift", "MP3", 9.99, 200, "Álbum íntimo de Taylor.", "img/folklore.jpg"),
        ("Evermore", "Taylor Swift", "MP3", 9.99, 200, "Continuación de Folklore.", "img/evermore.jpg"),
        ("DAMN.", "Kendrick Lamar", "Vinilo", 55.99, 15, "Incluye HUMBLE.", "img/damn.jpg"),
        ("To Pimp a Butterfly", "Kendrick Lamar", "Vinilo", 59.99, 12, "Obra maestra del rap.", "img/tpab.jpg"),
        ("good kid, m.A.A.d city", "Kendrick Lamar", "MP3", 8.99, 180, "Álbum debut de Kendrick.", "img/gkmc.jpg"),
        ("The Eminem Show", "Eminem", "Vinilo", 58.99, 10, "Con Without Me y Cleanin' Out My Closet.", "img/eminem_show.jpg"),
        ("Revival", "Eminem", "MP3", 7.99, 150, "Álbum de 2017.", "img/revival.jpg"),
        ("Scorpion", "Drake", "MP3", 8.99, 170, "Incluye God's Plan.", "img/scorpion.jpg"),
        ("Take Care", "Drake", "Vinilo", 56.99, 14, "Álbum con The Motto.", "img/take_care.jpg"),
        ("Views", "Drake", "Vinilo", 57.99, 16, "Incluye Hotline Bling.", "img/views.jpg"),
        ("Astroworld", "Travis Scott", "Vinilo", 54.99, 18, "Con Sicko Mode.", "img/astroworld.jpg"),
        ("Rodeo", "Travis Scott", "MP3", 7.99, 150, "Álbum debut de Travis.", "img/rodeo.jpg"),
        ("Graduation", "Kanye West", "Vinilo", 60.99, 12, "Incluye Stronger.", "img/graduation.jpg"),
        ("Yeezus", "Kanye West", "Vinilo", 61.99, 10, "Álbum experimental.", "img/yeezus.jpg"),
        ("The Life of Pablo", "Kanye West", "MP3", 8.99, 190, "Álbum con Ultralight Beam.", "img/tlop.jpg"),
        ("Midnight Marauders", "A Tribe Called Quest", "Vinilo", 52.99, 8, "Clásico del hip hop.", "img/midnight_marauders.jpg"),
        ("The Low End Theory", "A Tribe Called Quest", "Vinilo", 51.99, 8, "Disco influyente en el jazz rap.", "img/low_end_theory.jpg"),
        ("OK Computer", "Radiohead", "Vinilo", 63.99, 14, "Incluye Paranoid Android.", "img/ok_computer.jpg"),
        ("Kid A", "Radiohead", "Vinilo", 64.99, 10, "Álbum experimental.", "img/kid_a.jpg"),
        ("In Rainbows", "Radiohead", "MP3", 9.49, 160, "Con Nude y Weird Fishes.", "img/in_rainbows.jpg"),
        ("AM", "Arctic Monkeys", "Vinilo", 53.99, 15, "Con Do I Wanna Know?", "img/am.jpg"),
        ("Whatever People Say I Am", "Arctic Monkeys", "Vinilo", 52.99, 10, "Álbum debut de Arctic Monkeys.", "img/wpsiatwin.jpg"),
        ("Tranquility Base Hotel & Casino", "Arctic Monkeys", "MP3", 8.49, 140, "Álbum conceptual.", "img/tbhc.jpg"),
        ("The Wall", "Pink Floyd", "Vinilo", 66.99, 12, "Incluye Another Brick in the Wall.", "img/the_wall.jpg"),
        ("Wish You Were Here", "Pink Floyd", "Vinilo", 65.99, 10, "Otro clásico de Pink Floyd.", "img/wywh.jpg"),
        ("Animals", "Pink Floyd", "MP3", 9.49, 130, "Álbum conceptual.", "img/animals.jpg"),
        ("Led Zeppelin IV", "Led Zeppelin", "Vinilo", 67.99, 10, "Con Stairway to Heaven.", "img/led_zeppelin_iv.jpg"),
        ("Physical Graffiti", "Led Zeppelin", "Vinilo", 68.99, 9, "Doble álbum icónico.", "img/physical_graffiti.jpg"),
        ("Houses of the Holy", "Led Zeppelin", "MP3", 8.99, 140, "Incluye The Ocean.", "img/houses_holy.jpg"),
        ("Hybrid Theory", "Linkin Park", "Vinilo", 55.99, 15, "Álbum debut con In the End.", "img/hybrid_theory.jpg"),
        ("Meteora", "Linkin Park", "Vinilo", 56.99, 14, "Incluye Numb y Faint.", "img/meteora.jpg"),
        ("Minutes to Midnight", "Linkin Park", "MP3", 8.49, 160, "Álbum con What I've Done.", "img/minutes.jpg"),
        ("A Night at the Opera", "Queen", "Vinilo", 62.99, 10, "Incluye Bohemian Rhapsody.", "img/night_opera.jpg"),
        ("News of the World", "Queen", "Vinilo", 61.99, 10, "Incluye We Will Rock You.", "img/news_world.jpg"),
        ("Greatest Hits", "Queen", "MP3", 10.49, 200, "Recopilación de éxitos.", "img/queen_hits.jpg"),
    ]

    cursor.executemany(
        "INSERT INTO productos (nombre, artista, tipo, precio, stock, descripcion, imagen) VALUES (?,?,?,?,?,?,?)",
        productos
    )

conn.commit()
conn.close()
print("✅ Base de datos creada con 50 productos.")
