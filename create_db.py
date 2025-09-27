import sqlite3
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        correo TEXT UNIQUE,
        contraseña TEXT,
        es_comprador INTEGER DEFAULT 1,
        es_vendedor INTEGER DEFAULT 0
    );
    """)

    # productos
    c.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        tipo TEXT,
        artista TEXT,
        precio REAL,
        stock INTEGER,
        descripcion TEXT,
        imagen TEXT
    );
    """)

       # insertar datos de ejemplo solo si la tabla productos está vacía
    c.execute("SELECT COUNT(1) FROM productos")
    if c.fetchone()[0] == 0:
        productos = [
            ("Album Digital A", "mp3", "Artista 1", 10.0, 100, "Canciones en formato digital.", "mp3.png"),
            ("Vinilo Clásico B", "vinilo", "Artista 2", 25.0, 20, "Edición coleccionista en vinilo.", "vinilo.png"),
            ("Album Indie C", "mp3", "Artista 3", 8.0, 50, "Música independiente en formato digital.", "mp3.png"),
            ("Vinilo Retro D", "vinilo", "Artista 4", 30.0, 10, "Edición retro limitada.", "vinilo.png"),
            ("Single Pop E", "mp3", "Artista 5", 2.0, 500, "Single digital de pop.", "mp3.png"),
            ("Vinilo Jazz F", "vinilo", "Artista 6", 28.0, 15, "Colección de jazz en vinilo.", "vinilo.png"),
            ("Album Rock G", "mp3", "Artista 7", 12.0, 200, "Rock clásico digital.", "mp3.png"),
            ("Vinilo Metal H", "vinilo", "Artista 8", 35.0, 5, "Heavy Metal edición especial.", "vinilo.png"),
            ("EP Lo-Fi I", "mp3", "Artista 9", 5.0, 150, "Lo-Fi vibes digital.", "mp3.png"),
            ("Vinilo Soul J", "vinilo", "Artista 10", 32.0, 8, "Soul en vinilo de colección.", "vinilo.png"),
            ("Album Rap K", "mp3", "Artista 11", 11.0, 250, "Rap digital con beats modernos.", "mp3.png"),
            ("Vinilo Clásica L", "vinilo", "Artista 12", 40.0, 4, "Música clásica en vinilo.", "vinilo.png"),
            ("Single Trap M", "mp3", "Artista 13", 3.0, 600, "Single digital de trap.", "mp3.png"),
            ("Vinilo Electrónica N", "vinilo", "Artista 14", 29.0, 12, "Electrónica underground en vinilo.", "vinilo.png"),
            ("Album Baladas O", "mp3", "Artista 15", 9.0, 120, "Baladas románticas en digital.", "mp3.png"),
            ("Vinilo Blues P", "vinilo", "Artista 16", 27.0, 9, "Blues de colección en vinilo.", "vinilo.png"),
            ("Album Experimental Q", "mp3", "Artista 17", 7.0, 80, "Música experimental digital.", "mp3.png"),
            ("Vinilo Punk R", "vinilo", "Artista 18", 31.0, 6, "Punk Rock en vinilo.", "vinilo.png"),
            ("EP House S", "mp3", "Artista 19", 6.0, 90, "Música house digital.", "mp3.png"),
            ("Vinilo Reggae T", "vinilo", "Artista 20", 26.0, 7, "Reggae clásico en vinilo.", "vinilo.png"),
        ]
        c.executemany("""
            INSERT INTO productos (nombre, tipo, artista, precio, stock, descripcion, imagen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, productos)


    conn.commit()
    conn.close()
    print(f"Base de datos creada/actualizada: {DB_PATH}")

if __name__ == "__main__":
    init_db()
