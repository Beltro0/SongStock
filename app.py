from flask import Flask, render_template, request, redirect, session, url_for, jsonify, flash, send_file
import sqlite3, uuid, os
from datetime import datetime, timedelta
from config import DATABASE, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# ---------------- DB ----------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ========= AUTO-MIGRACIONES SPRINT 2 + SPRINT 3 =========
SCHEMA_SQL_SPRINT2_TABLES = """
-- Carritos
CREATE TABLE IF NOT EXISTS carts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
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
  status TEXT NOT NULL DEFAULT 'pending',
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

# 🆕 Descargas digitales Sprint 3
SCHEMA_SQL_DOWNLOADS = """
CREATE TABLE IF NOT EXISTS downloads (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  token TEXT NOT NULL UNIQUE,
  expires_at DATETIME NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES usuarios(id),
  FOREIGN KEY (product_id) REFERENCES productos(id)
);
"""

# Notificaciones Sprint 2
SCHEMA_SQL_NOTIFICATIONS = """
CREATE TABLE IF NOT EXISTS notifications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  order_id INTEGER NOT NULL,
  provider_email TEXT,
  message TEXT NOT NULL,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
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
    conn.executescript(SCHEMA_SQL_SPRINT2_TABLES)
    conn.commit()
    try:
        if not column_exists(conn, "productos", "stock"):
            conn.execute("ALTER TABLE productos ADD COLUMN stock INTEGER DEFAULT 0")
        if not column_exists(conn, "productos", "proveedor_email"):
            conn.execute("ALTER TABLE productos ADD COLUMN proveedor_email TEXT")
    except Exception:
        pass
    conn.commit()
    conn.close()

def apply_notifications_schema():
    conn = get_db_connection()
    conn.executescript(SCHEMA_SQL_NOTIFICATIONS)
    conn.commit()
    conn.close()

def apply_downloads_schema():
    conn = get_db_connection()
    conn.executescript(SCHEMA_SQL_DOWNLOADS)
    conn.commit()
    conn.close()

def ensure_cart(conn, user_id):
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if row: return row["id"]
    cur = conn.execute("INSERT INTO carts(user_id) VALUES (?)", (user_id,))
    conn.commit()
    return cur.lastrowid

def is_vinyl(p): return (p["tipo"] or "").strip().lower() == "vinilo"

def assert_stock_ok(conn, product_id, requested_qty):
    p = conn.execute("SELECT tipo, stock FROM productos WHERE id=?", (product_id,)).fetchone()
    if not p: return False, "Producto no encontrado"
    if is_vinyl(p):
        if requested_qty > int(p["stock"] or 0):
            return False, "Stock insuficiente"
    return True, None

def get_product_price(conn, product_id):
    p = conn.execute("SELECT precio FROM productos WHERE id=?", (product_id,)).fetchone()
    if not p: raise ValueError("Producto no encontrado")
    return float(p["precio"])

def notify_providers(conn, order_id, items, total):
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

# --- Bootstrap migraciones ---
try:
    apply_schema_sprint2()
    apply_notifications_schema()
    apply_downloads_schema()
    print("✅ Migraciones Sprint 2 + 3 aplicadas/validadas.")
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
        conn.commit(); conn.close()
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
            session['user_id'] = user['id']
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
        nueva = request.form['nueva_contraseña'].strip()
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM usuarios WHERE correo=?", (correo,)).fetchone()
        if user:
            conn.execute("UPDATE usuarios SET contraseña=? WHERE correo=?", (nueva, correo))
            conn.commit(); conn.close()
            return render_template('reset_password.html', success="✅ Contraseña actualizada.")
        conn.close()
        return render_template('reset_password.html', error="⚠️ Correo no registrado.")
    return render_template('reset_password.html')

