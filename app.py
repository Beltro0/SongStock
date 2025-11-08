from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import sqlite3
from config import DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------------- DB ----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ========= AUTO-MIGRACIÓN SPRINT 2 (compatible Flask 3.x) =========
SCHEMA_SQL_SPRINT2_TABLES = """
-- Carritos
CREATE TABLE IF NOT EXISTS carts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft', -- 'draft'|'checked_out'
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cart_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cart_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL DEFAULT 1,
  unit_price REAL NOT NULL,
  FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES productos(id),
  UNIQUE(cart_id, product_id)
);

-- Órdenes
CREATE TABLE IF NOT EXISTS orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending', -- 'pending'|'paid'|'rejected'|'accepted'
  total REAL NOT NULL DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  subtotal REAL NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES productos(id)
);
"""

def column_exists(conn, table, column):
    rows = conn.execute(f"PRAGMA table_info({table});").fetchall()
    for r in rows:
        if r["name"].lower() == column.lower():
            return True
    return False

def apply_schema_sprint2():
    conn = get_db_connection()
    # Crear tablas nuevas si no existen
    conn.executescript(SCHEMA_SQL_SPRINT2_TABLES)
    conn.commit()

    # Asegurar columnas en 'productos': stock y proveedor_email
    try:
        if not column_exists(conn, "productos", "stock"):
            conn.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
    except Exception:
        pass
    try:
        if not column_exists(conn, "productos", "proveedor_email"):
            conn.execute("ALTER TABLE productos ADD COLUMN proveedor_email TEXT")
    except Exception:
        pass

    conn.commit()
    conn.close()

