🎶 SongStock

Marketplace de música digital y física (MP3 y Vinilos), desarrollado en Python (Flask) con SQLite como base de datos.

🚀 Características implementadas (Sprint 1)

✅ Registro de usuarios (rol comprador/vendedor en la misma cuenta).

✅ Inicio de sesión y cierre de sesión.

✅ Recuperación básica de contraseña.

✅ Catálogo de productos con 20 items.

✅ Detalle de producto con precio, artista y descripción.

✅ Búsqueda básica de productos por nombre o artista.

✅ Filtro de productos por formato (MP3 o Vinilo).

✅ Interfaz visual con Bootstrap + CSS personalizado.

🖥️ Capturas (ejemplo)

(aquí puedes añadir imágenes con ![Texto](ruta) más adelante si deseas mostrar pantallas de login, catálogo, etc.)

⚙️ Instalación y ejecución
1. Clonar el repositorio
git clone https://github.com/Beltro0/SongStock.git
cd SongStock

2. Crear entorno virtual
python -m venv venv
venv\Scripts\activate

3. Instalar dependencias
pip install -r requirements.txt

4. Crear la base de datos
python create_db.py

5. Ejecutar la aplicación
python app.py


La aplicación estará disponible en:
👉 http://127.0.0.1:5000

🛠️ Tecnologías usadas

Python 3.12

Flask 3

SQLite

Bootstrap 5

CSS personalizado

📌 Próximos pasos (Sprint 2)

Mejorar sistema de recuperación de contraseña (token + email).

Carrito de compras.

Pasarela de pago simulada.

Panel de vendedor para gestión de productos.

Reseñas y calificaciones de productos.
