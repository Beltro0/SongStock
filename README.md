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

1. Objetivo del Sprint

Implementar todas las funcionalidades relacionadas con la logística de envíos de productos físicos (vinilos), notificaciones automáticas para comprador y proveedor, reporte de incidencias, y calificación del proveedor después de una entrega finalizada.

Este sprint completa el flujo real de negocios:
desde que un proveedor despacha un pedido hasta que el comprador confirma la entrega y evalúa la experiencia.

2. Historias de Usuario Implementadas
2.1 HU6.2 – Estado de envío

Se agregó al modelo de pedidos (orders) un campo shipping_status con los estados:

pendiente

enviado

entregado

incidencia

El proveedor puede actualizar el estado desde su panel.

2.2 HU6.3 – Confirmar recepción

El comprador, al ver un pedido con estado “enviado”, puede marcarlo como “entregado”.
Esto desbloquea la posibilidad de calificar al proveedor.

2.3 HU7.1 – Notificación al comprador

Cada cambio en el estado del pedido genera automáticamente una notificación interna para el comprador.
Estas notificaciones se muestran en su panel (perfil.html).

2.4 HU7.2 – Notificación al proveedor

Cada incidencia o confirmación de recepción envía una notificación al proveedor involucrado.
El proveedor puede consultar estas alertas en su panel de administración.

2.5 HU7.3 – Reportar incidencia

El comprador puede reportar problemas con un envío.
Se creó la tabla shipping_incidents y la vista report_incident.html.
Un pedido con incidencia cambia automáticamente a estado “incidencia”.

2.6 HU8.1 – Recomendaciones personalizadas

(En este sprint se dejan preparadas las estructuras pero de forma básica, ya que no se solicitó visualización avanzada.)

2.2 HU8.2 – Filtros avanzados

La vista del proveedor ahora filtra sus productos por correo.
Cada proveedor ve solo su inventario.

2.3 HU8.3 – Calificación del proveedor

Se implementó un nuevo sistema de calificación al proveedor después de la entrega final.
Incluye:

Nueva tabla supplier_ratings

Vista de calificación rate_supplier.html

Vista de consulta para el proveedor provider_ratings.html

Integración con pedidos finalizados

3. Cambios Realizados en la Base de Datos
3.1 Tabla supplier_ratings
CREATE TABLE IF NOT EXISTS supplier_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    provider_email TEXT NOT NULL,
    order_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(order_id) REFERENCES orders(id),
    FOREIGN KEY(user_id) REFERENCES usuarios(id)
);


Esta tabla almacena:

Calificación (1–5)

Comentario opcional

Pedido relacionado

Proveedor evaluado

4. Flujo Completo Implementado

A continuación se describe el flujo funcional que debe poder demostrar el usuario:

4.1 Flujo del Proveedor

El proveedor inicia sesión.

Accede a su panel de productos:
/provider/inventory
Solo ve productos asociados a su correo.

Recibe un nuevo pedido con vinilos suyos.

Marca el pedido como enviado:
/provider/orders

El sistema notifica al comprador.

Si el comprador reporta incidencia, el proveedor recibe notificación inmediata.

El proveedor puede consultar calificaciones recibidas:
/provider/ratings

4.2 Flujo del Comprador

El comprador realiza un pedido de un vinilo.

Accede a “Mis pedidos”:
/perfil

Ve su pedido con estado pendiente → luego enviado

Cuando el proveedor hace el envío, el comprador recibe una notificación.

Puede:

Confirmar recepción

Reportar incidencia

Tras confirmar recepción, aparece la opción para calificar al proveedor.

Completa la calificación desde:
/rate_supplier/<order_id>

5. Nuevas Rutas Añadidas
5.1 Confirmación de recepción

POST /orders/<order_id>/confirm

5.2 Reportar incidencia

GET/POST /orders/<order_id>/incident

5.3 Calificar proveedor

GET/POST /rate_supplier/<order_id>

5.4 Ver calificaciones recibidas (proveedor)

GET /provider/ratings

6. Nuevas Vistas (Templates)
6.1 rate_supplier.html

Formulario para evaluar al proveedor.

6.2 provider_ratings.html

Vista del proveedor con todas sus calificaciones.

6.3 report_incident.html

Formulario para reportar incidencia relacionada con el pedido.

6.4 Modificaciones a perfil.html

Se agregó:

Visualización del estado del envío

Acceso a incidencias

Calificaciones pendientes

Notificaciones del comprador

7. Integración con Notificaciones

Cada evento clave genera notificaciones:

Evento	Notificación comprador	Notificación proveedor
Pedido enviado	Sí	No
Pedido entregado	Sí	Sí
Incidencia reportada	Sí	Sí
Nueva calificación	No	Sí
8. Resumen Técnico

Se crearon 4 tablas nuevas:
user_notifications, shipping_incidents, supplier_ratings, ajustes en orders.

Se implementaron 6 nuevas rutas.

Se añadieron 3 vistas completas.

Se agregó lógica de negocio para validación de estados.

El proveedor ahora ve solo sus propios productos.

El comprador dispone de un flujo completo post-compra:
envío → entrega → calificación.

9. Resultado Final del Sprint

El Sprint 4 completa de forma funcional y visual todo el ciclo de vida de un pedido de vinilo dentro del marketplace:

Creación de producto por proveedor

Compra por parte del usuario

Validación y notificación del pedido

Envío por parte del proveedor

Confirmación de entrega por el comprador

Posibilidad de reportar incidencias

Calificación del proveedor

Panel del proveedor con retroalimentación directa

Este sprint sienta las bases para un marketplace totalmente operativo, con trazabilidad completa y retroalimentación a proveedores.


