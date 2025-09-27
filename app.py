from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from config import DB_PATH

app = Flask(__name__)
app.secret_key = "clave_secreta_universitaria"  # mantener simple para demo

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ----------------- RUTAS -----------------

@app.route('/')
def catalog():
    q = request.args.get('q', '').strip().lower()       # texto buscado
    tipo = request.args.get('tipo', '').strip().lower() # formato (mp3/vinilo)

    conn = get_db_connection()
    query = "SELECT * FROM productos WHERE 1=1"
    params = []

    if q:
        query += " AND (LOWER(nombre) LIKE ? OR LOWER(artista) LIKE ?)"
        params.extend([f"%{q}%", f"%{q}%"])

    if tipo and tipo in ["mp3", "vinilo"]:
        query += " AND LOWER(tipo) = ?"
        params.append(tipo)

    productos = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('catalog.html', productos=productos, q=q, tipo=tipo)


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        correo = request.form['correo'].strip().lower()
        contraseña = request.form['contraseña'].strip()
        es_comprador = 1 if request.form.get('es_comprador') else 0
        es_vendedor = 1 if request.form.get('es_vendedor') else 0

        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO usuarios (nombre, correo, contraseña, es_comprador, es_vendedor)
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, correo, contraseña, es_comprador, es_vendedor))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            # correo duplicado
            return render_template('register.html', error="El correo ya está registrado.")
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        contraseña = request.form['contraseña'].strip()

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE correo=? AND contraseña=?", (correo, contraseña)).fetchone()
        conn.close()

        if user:
            session['usuario'] = user['nombre']
            # sqlite guarda 0/1 -> convertir a booleans para la sesión
            session['es_comprador'] = bool(user['es_comprador'])
            session['es_vendedor'] = bool(user['es_vendedor'])
            return redirect(url_for('catalog'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Ruta de detalle simple (opcional)
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    p = conn.execute("SELECT * FROM productos WHERE id=?", (product_id,)).fetchone()
    conn.close()
    if not p:
        return "Producto no encontrado", 404
    return render_template('product_detail.html', producto=p)

@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        nueva_contraseña = request.form['nueva_contraseña'].strip()

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE correo=?", (correo,)).fetchone()

        if user:
            conn.execute("UPDATE usuarios SET contraseña=? WHERE correo=?", (nueva_contraseña, correo))
            conn.commit()
            conn.close()
            return render_template('reset_password.html', success="✅ Contraseña actualizada correctamente. Ahora puedes iniciar sesión.")
        else:
            conn.close()
            return render_template('reset_password.html', error="⚠️ Ese correo no está registrado.")
    return render_template('reset_password.html')


# -------------- EJECUCIÓN --------------
if __name__ == "__main__":
    print("🚀 Iniciando servidor Flask en http://127.0.0.1:5000")
    app.run(debug=True)
