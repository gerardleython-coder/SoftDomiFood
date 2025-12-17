Radiografía actual del proyecto
1. Descripción del Proyecto:
•	Nombre del Proyecto: SoftDomiFood
•	Objetivo del Proyecto: Restaurante en línea para que los usuarios hagan pedidos, puedan recogerlos o pedir despacho/domicilio.
2. Flujos Críticos del Negocio:
•	Principales Flujos de Trabajo:
o	Levantar el proyecto con Docker (ejecutar comando para correr los servicios).
o	Cargar productos con un proceso tipo “semilla” (ejecutar comando con docker para cargar productos).
o	Registro e inicio de sesión de clientes.
o	Inicio de sesión de administrador (correo y contraseña definidos en el README, mencionados en la sesión).
o	Gestión de productos (crear/editar/eliminar) desde panel admin.
o	Navegación de cliente: ver menú, agregar al carrito, marcar favoritos y ver favoritos.
o	Creación de pedido: seleccionar dirección, elegir si es para “más tarde” (programar) o directo; seleccionar medio de pago (mencionan efectivo); confirmar pedido.
o	Actualización/seguimiento de estado del pedido (pendiente, en preparación, listo, entregado, programado), con actualización automática cada 10 segundos (polling a “Get Orders”).
o	Cupones: crear cupón en admin y aplicarlo en el carrito del cliente.
o	Reseñas: calificar producto una vez entregado; visualizar reseñas en menú; listar/eliminar reseñas en admin.
•	Módulos o Funcionalidades Críticas:
o	Frontend Cliente (menú, carrito, pedidos, favoritos, cupones, reseñas).
o	Frontend Administrativo (productos, pedidos/estados, cupones, reseñas, clientes - historial).
o	Backend / API (rutas/servicios en Python).
o	Base de datos (mencionan exportación SQL + scripts para recuperar/inicializar) Postgre.
o	Carga de datos / set data (cargar productos como semilla).
o	Automatización de pruebas “CUA” (mencionada, no validada).
3. Reglas de Negocio y Restricciones:
•	Reglas de Negocio Relevantes:
o	El proyecto tiene 2 frontends: cliente y admin.
o	El estado de pedidos no cambia en tiempo real; se actualiza por polling cada 10 segundos consultando un servicio tipo “Get Orders”.
o	Programar pedido para más tarde: no puede superar 48 horas.
o	Restricción de horario del restaurante: abre a las 10:00 a.m. y cierra “como a medianoche” (mencionado de forma aproximada).
o	Botones de gestión de estado (listo/entregado) no aparecen para pedidos en estado programado hasta que llegue fecha/hora; solo aparece opción de cancelar.
o	Cupones: descuento puede ser por porcentaje o monto fijo.
o	Validaciones: se menciona que el admin no tiene validación de fechas del cupón; el lado cliente sí tiene alguna validación (se menciona, no se detalla).

4. Perfiles de Usuario y Roles:
•	Perfiles o Roles de Usuario en el Sistema:
o	Administrador (panel administrativo).
o	Cliente/Usuario final (frontend cliente: registro, pedidos, etc.).
•	Permisos y Limitaciones de Cada Perfil:
o	Administrador: inicia sesión con credenciales definidas en README; gestiona productos; visualiza y cambia estado de pedidos; crea/actualiza cupones; lista y elimina reseñas; ve clientes (historial, sin CRUD).
o	Cliente: se registra/inicia sesión; navega productos; agrega al carrito; marca favoritos; crea pedidos (directo o programado); aplica cupones; califica productos cuando el pedido está entregado; ve sus pedidos y reseñas en menú.
5. Condiciones del Entorno Técnico:
•	Plataformas Soportadas:
o	Web (dos frontends: cliente y admin). No se menciona móvil.
•	Tecnologías o Integraciones Clave:
o	Docker para ejecución del proyecto.
o	Backend en Python (API con rutas y servicios).
o	Base de datos con exportación SQL + scripts de inicialización/recuperación.
o	Servicio consultado cada 10s para pedidos (“Get Orders” o similar).
o	Pruebas “CUA” (mencionadas, sin detalle técnico adicional).
6. Casos Especiales o Excepciones (Opcional):
•	Escenarios Alternos o Excepciones que Deben Considerarse:
o	Actualización cada 10 segundos (comportamiento no en tiempo real) afecta la percepción del cambio de estado. Colocar modal cargando
o	Ventana/alerta al agregar producto (“ventanita”) no se cierra sola; persiste y se quita entrando al carrito (comportamiento identificado, no corregido).
o	Posible problema de zona horaria: reportan desfase de ~3 horas al programar pedidos.
o	CSS: en reseñas se desborda el CSS (identificado).
o	En registro/login: se menciona un “errorcito” porque parece que “carga y consulta a la vez” (no se detalla).
o	Hay “muchos archivos” no probados/por depurar (markdowns, archivos fuera del core).
o	Se removieron del repo cosas como entorno virtual/cache (basura generada al ejecutar), pero localmente alguien aún ve cambios sin commitear.
o	La estructura no esta limpia.