# ----------- CARRITO -----------
@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    cart_id = ensure_cart(conn, user_id)
    unit_price = get_product_price(conn, product_id)
    row = conn.execute("""SELECT id, qty FROM cart_items WHERE cart_id=? AND product_id=?""",
                       (cart_id, product_id)).fetchone()
    new_qty = (row["qty"] + 1) if row else 1
    ok, err = assert_stock_ok(conn, product_id, new_qty)
    if not ok:
        conn.close()
        return redirect(url_for('cart', error=err))
    if row:
        conn.execute("UPDATE cart_items SET qty=? WHERE id=?", (new_qty, row["id"]))
    else:
        conn.execute("""INSERT INTO cart_items(cart_id, product_id, qty, unit_price)
                        VALUES (?,?,?,?)""", (cart_id, product_id, 1, unit_price))
    conn.commit(); conn.close()
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    productos = []; total = 0.0
    if row:
        cart_id = row["id"]
        items = conn.execute("""SELECT ci.product_id, ci.qty, ci.unit_price, p.nombre, p.tipo
                                FROM cart_items ci JOIN productos p ON p.id=ci.product_id
                                WHERE ci.cart_id=?""", (cart_id,)).fetchall()
        for it in items:
            subtotal = float(it["unit_price"]) * int(it["qty"])
            productos.append({"id": it["product_id"],"nombre": it["nombre"],
                              "precio": it["unit_price"],"cantidad": it["qty"],
                              "subtotal": subtotal,"tipo": it["tipo"]})
            total += subtotal
    conn.close()
    return render_template('cart.html', productos=productos, total=total, error=request.args.get("error"))

# ----------- PANTALLA PASARELA DE PAGO (visual Sprint 3) -----------
@app.route('/pay', methods=['GET'])
def pay():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if not row:
        conn.close()
        return redirect(url_for('cart'))
    cart_id = row["id"]
    items = conn.execute("""
        SELECT ci.product_id, ci.qty as cantidad, ci.unit_price as precio, p.nombre, p.tipo
        FROM cart_items ci
        JOIN productos p ON p.id = ci.product_id
        WHERE ci.cart_id=?
    """, (cart_id,)).fetchall()
    total = sum(float(it["precio"]) * int(it["cantidad"]) for it in items)
    conn.close()
    return render_template('checkout.html', productos=items, total=total)


@app.route('/remove_from_cart/<int:product_id>')
def remove_from_cart(product_id):
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM cart_items WHERE cart_id=? AND product_id=?", (row["id"], product_id))
        conn.commit()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/clear_cart')
def clear_cart():
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    row = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if row:
        conn.execute("DELETE FROM cart_items WHERE cart_id=?", (row["id"],))
        conn.commit()
    conn.close()
    return redirect(url_for('cart'))

# ----------- CHECKOUT (Sprint 3) -----------
@app.route('/checkout', methods=['POST'])
def checkout():
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    cart = conn.execute("SELECT id FROM carts WHERE user_id=? AND status='draft'", (user_id,)).fetchone()
    if not cart:
        conn.close(); return redirect(url_for('cart'))
    cart_id = cart["id"]
    items = conn.execute("""SELECT ci.product_id, ci.qty, ci.unit_price, 
                                   p.tipo, p.stock, p.proveedor_email, p.nombre
                            FROM cart_items ci
                            JOIN productos p ON p.id=ci.product_id
                            WHERE ci.cart_id=?""", (cart_id,)).fetchall()
    if not items:
        conn.close(); return redirect(url_for('cart'))
    for it in items:
        if (it["tipo"] or "").lower()=="vinilo" and int(it["qty"])>int(it["stock"] or 0):
            conn.close(); return redirect(url_for('cart', error="Stock insuficiente"))
    total=sum(float(it["unit_price"])*int(it["qty"]) for it in items)
    cur=conn.execute("INSERT INTO orders(user_id,total,status) VALUES(?,?,'paid')",(user_id,total))
    order_id=cur.lastrowid
    for it in items:
        subtotal=float(it["unit_price"])*int(it["qty"])
        conn.execute("""INSERT INTO order_items(order_id,product_id,qty,unit_price,subtotal)
                        VALUES (?,?,?,?,?)""",(order_id,it["product_id"],it["qty"],it["unit_price"],subtotal))
        if (it["tipo"] or "").lower()=="vinilo":
            conn.execute("UPDATE productos SET stock=stock-? WHERE id=?",(it["qty"],it["product_id"]))
        elif (it["tipo"] or "").lower()=="mp3":
            token=str(uuid.uuid4())
            expira=datetime.now()+timedelta(days=7)
            conn.execute("""INSERT INTO downloads(user_id,product_id,token,expires_at)
                            VALUES (?,?,?,?)""",(user_id,it["product_id"],token,expira))
    conn.execute("UPDATE carts SET status='checked_out' WHERE id=?", (cart_id,))
    conn.execute("DELETE FROM cart_items WHERE cart_id=?", (cart_id,))
    conn.commit(); notify_providers(conn, order_id, items, total); conn.close()
    flash("✅ Pago procesado. Descargas disponibles en tu perfil.", "success")
    return redirect(url_for('perfil'))