# ---------- NOTIFICATIONS: tabla y helpers ----------
SCHEMA_SQL_NOTIFICATIONS = """
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  provider_email TEXT,
  message TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""

def apply_notifications_schema():
    conn = get_db_connection()
    conn.executescript(SCHEMA_SQL_NOTIFICATIONS)
    conn.commit()
    conn.close()

def ensure_cart(conn, user_id):
    row = conn.execute(
        "SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)
    ).fetchone()
    if row:
        return row["id"]
    cur = conn.execute("INSERT INTO carts(user_id) VALUES (?)", (user_id,))
    conn.commit()
    return cur.lastrowid

def is_vinyl(producto_row):
    t = (producto_row["tipo"] or "").strip().lower()
    return t == "vinilo"

def assert_stock_ok(conn, product_id, requested_qty):
    """Valida stock SOLO para vinilos."""
    p = conn.execute("SELECT tipo, stock FROM productos WHERE id=?", (product_id,)).fetchone()
    if not p:
        return False, "Producto no encontrado"
    if is_vinyl(p):
        stock = int(p["stock"] or 0)
        if requested_qty > stock:
            return False, "Stock insuficiente"
    return True, None

def get_product_price(conn, product_id):
    p = conn.execute("SELECT precio FROM productos WHERE id=?", (product_id,)).fetchone()
    if not p:
        raise ValueError("Producto no encontrado")
    return float(p["precio"])

def notify_providers(conn, order_id, items, total):
    """
    Agrupa ítems de vinilo por email de proveedor, imprime en consola y
    persiste una 'traza' de notificación para demostrar HU4.3.
    """
    proveedores = {}
    for it in items:
        if (it["tipo"] or "").lower() == "vinilo":
            email = (it["proveedor_email"] or "").strip()
            if email:
                proveedores.setdefault(email, []).append(f"{it['nombre']} x{it['qty']}")

    if proveedores:
        print(f"[NOTIFY] Orden #{order_id} total ${total:.2f}")
        for email, lines in proveedores.items():
            msg = "; ".join(lines)
            conn.execute(
                "INSERT INTO notifications(order_id, provider_email, message) VALUES (?,?,?)",
                (order_id, email, msg),
            )
            print(f"  -> Enviar correo a {email}: {msg}")
        conn.commit()

# --- Bootstrap de migración al importar (Flask 3.x friendly) ---
try:
    apply_schema_sprint2()
    apply_notifications_schema()
    print("✅ Migración Sprint 2 + Notifications aplicadas/validadas.")
except Exception as e:
    print(f"⚠️ Error aplicando migraciones: {e}")

# ---------------- RUTAS ----------------

@app.route('/')
def catalog():
    q = request.args.get('q', '').strip().lower()
    tipo = request.args.get('tipo', '').strip().lower()

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

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    conn = get_db_connection()
    producto = conn.execute("SELECT * FROM productos WHERE id=?", (product_id,)).fetchone()
    conn.close()
    return render_template('product_detail.html', producto=producto)

# ----------- AUTH -----------

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo'].strip().lower()
        contraseña = request.form['contraseña']

        conn = get_db_connection()
        conn.execute("""INSERT INTO usuarios (nombre,correo,contraseña,es_comprador,es_vendedor)
                        VALUES (?,?,?,?,?)""",
                     (nombre, correo, contraseña, 1, 1))
        conn.commit()
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo'].strip().lower()
        contraseña = request.form['contraseña']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE correo=? AND contraseña=?", 
                            (correo, contraseña)).fetchone()
        conn.close()

        if user:
            session['usuario'] = user['nombre']
            session['user_id'] = user['id']           # <-- necesario para carrito persistente
            session['es_comprador'] = user['es_comprador']
            session['es_vendedor'] = user['es_vendedor']
            return redirect(url_for('catalog'))
        else:
            return render_template('login.html', error="⚠️ Credenciales incorrectas")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

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
            return render_template('reset_password.html', success="✅ Contraseña actualizada correctamente.")
        else:
            conn.close()
            return render_template('reset_password.html', error="⚠️ Ese correo no está registrado.")
    return render_template('reset_password.html')

# ----------- CARRITO (Sprint 2: persistente en BD + validación stock vinilo) -----------

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    # Conservamos el endpoint que ya usas, pero ahora persiste en BD y valida stock
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    # Asegurar carrito 'draft' del usuario
    cart_id = ensure_cart(conn, user_id)

    # Precio actual del producto
    unit_price = get_product_price(conn, product_id)

    # Leer qty actual en carrito y calcular qty nueva
    row = conn.execute("""SELECT id, qty FROM cart_items
                          WHERE cart_id=? AND product_id=?""",
                       (cart_id, product_id)).fetchone()
    new_qty = (row["qty"] + 1) if row else 1

    # Validar stock si es vinilo
    ok, err = assert_stock_ok(conn, product_id, new_qty)
    if not ok:
        conn.close()
        return redirect(url_for('cart', error=err))

    if row:
        conn.execute("UPDATE cart_items SET qty=? WHERE id=?", (new_qty, row["id"]))
    else:
        conn.execute("""INSERT INTO cart_items(cart_id, product_id, qty, unit_price)
                        VALUES (?,?,?,?)""", (cart_id, product_id, 1, unit_price))
    conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()

    productos = []
    total = 0.0
    if row:
        cart_id = row["id"]
        items = conn.execute("""SELECT ci.id, ci.product_id, ci.qty, ci.unit_price,
                                       p.nombre, p.tipo
                                FROM cart_items ci
                                JOIN productos p ON p.id = ci.product_id
                                WHERE ci.cart_id=?""", (cart_id,)).fetchall()
        for it in items:
            subtotal = float(it["unit_price"]) * int(it["qty"])
            productos.append({
                "id": it["product_id"],
                "nombre": it["nombre"],
                "precio": it["unit_price"],
                "cantidad": it["qty"],
                "subtotal": subtotal,
                "tipo": it["tipo"]
            })
            total += subtotal

    conn.close()
    return render_template('cart.html', productos=productos, total=total, error=request.args.get("error"))

@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if row:
        cart_id = row["id"]
        conn.execute("DELETE FROM cart_items WHERE cart_id=? AND product_id=?", (cart_id, product_id))
        conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM cart_items WHERE cart_id=?", (row["id"],))
        conn.commit()
    conn.close()
    return redirect(url_for('cart'))

# ----------- ÓRDENES (Sprint 2) -----------

@app.route('/checkout', methods=['POST'])
def checkout():
    # Genera la orden desde el carrito, valida stock (vinilo) y descuenta
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cart = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if not cart:
        conn.close()
        return redirect(url_for('cart'))

    cart_id = cart["id"]
    items = conn.execute("""SELECT ci.product_id, ci.qty, ci.unit_price, 
                                   p.tipo, p.stock, p.proveedor_email, p.nombre
                            FROM cart_items ci
                            JOIN productos p ON p.id = ci.product_id
                            WHERE ci.cart_id=?""", (cart_id,)).fetchall()

    if not items:
        conn.close()
        return redirect(url_for('cart'))

    # Revalidar stock vinilo
    for it in items:
        if (it["tipo"] or "").lower() == "vinilo":
            if int(it["qty"]) > int(it["stock"] or 0):
                conn.close()
                return redirect(url_for('cart', error="Stock insuficiente en uno o más vinilos"))

    # Crear orden
    total = sum(float(it["unit_price"]) * int(it["qty"]) for it in items)
    cur = conn.execute("INSERT INTO orders(user_id,total) VALUES(?,?)", (user_id, total))
    order_id = cur.lastrowid

    # Crear order_items y descontar stock de vinilo
    for it in items:
        subtotal = float(it["unit_price"]) * int(it["qty"])
        conn.execute("""INSERT INTO order_items(order_id,product_id,qty,unit_price,subtotal)
                        VALUES (?,?,?,?,?)""",
                     (order_id, it["product_id"], it["qty"], it["unit_price"], subtotal))
        if (it["tipo"] or "").lower() == "vinilo":
            conn.execute("UPDATE productos SET stock = stock - ? WHERE id=?",
                         (it["qty"], it["product_id"]))

    # Cerrar carrito
    conn.execute("UPDATE carts SET status='checked_out' WHERE id=?", (cart_id,))
    conn.execute("DELETE FROM cart_items WHERE cart_id=?", (cart_id,))
    conn.commit()

    # Notificación (persistente)
    notify_providers(conn, order_id, items, total)

    conn.close()
    # Volver al carrito con confirmación visual
    return redirect(url_for('cart', ok=1))

# ----------- INVENTARIO PROVEEDOR (Sprint 2) -----------

@app.route('/provider/inventory/<int:product_id>', methods=['PATCH'])
def provider_inventory_update(product_id):
    # API: actualizar inventario por producto (para pruebas rápidas con cURL/PowerShell)
    payload = request.get_json(force=True)
    stock = payload.get("stock")
    price = payload.get("price")
    proveedor_email = payload.get("proveedor_email")

    conn = get_db_connection()
    if stock is not None:
        conn.execute("UPDATE productos SET stock=? WHERE id=?", (int(stock), product_id))
    if price is not None:
        conn.execute("UPDATE productos SET precio=? WHERE id=?", (float(price), product_id))
    if proveedor_email is not None:
        conn.execute("UPDATE productos SET proveedor_email=? WHERE id=?", (proveedor_email, product_id))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})

@app.route('/provider/inventory', methods=['GET','POST'])
def provider_inventory():
    # UI: gestión de inventario de vinilos
    conn = get_db_connection()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        stock = request.form.get('stock')
        price = request.form.get('price')
        email = request.form.get('proveedor_email', '').strip()
        if stock is not None and stock != '':
            conn.execute("UPDATE productos SET stock=? WHERE id=?", (int(stock), product_id))
        if price is not None and price != '':
            conn.execute("UPDATE productos SET precio=? WHERE id=?", (float(price), product_id))
        conn.execute("UPDATE productos SET proveedor_email=? WHERE id=?", (email, product_id))
        conn.commit()

    productos = conn.execute("""
        SELECT id, nombre, tipo, precio, stock, proveedor_email
        FROM productos
        WHERE LOWER(tipo)='vinilo'
        ORDER BY nombre
    """).fetchall()
    conn.close()
    return render_template('provider_inventory.html', productos=productos)

# ----------- VISTA: Notificaciones (para demostrar HU4.3) -----------

@app.route('/admin/notifications')
def admin_notifications():
    # UI: listado de notificaciones generadas al crear órdenes
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT id, order_id, provider_email, message, created_at
        FROM notifications
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return render_template('admin_notifications.html', notifications=rows)

# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)
