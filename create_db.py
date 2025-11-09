import sqlite3, os
from datetime import datetime

DB_NAME = "songstock.db"

# ---------- CONEXIÓN ----------
def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# ---------- CREACIÓN COMPLETA ----------
def create_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print("🗑️  Base de datos anterior eliminada para recrear limpia.")

    conn = get_connection()
    cursor = conn.cursor()

    # ---------- TABLAS PRINCIPALES ----------
    cursor.execute("""
    CREATE TABLE usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT UNIQUE NOT NULL,
        contraseña TEXT NOT NULL,
        es_comprador INTEGER DEFAULT 1,
        es_vendedor INTEGER DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        artista TEXT,
        tipo TEXT CHECK(tipo IN ('mp3','vinilo')) NOT NULL,
        precio REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        proveedor_email TEXT,
        descripcion TEXT,
        imagen TEXT
    );
    """)

    # ---------- TABLAS SECUNDARIAS ----------
    cursor.executescript("""
    CREATE TABLE carts (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'draft',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE cart_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      cart_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      qty INTEGER NOT NULL DEFAULT 1,
      unit_price REAL NOT NULL
    );

    CREATE TABLE orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      status TEXT NOT NULL DEFAULT 'pending',
      total REAL NOT NULL DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE order_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      qty INTEGER NOT NULL,
      unit_price REAL NOT NULL,
      subtotal REAL NOT NULL
    );

    CREATE TABLE downloads (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      token TEXT NOT NULL UNIQUE,
      expires_at DATETIME NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE notifications (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      provider_email TEXT,
      message TEXT NOT NULL,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # ---------- USUARIO DEMO ----------
    cursor.execute("""
    INSERT INTO usuarios (nombre, correo, contraseña, es_comprador, es_vendedor)
    VALUES ('Usuario Demo', 'demo@correo.com', '1234', 1, 1);
    """)

    # ---------- 50 PRODUCTOS (MP3 + VINILOS) ----------
    demo_products = [

        # ===== MP3 (25) =====
        ("Shape of You", "Ed Sheeran", "mp3", 2.99, 0, None, "Éxito mundial de pop moderno.",
         "https://i.imgur.com/Q2S0M5t.jpg"),
        ("Blinding Lights", "The Weeknd", "mp3", 2.49, 0, None, "Synthwave contemporáneo con gran energía.",
         "https://i.imgur.com/wqkRpco.jpg"),
        ("Levitating", "Dua Lipa", "mp3", 2.29, 0, None, "Pop-disco con estilo retro y ritmo contagioso.",
         "https://i.imgur.com/Y4cQjzF.jpg"),
        ("Watermelon Sugar", "Harry Styles", "mp3", 2.19, 0, None, "Pop alegre con influencias vintage.",
         "https://i.imgur.com/2FxF0fA.jpg"),
        ("Peaches", "Justin Bieber", "mp3", 2.39, 0, None, "R&B suave con ritmos modernos.",
         "https://i.imgur.com/4QkSezC.jpg"),
        ("Save Your Tears", "The Weeknd", "mp3", 2.59, 0, None, "Canción nostálgica de amor y arrepentimiento.",
         "https://i.imgur.com/0zFkGGB.jpg"),
        ("Stay", "The Kid LAROI & Justin Bieber", "mp3", 2.49, 0, None, "Colaboración pop intensa y pegajosa.",
         "https://i.imgur.com/Ec9uBfq.jpg"),
        ("Bad Guy", "Billie Eilish", "mp3", 2.19, 0, None, "Minimalista, oscura y experimental.",
         "https://i.imgur.com/jHPOzYk.jpg"),
        ("As It Was", "Harry Styles", "mp3", 2.39, 0, None, "Reflexiva y melódica con sintetizadores ochenteros.",
         "https://i.imgur.com/0yiXcmF.jpg"),
        ("Flowers", "Miley Cyrus", "mp3", 2.29, 0, None, "Canción sobre independencia emocional.",
         "https://i.imgur.com/THzqpYZ.jpg"),
        ("Rolling in the Deep", "Adele", "mp3", 2.99, 0, None, "Voz potente con ritmo soul.",
         "https://i.imgur.com/DxtsYXa.jpg"),
        ("Uptown Funk", "Mark Ronson ft. Bruno Mars", "mp3", 2.79, 0, None, "Funk moderno irresistible.",
         "https://i.imgur.com/TS6Cxdy.jpg"),
        ("Happy", "Pharrell Williams", "mp3", 2.49, 0, None, "Himno alegre del pop contemporáneo.",
         "https://i.imgur.com/YzvxyOZ.jpg"),
        ("Counting Stars", "OneRepublic", "mp3", 2.59, 0, None, "Pop-rock con toques de folk.",
         "https://i.imgur.com/HmBQsh2.jpg"),
        ("Radioactive", "Imagine Dragons", "mp3", 2.69, 0, None, "Fusión de rock alternativo y electrónica.",
         "https://i.imgur.com/TTACoXo.jpg"),
        ("Believer", "Imagine Dragons", "mp3", 2.49, 0, None, "Motivacional y energética.",
         "https://i.imgur.com/x8FytHb.jpg"),
        ("Viva La Vida", "Coldplay", "mp3", 2.99, 0, None, "Pop orquestal con tintes épicos.",
         "https://i.imgur.com/qYk8m6p.jpg"),
        ("Paradise", "Coldplay", "mp3", 2.79, 0, None, "Tema melancólico con gran producción.",
         "https://i.imgur.com/05U2N6M.jpg"),
        ("Demons", "Imagine Dragons", "mp3", 2.39, 0, None, "Balada oscura sobre lucha interna.",
         "https://i.imgur.com/KW2UkL8.jpg"),
        ("Someone Like You", "Adele", "mp3", 2.99, 0, None, "Balada emocional con piano.",
         "https://i.imgur.com/KJzLqyz.jpg"),
        ("Let Her Go", "Passenger", "mp3", 2.39, 0, None, "Melancólica y acústica.",
         "https://i.imgur.com/jXSCcJH.jpg"),
        ("Thinking Out Loud", "Ed Sheeran", "mp3", 2.59, 0, None, "Romántica con toque soul.",
         "https://i.imgur.com/Mi7YcIu.jpg"),
        ("Shallow", "Lady Gaga & Bradley Cooper", "mp3", 2.79, 0, None, "Dueto poderoso de la película A Star is Born.",
         "https://i.imgur.com/E6EJ2W1.jpg"),
        ("Perfect", "Ed Sheeran", "mp3", 2.69, 0, None, "Romántica y cálida, ideal para bodas.",
         "https://i.imgur.com/qzKLaUx.jpg"),
        ("Halo", "Beyoncé", "mp3", 2.89, 0, None, "Balada pop con voces angelicales.",
         "https://i.imgur.com/1P3Jp9y.jpg"),

        # ===== VINILOS (25) =====
        ("Abbey Road", "The Beatles", "vinilo", 25.00, 15, "beatles@vinyls.com",
         "Vinilo icónico con 'Come Together' y 'Here Comes the Sun'.",
         "https://i.imgur.com/dEdHbGg.jpg"),
        ("Thriller", "Michael Jackson", "vinilo", 30.00, 10, "mj@vinyls.com",
         "El disco más vendido de la historia, 1982.",
         "https://i.imgur.com/6bzAEGg.jpg"),
        ("Back in Black", "AC/DC", "vinilo", 28.50, 12, "acdc@vinyls.com",
         "Álbum de hard rock clásico.",
         "https://i.imgur.com/qDJn9HK.jpg"),
        ("Rumours", "Fleetwood Mac", "vinilo", 26.00, 8, "mac@vinyls.com",
         "Uno de los discos más vendidos de todos los tiempos.",
         "https://i.imgur.com/hUlG7vv.jpg"),
        ("Dark Side of the Moon", "Pink Floyd", "vinilo", 32.00, 9, "pinkfloyd@vinyls.com",
         "Obra maestra del rock progresivo.",
         "https://i.imgur.com/2ugFhbz.jpg"),
        ("Hotel California", "Eagles", "vinilo", 27.00, 6, "eagles@vinyls.com",
         "Clásico del rock suave de los 70s.",
         "https://i.imgur.com/Ln5Vg6y.jpg"),
        ("21", "Adele", "vinilo", 26.00, 8, "adele@vinyls.com",
         "Vinilo moderno con gran potencia vocal.",
         "https://i.imgur.com/xL0H5Eh.jpg"),
        ("Born to Run", "Bruce Springsteen", "vinilo", 25.50, 10, "springsteen@vinyls.com",
         "Himno del rock estadounidense.",
         "https://i.imgur.com/HqDe8Wv.jpg"),
        ("The Wall", "Pink Floyd", "vinilo", 33.00, 5, "pinkfloyd@vinyls.com",
         "Conceptual y revolucionario, 1979.",
         "https://i.imgur.com/CxB3aqW.jpg"),
        ("Nevermind", "Nirvana", "vinilo", 29.00, 7, "nirvana@vinyls.com",
         "Grunge que cambió la historia del rock.",
         "https://i.imgur.com/MnZCvYX.jpg"),
        ("Appetite for Destruction", "Guns N' Roses", "vinilo", 30.00, 9, "gnr@vinyls.com",
         "Debut explosivo del hard rock.",
         "https://i.imgur.com/bGvCv5z.jpg"),
        ("Led Zeppelin IV", "Led Zeppelin", "vinilo", 31.00, 10, "zeppelin@vinyls.com",
         "Incluye 'Stairway to Heaven'.",
         "https://i.imgur.com/z13E7yW.jpg"),
        ("The Joshua Tree", "U2", "vinilo", 28.00, 8, "u2@vinyls.com",
         "Rock alternativo y espiritual de los 80s.",
         "https://i.imgur.com/DZk0bMv.jpg"),
        ("Random Access Memories", "Daft Punk", "vinilo", 32.00, 5, "daftpunk@vinyls.com",
         "Electrónica con influencias setenteras.",
         "https://i.imgur.com/lxRAzB2.jpg"),
        ("American Idiot", "Green Day", "vinilo", 27.00, 10, "greenday@vinyls.com",
         "Rock político y energético.",
         "https://i.imgur.com/6nTwT2y.jpg"),
        ("1989", "Taylor Swift", "vinilo", 29.00, 12, "taylorswift@vinyls.com",
         "Pop moderno con estilo ochentero.",
         "https://i.imgur.com/DpZlSGy.jpg"),
        ("Hounds of Love", "Kate Bush", "vinilo", 26.00, 9, "katebush@vinyls.com",
         "Álbum experimental de culto.",
         "https://i.imgur.com/1xSAgVf.jpg"),
        ("OK Computer", "Radiohead", "vinilo", 31.00, 7, "radiohead@vinyls.com",
         "Obra maestra del rock alternativo.",
         "https://i.imgur.com/RjN9NQe.jpg"),
        ("The College Dropout", "Kanye West", "vinilo", 28.00, 5, "kanye@vinyls.com",
         "Hip-hop introspectivo y melódico.",
         "https://i.imgur.com/LlMJUTb.jpg"),
        ("To Pimp a Butterfly", "Kendrick Lamar", "vinilo", 33.00, 4, "kendrick@vinyls.com",
         "Rap innovador con jazz y funk.",
         "https://i.imgur.com/JMiHxR6.jpg"),
        ("Back to Black", "Amy Winehouse", "vinilo", 27.00, 8, "amy@vinyls.com",
         "Soul moderno con estética retro.",
         "https://i.imgur.com/93Wvx6r.jpg"),
        ("Rumours (Reissue)", "Fleetwood Mac", "vinilo", 28.00, 6, "mac@vinyls.com",
         "Versión remasterizada del clásico de 1977.",
         "https://i.imgur.com/BZDV19Y.jpg"),
        ("Future Nostalgia", "Dua Lipa", "vinilo", 29.00, 10, "dualipa@vinyls.com",
         "Vinilo moderno con estética disco.",
         "https://i.imgur.com/gB5Cy2S.jpg"),
        ("DAMN.", "Kendrick Lamar", "vinilo", 30.00, 5, "kendrick@vinyls.com",
         "Rap contemporáneo ganador del Pulitzer.",
         "https://i.imgur.com/2Oe9OnI.jpg"),
        ("In Rainbows", "Radiohead", "vinilo", 32.00, 6, "radiohead@vinyls.com",
         "Rock alternativo con texturas electrónicas.",
         "https://i.imgur.com/FR6m8Uv.jpg")
    ]

    cursor.executemany("""
        INSERT INTO productos (nombre, artista, tipo, precio, stock, proveedor_email, descripcion, imagen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, demo_products)

    conn.commit()
    conn.close()
    print("✅ Base de datos creada con 50 productos (25 MP3 + 25 Vinilos).")
    print("   Usuario demo: demo@correo.com / contraseña: 1234")


if __name__ == "__main__":
    create_database()