# ----------- PERFIL Y DESCARGAS -----------
@app.route('/perfil')
def perfil():
    if 'usuario' not in session: return redirect(url_for('login'))
    user_id=session.get('user_id')
    conn=get_db_connection()
    rows=conn.execute("""SELECT d.id,p.nombre,p.artista,p.id AS producto_id,d.token,d.expires_at
                         FROM downloads d JOIN productos p ON p.id=d.product_id
                         WHERE d.user_id=? ORDER BY d.created_at DESC""",(user_id,)).fetchall()
    conn.close()
    return render_template('perfil.html',descargas=rows)

@app.route('/download/<token>')
def download_file(token):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    user_id = session.get('user_id')

    conn = get_db_connection()
    d = conn.execute("SELECT * FROM downloads WHERE token=?", (token,)).fetchone()
    conn.close()

    if not d:
        flash("❌ Token inválido.", "danger")
        return redirect(url_for('perfil'))

    # ✅ Manejo de fechas con microsegundos
    try:
        expira = datetime.strptime(d["expires_at"], "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        expira = datetime.strptime(d["expires_at"], "%Y-%m-%d %H:%M:%S")

    if expira < datetime.now():
        flash("⚠️ Enlace expirado.", "warning")
        return redirect(url_for('perfil'))

    if d["user_id"] != user_id:
        flash("🚫 No autorizado.", "danger")
        return redirect(url_for('perfil'))

    # ✅ Usar un archivo MP3 genérico para la demo
    path = os.path.join("static", "mp3", "demo.mp3")
    if not os.path.exists(path):
        flash("⚠️ El archivo genérico demo.mp3 no se encontró en /static/mp3/", "warning")
        return redirect(url_for('perfil'))

    # Mostrar mensaje visual de éxito
    flash("✅ Descarga iniciada correctamente.", "success")
    return send_file(path, as_attachment=True)



# ----------- INVENTARIO PROVEEDOR -----------
@app.route('/provider/inventory/<int:product_id>', methods=['PATCH'])
def provider_inventory_update(product_id):
    payload=request.get_json(force=True)
    stock=payload.get("stock"); price=payload.get("price"); proveedor_email=payload.get("proveedor_email")
    conn=get_db_connection()
    if stock is not None: conn.execute("UPDATE productos SET stock=? WHERE id=?",(int(stock),product_id))
    if price is not None: conn.execute("UPDATE productos SET precio=? WHERE id=?",(float(price),product_id))
    if proveedor_email is not None: conn.execute("UPDATE productos SET proveedor_email=? WHERE id=?",(proveedor_email,product_id))
    conn.commit(); conn.close()
    return jsonify({"ok":True})

@app.route('/provider/inventory', methods=['GET','POST'])
def provider_inventory():
    conn=get_db_connection()
    if request.method=='POST':
        pid=int(request.form['product_id'])
        stock=request.form.get('stock'); price=request.form.get('price'); email=request.form.get('proveedor_email','').strip()
        if stock: conn.execute("UPDATE productos SET stock=? WHERE id=?",(int(stock),pid))
        if price: conn.execute("UPDATE productos SET precio=? WHERE id=?",(float(price),pid))
        conn.execute("UPDATE productos SET proveedor_email=? WHERE id=?",(email,pid))
        conn.commit()
    productos=conn.execute("""SELECT id,nombre,tipo,precio,stock,proveedor_email
                               FROM productos WHERE LOWER(tipo)='vinilo' ORDER BY nombre""").fetchall()
    conn.close()
    return render_template('provider_inventory.html',productos=productos)

# ----------- NOTIFICACIONES -----------
@app.route('/admin/notifications')
def admin_notifications():
    conn=get_db_connection()
    rows=conn.execute("SELECT id,order_id,provider_email,message,created_at FROM notifications ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template('admin_notifications.html',notifications=rows)

# ---------------- MAIN ----------------
if __name__=="__main__":
    app.run(debug=True)
