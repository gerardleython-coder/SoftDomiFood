# REFINED_BACKLOG.md
> Fecha de Validación: 24 de Mayo de 2024
> Auditor: Agile INVEST Auditor (Gemini)

## [HU-01] Acceso rápido y confiable al sistema
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero que el acceso al sistema sea rápido y confiable al iniciar sesión y consultar productos, para poder navegar y realizar pedidos sin demoras ni interrupciones.
* **Criterios de Aceptación (Lista):**
    * [ ] El tiempo de respuesta de las operaciones de acceso (login) y consulta de productos es ≤ 50 ms en el percentil 90 (P90).
    * [ ] Ante picos de alta concurrencia de usuarios, el sistema mantiene tiempos de respuesta estables sin degradación notable.
    * [ ] No se presentan errores intermitentes (timeouts o 500s) durante el flujo de autenticación o navegación por el catálogo inicial.
* **Notas de Estimación:** Complejidad Media. Requiere optimización de la lógica de backend y posiblemente implementación de caché en puntos críticos.

---

## [HU-02] Finalizar un pedido usando una dirección existente
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero finalizar mi pedido seleccionando una de mis direcciones guardadas, para completar la compra de forma rápida y sin tener que volver a ingresar mis datos de envío.
* **Criterios de Aceptación (Lista):**
    * [ ] El sistema muestra una lista clara de al menos una dirección utilizada o guardada previamente por el usuario.
    * [ ] Al seleccionar una dirección de la lista, los datos de envío del pedido se actualizan y registran correctamente en la base de datos de pedidos.
    * [ ] Si el usuario intenta avanzar sin seleccionar una dirección válida, el sistema impide el paso al pago y muestra un mensaje de advertencia claro.
* **Notas de Estimación:** Complejidad Baja. Se asume que la base de datos de perfiles de usuario ya cuenta con el almacenamiento de direcciones.

---

## [HU-03] Añadir una nueva dirección válida al realizar un pedido
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero añadir una nueva dirección de entrega durante el proceso de compra, para asegurar que mi pedido llegue a cualquier ubicación correcta sin errores logísticos.
* **Criterios de Aceptación (Lista):**
    * [ ] El sistema valida automáticamente que el formato de la nueva dirección ingresada sea correcto (Código Postal, Ciudad, Calle).
    * [ ] Si la validación automática detecta una inconsistencia, el sistema permite al usuario corregirla o continuar bajo su responsabilidad tras una advertencia clara.
    * [ ] La nueva dirección se asocia correctamente al pedido actual y se guarda en el historial del usuario para futuras compras.
* **Notas de Estimación:** Complejidad Media. Requiere integración con servicios de validación de mapas o geocodificación.

---

## [HU-04] Creación instantánea de pedidos sin bloqueos
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero que la confirmación de mi pedido sea inmediata después de hacer clic en "comprar", incluso en momentos de alta demanda del sistema, para tener una experiencia de compra fluida.
* **Criterios de Aceptación (Lista):**
    * [ ] El sistema devuelve una confirmación visual de "Pedido Recibido" en ≤ 100 ms en el percentil 95 (P95).
    * [ ] Cualquier fallo en el procesamiento posterior (notificaciones, inventario) no bloquea ni revierte la confirmación inicial mostrada al cliente en el frontend.
    * [ ] El pedido se registra de forma asíncrona garantizando que no haya pérdida de datos incluso ante errores temporales de infraestructura.
* **Notas de Estimación:** Complejidad Alta. Requiere implementación de arquitectura basada en eventos (colas de mensajería).

---

## [HU-05] Protección segura de la información del sistema
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero que mi información personal y la operación general del sistema estén protegidas frente a accesos no autorizados, para confiar plenamente en la seguridad del servicio.
* **Criterios de Aceptación (Lista):**
    * [ ] Las credenciales de base de datos y llaves API sensibles no están expuestas en el código fuente ni en configuraciones públicas.
    * [ ] El sistema permite la rotación de secretos y credenciales de infraestructura en un plazo máximo de 5 minutos sin causar caídas de servicio para el usuario.
    * [ ] Todo acceso a información sensible de configuración del sistema queda registrado en logs de auditoría inmutables.
* **Notas de Estimación:** Complejidad Media-Alta. Se enfoca en la implementación de gestores de secretos y políticas de seguridad Zero Trust.

---

## [HU-06] Entrega de pedidos programados a la hora exacta
**Estado:** ✅ CERTIFICADA INVEST
* **Descripción:** Como cliente, quiero que mis pedidos programados se ejecuten y entreguen exactamente a la hora que seleccioné, para organizar mi tiempo sin sufrir retrasos ni adelantos inesperados.
* **Criterios de Aceptación (Lista):**
    * [ ] El sistema procesa la orden basándose en la hora local exacta seleccionada por el usuario en el frontend.
    * [ ] La desviación máxima permitida entre la hora programada y la ejecución técnica del pedido es de ± 1 minuto.
    * [ ] El comportamiento de la programación es consistente y correcto independientemente de la zona horaria del cliente o del servidor.
* **Notas de Estimación:** Complejidad Media. Requiere manejo estricto de objetos DateTime en formato UTC y conversiones dinámicas.