# Historias de Usuario

## 1. Sistema de Cupones y Descuentos

### Historia de Usuario
Como cliente registrado, quiero aplicar un cupón de descuento durante mi compra, para obtener un mejor precio en mi pedido.

### Criterios de Aceptación
- El sistema debe permitir ingresar un código de cupón en el checkout.
- El backend debe validar:
	- Si el cupón existe.
	- Si está vigente.
	- Si aplica al usuario.
	- Si no ha sido usado previamente (si es de un solo uso).
- Si el cupón es válido:
	- Debe recalcular el total del carrito.
	- Debe mostrarse el descuento aplicado.
- Si es inválido, debe mostrarse un mensaje explicativo.
- El admin puede crear, editar y eliminar cupones desde el panel.

## 2. Lista de Favoritos / Wishlist

### Historia de Usuario
Como cliente, quiero poder marcar productos como favoritos, para encontrarlos rápidamente en futuras compras.

### Criterios de Aceptación
- Cada producto debe mostrar un ícono de "favorito" (estrella / corazón).
- Al hacer clic, el producto debe agregarse o eliminarse de la lista.
- La lista de favoritos debe ser persistente por usuario.
- Debe existir una vista dedicada: "Mis Favoritos".
- Si no hay favoritos, debe mostrarse un mensaje indicando que está vacío.

## 3. Programación de Pedidos (Pedido Programado)

### Historia de Usuario
Como cliente, quiero poder programar mi pedido para una fecha y hora futura, para recibirlo en el momento que más me convenga.

### Criterios de Aceptación
- El cliente puede seleccionar una fecha y hora disponible al momento de finalizar la compra.
- El sistema debe validar:
	- Que la fecha/hora esté en el futuro.
	- Que el restaurante esté disponible en ese horario.
	- Que no supere un límite máximo (ej.: 48 horas).
- El pedido debe guardarse con estado “Programado”.
- El sistema debe enviar el pedido al flujo normal cuando llegue la hora programada.
- El admin puede ver qué pedidos están programados.
- El cliente debe poder ver la información del pedido programado en su historial.

## 4. Sistema de Calificaciones y Reseñas

### Historia de Usuario
Como cliente que ya recibió su pedido, quiero calificar los productos que compré, para compartir mi experiencia y mejorar el servicio.

### Criterios de Aceptación
- Solo usuarios autenticados pueden dejar reseñas.
- Solo pueden calificar productos de pedidos entregados.
- Las reseñas deben incluir:
	- Puntaje (1 a 5 estrellas).
	- Comentario opcional.
- El producto debe mostrar su calificación promedio.
- El admin puede ver todas las reseñas desde su panel.
- Si un usuario intenta calificar un producto que no compró, el sistema debe impedirlo.

---

### Notas finales
- Estas historias están alineadas con la arquitectura existente del sistema (backend en FastAPI, frontend en React y capa de mensajería con RabbitMQ).
- Permiten además desarrollar pruebas unitarias e integración, mockups visuales simples y seguir buenas prácticas (SOLID, separación de responsabilidades, etc.).