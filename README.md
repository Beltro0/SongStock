SongStock

Marketplace de música digital y física (MP3 y Vinilos), desarrollado en Python (Flask) con SQLite como base de datos.

Características implementadas (Sprint 1)

- Registro de usuarios (rol comprador/vendedor en la misma cuenta).

- Inicio de sesión y cierre de sesión.

- Recuperación básica de contraseña.

- Catálogo de productos con 20 items.

- Detalle de producto con precio, artista y descripción.

- Búsqueda básica de productos por nombre o artista.

- Filtro de productos por formato (MP3 o Vinilo).

- Interfaz visual con Bootstrap + CSS personalizado.

Instalación y ejecución

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
- http://127.0.0.1:5000

🛠️ Tecnologías usadas

Python 3.12

Flask 3

SQLite

Bootstrap 5

CSS personalizado

Próximos pasos (Sprint 2)

Mejorar sistema de recuperación de contraseña (token + email).

Carrito de compras.

Pasarela de pago simulada.

Panel de vendedor para gestión de productos.

Reseñas y calificaciones de productos.






Sprint 3 – Pasarela de Pago Simulada y Descargas Digitales
Descripción general

Durante el Sprint 3 se implementaron las funcionalidades relacionadas con la compra y descarga de productos digitales.
El objetivo fue permitir al usuario simular un pago, generar una orden y obtener accesos de descarga a los productos adquiridos (formato MP3).

Objetivos principales

Implementar una pasarela de pago simulada para completar compras.

Crear una tabla de descargas digitales que almacene tokens únicos y fechas de expiración.

Desarrollar un panel de usuario (perfil) que muestre las descargas disponibles.

Habilitar la descarga segura de archivos MP3 a partir de tokens válidos.

Mantener la coherencia visual del sistema y un flujo de compra completo.

Funcionalidades implementadas
Pasarela de pago (/pay)

Nueva vista con resumen del carrito y formulario de pago simulado.

Incluye animación de carga antes de ejecutar el flujo real de pago.

Conecta con /checkout para registrar la orden.

Generación de tokens y descargas (downloads)

Cada compra genera un token único por producto MP3.

Se define una fecha de expiración de 7 días.

Los tokens se almacenan en la nueva tabla downloads.

Panel del usuario (/perfil)

Muestra estadísticas de descargas:

Total de descargas.

Último producto adquirido.

Próxima fecha de expiración.

Incluye tabla con nombre, artista, token, fecha de expiración y botón de descarga.

Descarga segura (/download/<token>)

Verifica sesión activa, token y expiración.

Devuelve el archivo correspondiente (en este caso un MP3 genérico de prueba).

Incluye mensajes de confirmación y advertencia mediante flash.
Flujo general del Sprint 3

El usuario agrega productos al carrito.

Desde el carrito selecciona “Proceder al pago”.

Se muestra la pasarela visual (/pay) y se simula el pago.

El backend genera la orden y las descargas digitales (downloads).

El usuario es redirigido al panel /perfil, donde puede descargar sus archivos.

Resultados

Flujo completo de compra–pago–descarga operativo.

Tokens únicos y fechas de expiración funcionales.

Interfaz coherente con el resto de la aplicación.

Prototipo listo para presentación académica.
