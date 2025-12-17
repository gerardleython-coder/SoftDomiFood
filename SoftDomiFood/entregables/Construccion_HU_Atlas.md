Entendido. He analizado el archivo "SoftDomiFood_resumen_proceso.pdf" y comprendo que el objetivo es refinar, mejorar y endurecer el sistema actual de SoftDomiFood, enfocándose en la calidad, seguridad, rendimiento, observabilidad y mantenibilidad, sin introducir nuevas funcionalidades.

A continuación, presento las Historias de Usuario reescritas o refinadas, trazadas a los hallazgos AS-IS, riesgos y requisitos no funcionales identificados en el documento. Estas historias están diseñadas para ser claras, accionables y verificables, y buscan corregir ambigüedades, reducir riesgos y eliminar deuda técnica.

---

### Historias de Usuario Refinadas para Optimización y Calidad del Sistema

**1. Consolidación de Lógica y Mantenibilidad**

*   **US-027: Eliminar y Consolidar Lógica Duplicada del Backend Express en FastAPI**
    *   **Descripción:**
        Como desarrollador,
        Quiero eliminar la duplicación de lógica existente entre el backend `api/` (FastAPI) y el backend `backend/` (Express),
        Para reducir la deuda técnica, mejorar la mantenibilidad y mitigar el **riesgo RS-003 (Duplicación de lógica de backend)**, asegurando que todas las funcionalidades residan en un único backend FastAPI.
    *   **Criterios de Aceptación:**
        *   **Dado que** existe lógica de negocio redundante en el backend `backend/` (Express), **cuando** se completa la migración de toda su lógica relevante al backend `api/` (FastAPI), **entonces** el backend de Express se desactiva y se retira del despliegue, y todas las funcionalidades previamente gestionadas por Express operan exclusivamente desde FastAPI.
        *   **Dado que** la lógica ha sido consolidada en FastAPI, **cuando** se ejecutan las pruebas de integración y E2E para las funcionalidades migradas, **entonces** todas operan correctamente, demostrando paridad funcional con la implementación anterior.
        *   **Dado que** el backend de Express ha sido retirado, **cuando** se revisa el repositorio, **entonces** el código del backend Express es eliminado o archivado en una ubicación designada, asegurando que no haya confusión sobre la fuente de la lógica activa.
    *   **Prioridad:** Alta
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

*   **US-028: Refactorizar Código para Adherencia al Principio de Responsabilidad Única**
    *   **Descripción:**
        Como desarrollador,
        Quiero refactorizar las funciones y módulos existentes que presentan múltiples responsabilidades, asegurando que cada uno adhiera al Principio de Responsabilidad Única (SRP),
        Para mejorar la claridad del código, reducir la complejidad, facilitar el mantenimiento y la testabilidad, y reducir la probabilidad de introducir errores en SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** se identifican funciones o clases con más de una responsabilidad clara (ej. "crear pedido y enviar notificación" en una misma función), **cuando** se refactorizan, **entonces** cada nueva función/clase resultante tiene una única razón para cambiar y se enfoca en una tarea específica.
        *   **Dado que** se ha aplicado el SRP, **cuando** se revisa el código de los módulos `api/` y `worker/`, **entonces** la cohesión de las funciones es alta y el acoplamiento entre módulos es bajo, según métricas o estándares de revisión de código definidos.
        *   **Dado que** se implementan nuevas funcionalidades o se modifica código existente, **cuando** se desarrolla, **entonces** se aplica el Principio de Responsabilidad Única como estándar de diseño, verificado mediante revisiones de código.
    *   **Prioridad:** Media
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.1

*   **US-030: Eliminar el Uso Indiscriminado de `any` en Código TypeScript**
    *   **Descripción:**
        Como desarrollador,
        Quiero refactorizar el código TypeScript del `worker/` y los frontends (`frontend/`, `admin-frontend/`) para eliminar el uso indiscriminado del tipo `any`,
        Para mitigar el **riesgo RS-012 (Uso indiscriminado de `any` en TypeScript)**, mejorar la seguridad de tipos, la legibilidad y la mantenibilidad del código.
    *   **Criterios de Aceptación:**
        *   **Dado que** se revisa el código TypeScript existente en los módulos `worker/`, `frontend/` y `admin-frontend/`, **cuando** se encuentran declaraciones o usos del tipo `any` sin justificación explícita, **entonces** se refactorizan para utilizar tipos específicos, interfaces, tipos genéricos o uniones de tipos que reflejen con precisión la estructura de los datos.
        *   **Dado que** se desarrolla nuevo código TypeScript, **cuando** se escribe, **entonces** se prohíbe el uso de `any` a menos que sea estrictamente necesario (ej. para integración con librerías externas sin tipado) y esta excepción esté explícitamente documentada y justificada.
        *   **Dado que** se ha implementado esta mejora, **cuando** se ejecuta el linter configurado para TypeScript, **entonces** se detectan y reportan los usos no justificados de `any`, ayudando a mantener el estándar de calidad de código.
    *   **Prioridad:** Media
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.1

**2. Seguridad del Sistema**

*   **US-023: Externalizar y Automatizar la Rotación de Secretos del Sistema**
    *   **Descripción:**
        Como administrador de seguridad,
        Quiero que todos los secretos sensibles del sistema (como contraseñas de bases de datos, claves JWT y credenciales de servicios externos) estén externalizados y se puedan rotar automáticamente,
        Para mitigar el **riesgo RS-001 (Secretos hardcodeados o accesibles)**, evitar su almacenamiento en código fuente o archivos versionados, y mejorar la postura general de seguridad de SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** el sistema se despliega, **cuando** los servicios (`api/`, `worker/`, `database/`) necesitan acceder a secretos, **entonces** estos se cargan exclusivamente desde variables de entorno seguras (ej. inyectadas por Podman Compose) o un gestor de secretos, y no hay secretos sensibles hardcodeados o visibles en el repositorio de código.
        *   **Dado que** un secreto necesita ser rotado (ej. una clave JWT), **cuando** se actualiza en la fuente de configuración (variables de entorno o gestor), **entonces** los servicios afectados pueden recargar y utilizar el nuevo secreto sin requerir un despliegue completo o intervención manual extensiva, minimizando el tiempo de inactividad.
        *   **Dado que** se ha implementado la externalización de secretos, **cuando** se ejecuta un análisis de seguridad del código fuente (SAST), **entonces** no se detectan secretos sensibles expuestos directamente en el código.
    *   **Prioridad:** Alta
    *   **Feature:** FT-013 - Seguridad del Sistema
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

*   **US-024: Fortalecer la Seguridad y Gestión de Tokens JWT**
    *   **Descripción:**
        Como administrador de seguridad,
        Quiero asegurar que los tokens JWT utilizados para la autenticación y autorización en SoftDomiFood sean generados con secretos robustos y gestionados con duraciones controladas (Access Token: 15 min, Refresh Token: 7 días),
        Para proteger la autenticación de usuarios, reducir el riesgo de compromiso de tokens y cumplir con los requisitos de seguridad.
    *   **Criterios de Aceptación:**
        *   **Dado que** un usuario inicia sesión, **cuando** el backend `api/` genera un Access Token, **entonces** este token utiliza un secreto criptográficamente robusto (de al menos 32 caracteres generados aleatoriamente) y tiene una duración estricta de 15 minutos.
        *   **Dado que** un usuario inicia sesión, **cuando** el backend `api/` genera un Refresh Token, **entonces** este token utiliza un secreto criptográficamente robusto y tiene una duración estricta de 7 días.
        *   **Dado que** se presenta un JWT expirado o con una firma inválida al sistema, **cuando** el backend intenta validar la autenticación, **entonces** la solicitud es consistentemente rechazada y se registra un evento de autenticación fallida.
        *   **Dado que** se ha fortalecido la gestión de JWT, **cuando** un usuario legítimo intenta acceder a un recurso después de que su Access Token ha expirado pero su Refresh Token es válido, **entonces** puede obtener un nuevo Access Token sin necesidad de iniciar sesión nuevamente.
    *   **Prioridad:** Alta
    *   **Feature:** FT-013 - Seguridad del Sistema
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-023
    *   **Versión / Release:** 1.0

*   **US-025: Implementar Protección Robusta contra XSS y CSRF para Tokens de Sesión**
    *   **Descripción:**
        Como administrador de seguridad,
        Quiero asegurar que los tokens de sesión estén protegidos contra ataques de Cross-Site Scripting (XSS) y Cross-Site Request Forgery (CSRF),
        Para mitigar el **riesgo RS-002 (Vulnerabilidades XSS/CSRF por JWT en localStorage)**, evitar el robo de sesión y cumplir con los requisitos de seguridad de la plataforma SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** un usuario inicia sesión en la plataforma, **cuando** el backend emite tokens de sesión (Access y Refresh Tokens), **entonces** estos tokens no se almacenan en `localStorage` del lado del cliente.
        *   **Dado que** se utilizan cookies para gestionar los tokens de sesión, **cuando** estas cookies son enviadas al cliente, **entonces** se configuran con los atributos `HttpOnly` (para prevenir acceso vía JavaScript) y `SameSite=Strict` (o `Lax` si es necesario para usabilidad, con justificación) para proteger contra XSS y CSRF respectivamente.
        *   **Dado que** se ha implementado la protección, **cuando** se realizan pruebas de seguridad (ej. SAST, escaneo de vulnerabilidades web), **entonces** no se reportan vulnerabilidades críticas relacionadas con el almacenamiento de tokens en `localStorage` o falta de atributos de seguridad en las cookies.
    *   **Prioridad:** Alta
    *   **Feature:** FT-013 - Seguridad del Sistema
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

*   **US-026: Establecer Mecanismos de Rotación Regular para Credenciales Críticas**
    *   **Descripción:**
        Como administrador de seguridad,
        Quiero establecer y documentar un proceso para la rotación regular y automatizada de todas las credenciales críticas del sistema (ej. secretos JWT, credenciales de base de datos, claves de RabbitMQ),
        Para reducir el riesgo de compromiso a largo plazo y asegurar la conformidad con las mejores prácticas de seguridad, complementando la externalización de secretos (US-023).
    *   **Criterios de Aceptación:**
        *   **Dado que** las credenciales de los servicios tienen una vida útil definida, **cuando** se alcanza el período de rotación, **entonces** el sistema permite la actualización de estas credenciales en el fuente de secretos (ej. variables de entorno o gestor) y los servicios (`api/`, `worker/`, `database/`) las adoptan sin interrupción del servicio o con una interrupción mínima y planificada.
        *   **Dado que** se han rotado las credenciales (ej. el secreto JWT), **cuando** los servicios dependientes intentan autenticarse o validar, **entonces** utilizan las nuevas credenciales exitosamente, y las credenciales antiguas son invalidadas de forma segura.
        *   **Dado que** se ha implementado la rotación de credenciales, **cuando** se audita el proceso de seguridad, **entonces** existe documentación clara sobre la frecuencia, el método y los responsables de la rotación de cada tipo de credencial.
    *   **Prioridad:** Media
    *   **Feature:** FT-013 - Seguridad del Sistema
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-023
    *   **Versión / Release:** 1.1

*   **US-031: Eliminar SQL Embebido en Strings para Prevenir Inyecciones SQL**
    *   **Descripción:**
        Como desarrollador,
        Quiero refactorizar todo el código que actualmente utiliza sentencias SQL embebidas directamente en strings, reemplazándolas por un ORM (como Prisma) o consultas parametrizadas,
        Para mitigar el **riesgo RS-011 (Vulnerabilidades por SQL embebido)**, prevenir ataques de inyección SQL, y mejorar la seguridad y mantenibilidad de las interacciones con la base de datos PostgreSQL.
    *   **Criterios de Aceptación:**
        *   **Dado que** se revisa el código del backend `api/` y el `worker/` que interactúa con la base de datos, **cuando** se encuentran sentencias SQL construidas directamente concatenando strings o variables sin parametrización, **entonces** estas son refactorizadas para utilizar el ORM Prisma o, en su defecto, mecanismos de consultas parametrizadas.
        *   **Dado que** se ha eliminado el SQL embebido, **cuando** se ejecutan pruebas de seguridad (ej. SAST, escaneo de inyección SQL), **entonces** no se detectan vulnerabilidades de inyección SQL en los puntos de interacción con la base de datos.
        *   **Dado que** se desarrolla nuevo código de acceso a datos, **cuando** se escribe, **entonces** se utiliza exclusivamente el ORM Prisma o consultas parametrizadas, y esta práctica es validada en revisiones de código.
    *   **Prioridad:** Alta
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

**3. Confiabilidad y Operación**

*   **US-021: Garantizar Consistencia de Esquemas de Datos con Prisma**
    *   **Descripción:**
        Como desarrollador,
        Quiero asegurar que los esquemas de datos, gestionados por Prisma, sean consistentemente sincronizados entre el backend FastAPI y el worker Node.js/TypeScript,
        Para mitigar el **riesgo RS-006 (Inconsistencia de esquemas de BD)**, prevenir errores de integración y garantizar la integridad de los datos en toda la plataforma SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** se introduce o modifica el esquema de la base de datos en el proyecto, **cuando** se aplica la migración de Prisma, **entonces** el esquema de la base de datos se actualiza exitosamente y es accesible y consistente para ambos, el backend `api/` y el `worker/`, sin conflictos de tipos o estructuras.
        *   **Dado que** los servicios `api/` y `worker/` interactúan con la base de datos, **cuando** realizan operaciones de lectura/escritura, **entonces** no se producen errores de mapeo de datos o inconsistencias debido a diferencias en los modelos de Prisma.
        *   **Dado que** se ha establecido un proceso de sincronización, **cuando** se ejecuta el pipeline de CI, **entonces** se verifica automáticamente la consistencia del esquema de Prisma entre los componentes relevantes.
    *   **Prioridad:** Alta
    *   **Feature:** FT-011 - Base de Datos
    *   **Épica:** EP-001 - Plataforma de Pedidos en Línea Robusta y Segura
    *   **Dependencias:** FT-010, FT-012
    *   **Versión / Release:** 1.0

*   **US-022: Asegurar Procesamiento Asíncrono Robusto de Eventos de Pedidos**
    *   **Descripción:**
        Como parte de la arquitectura del sistema,
        Quiero que los eventos de pedidos se procesen de forma asíncrona y confiable utilizando RabbitMQ y el worker Node.js/TypeScript,
        Para desacoplar la creación de pedidos de su procesamiento complejo, mejorar la capacidad de respuesta del backend y garantizar la resiliencia del flujo de pedidos.
    *   **Criterios de Aceptación:**
        *   **Dado que** se crea un nuevo pedido a través del backend FastAPI, **cuando** el backend publica el evento de "Pedido Creado" en RabbitMQ, **entonces** el mensaje es encolado y el backend responde al cliente en menos de [X ms] sin esperar el procesamiento completo.
        *   **Dado que** el worker consume un evento de pedido de RabbitMQ, **cuando** lo procesa (ej., actualiza el estado detallado en la base de datos), **entonces** el estado del pedido se refleja correctamente en PostgreSQL y cualquier lógica de negocio asíncrona asociada se ejecuta sin errores.
        *   **Dado que** el flujo de procesamiento asíncrono está activo, **cuando** se simula una carga elevada de creación de pedidos, **entonces** el sistema mantiene su rendimiento de respuesta al cliente y el worker procesa la cola de mensajes de manera eficiente, sin acumulación excesiva de mensajes no procesados.
    *   **Prioridad:** Alta
    *   **Feature:** FT-012 - Procesamiento Asíncrono de Pedidos
    *   **Épica:** EP-001 - Plataforma de Pedidos en Línea Robusta y Segura
    *   **Dependencias:** FT-010, FT-011
    *   **Versión / Release:** 1.0

*   **US-032: Implementar Manejo de Errores Robusto y Específico en Servicios Backend**
    *   **Descripción:**
        Como desarrollador,
        Quiero implementar un sistema de manejo de errores robusto y específico en el backend FastAPI y el worker Node.js/TypeScript,
        Para asegurar respuestas claras y consistentes a los usuarios, facilitar la depuración con información contextual en los logs, y evitar la exposición de detalles internos sensibles del sistema.
    *   **Criterios de Aceptación:**
        *   **Dado que** ocurre un error previsible (ej. validación de entrada, recurso no encontrado) en el backend, **cuando** el sistema lo maneja, **entonces** se devuelve una respuesta HTTP con el código de estado apropiado y un mensaje de error específico y amigable para el usuario, sin exponer rastros de pila o detalles de implementación.
        *   **Dado que** ocurre un error inesperado (ej. fallo de conexión a DB, excepción interna) en el backend, **cuando** el sistema lo maneja, **entonces** se registra un log estructurado (US-029) con el contexto completo del error (stack trace, parámetros relevantes) y se devuelve una respuesta genérica al usuario (ej. "Error interno del servidor").
        *   **Dado que** se desarrolla o refactoriza código en los servicios backend, **cuando** se implementa la lógica de negocio, **entonces** se incluyen bloques de manejo de errores (`try-catch`, `except`) específicos para diferentes escenarios, diferenciando entre errores de negocio y errores técnicos.
        *   **Dado que** el sistema maneja errores, **cuando** los logs de errores son revisados, **entonces** proporcionan suficiente información contextual para identificar y diagnosticar la causa raíz del problema de manera eficiente.
    *   **Prioridad:** Alta
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-029
    *   **Versión / Release:** 1.0

*   **US-035: Implementar Pipelines de CI/CD Automatizados con GitHub Actions**
    *   **Descripción:**
        Como desarrollador y especialista en DevOps,
        Quiero establecer pipelines de Integración Continua (CI) y Despliegue Continuo (CD) completamente automatizados utilizando GitHub Actions,
        Para mitigar el **riesgo RS-004 (Falta de automatización CI/CD)**, asegurar la calidad del código, automatizar la validación y los despliegues de SoftDomiFood, y mejorar la confiabilidad y eficiencia operativa.
    *   **Criterios de Aceptación:**
        *   **Dado que** un desarrollador realiza un `push` a una rama de desarrollo o crea un `Pull Request`, **cuando** se activa el pipeline de CI, **entonces** se ejecutan automáticamente los linters (US-042), las pruebas unitarias y de integración (US-040), y el análisis estático de seguridad (SAST) (US-041) para todos los servicios (`api/`, `worker/`, frontends).
        *   **Dado que** el pipeline de CI pasa exitosamente y se aprueba un `Pull Request` para la rama principal, **cuando** se cumplen las condiciones de despliegue (ej. merge a `main`), **entonces** el pipeline de CD se activa y despliega automáticamente las nuevas versiones de los servicios en el entorno de staging o producción.
        *   **Dado que** el pipeline de CD se ejecuta, **cuando** finaliza, **entonces** los servicios desplegados están operativos y sus health checks (US-037) reportan un estado saludable.
    *   **Prioridad:** Alta
    *   **Feature:** FT-016 - Confiabilidad y Operación
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-040, US-041, US-042, US-037
    *   **Versión / Release:** 1.0

*   **US-037: Implementar Health Checks Estándar para Todos los Servicios Críticos**
    *   **Descripción:**
        Como operador,
        Quiero implementar endpoints de health check estandarizados para todos los servicios críticos de SoftDomiFood (`api/`, `worker/`, RabbitMQ, PostgreSQL),
        Para monitorear proactivamente su disponibilidad, estado operacional y dependencias clave, facilitando la detección temprana de problemas y la gestión de la confiabilidad del sistema.
    *   **Criterios de Aceptación:**
        *   **Dado que** los servicios `api/` y `worker/` están operativos, **cuando** se consulta su endpoint `/health` (o similar), **entonces** devuelve un código de estado HTTP 200 OK y un cuerpo de respuesta (ej. JSON) que indica un estado "UP" y, opcionalmente, el estado de sus dependencias críticas (ej. conexión a DB, RabbitMQ).
        *   **Dado que** un servicio (ej. `api/`) tiene un problema con una dependencia crítica (ej. la base de datos no es accesible), **cuando** se consulta su health check, **entonces** devuelve un código de estado HTTP 5xx (ej. 503 Service Unavailable) y un cuerpo de respuesta que detalla la dependencia fallida.
        *   **Dado que** el `podman-compose.yml` está configurado para health checks, **cuando** un servicio deja de responder a su health check, **entonces** Podman intenta reiniciar el contenedor automáticamente.
        *   **Dado que** los health checks están integrados con el sistema de monitoreo (US-036), **cuando** un health check falla persistentemente, **entonces** se dispara una alerta al equipo de operaciones.
    *   **Prioridad:** Alta
    *   **Feature:** FT-016 - Confiabilidad y Operación
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-036 (para integración con monitoreo)
    *   **Versión / Release:** 1.0

*   **US-038: Implementar Dead Letter Queue (DLQ) para Mensajes Fallidos de RabbitMQ**
    *   **Descripción:**
        Como operador,
        Quiero configurar una Dead Letter Queue (DLQ) en RabbitMQ para gestionar los mensajes que el `worker/` no puede procesar después de múltiples reintentos,
        Para mitigar el **riesgo RS-010 (Mensajes no procesados en RabbitMQ)**, evitar la pérdida de eventos críticos de pedidos, facilitar la depuración de errores asíncronos y mejorar la confiabilidad del procesamiento de pedidos.
    *   **Criterios de Aceptación:**
        *   **Dado que** el `worker/` intenta procesar un mensaje de la cola de pedidos y falla repetidamente (ej. 3 reintentos configurables), **cuando** el mensaje excede el número máximo de reintentos, **entonces** es redirigido automáticamente a la DLQ configurada en RabbitMQ, sin ser descartado.
        *   **Dado que** un mensaje es enviado a la DLQ, **cuando** se monitorea la DLQ (ej. a través de métricas en US-036 o la interfaz de RabbitMQ), **entonces** se genera una alerta (US-036) notificando al equipo de operaciones sobre la presencia de mensajes fallidos.
        *   **Dado que** hay mensajes en la DLQ, **cuando** el equipo de operaciones los revisa, **entonces** puede acceder a los detalles del mensaje fallido y, si la causa raíz se resuelve, tiene la capacidad de reprocesarlos manualmente o automáticamente.
    *   **Prioridad:** Media
    *   **Feature:** FT-016 - Confiabilidad y Operación
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** FT-012 (El worker es el consumidor principal), US-036 (para monitoreo y alertas)
    *   **Versión / Release:** 1.1

*   **US-039: Corregir Desfase Horario en la Programación de Pedidos**
    *   **Descripción:**
        Como desarrollador,
        Quiero implementar una solución robusta para corregir el desfase horario de aproximadamente 3 horas en la activación de pedidos programados,
        Para mitigar el **riesgo RS-007 (Desfase horario en pedidos programados)**, asegurar que los pedidos se preparen y entreguen exactamente a la hora programada por el cliente y cumplir con las reglas de negocio de SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** un cliente programa un pedido para una fecha y hora específica (ej. 14:00 del día siguiente), **cuando** se registra el pedido, **entonces** la hora de activación almacenada en la base de datos y utilizada por el `worker/` (FT-012) corresponde precisamente a la hora elegida por el cliente, ajustando correctamente cualquier consideración de zona horaria.
        *   **Dado que** el `worker/` es responsable de procesar pedidos programados, **cuando** llega la fecha y hora de activación de un pedido, **entonces** el `worker/` lo activa y cambia su estado a "en preparación" (o similar) en el minuto exacto programado, sin ningún desfase.
        *   **Dado que** se realizan pruebas de regresión para pedidos programados, **cuando** se simulan diferentes zonas horarias o cambios de horario (DST), **entonces** la hora de activación de los pedidos programados sigue siendo precisa y consistente.
    *   **Prioridad:** Alta
    *   **Feature:** FT-016 - Confiabilidad y Operación
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** FT-003 (Gestión de Pedidos Cliente), FT-012 (Procesamiento Asíncrono)
    *   **Versión / Release:** 1.0

**4. Observabilidad**

*   **US-029: Implementar Logging Estructurado Consistente en Producción**
    *   **Descripción:**
        Como desarrollador y operador,
        Quiero que todos los componentes del sistema (`api/`, `worker/`, frontends) utilicen logging estructurado (ej. en formato JSON) en producción, en lugar de `print()` o `console.log()`,
        Para mejorar la **observabilidad** (requisito no funcional), facilitar el análisis, la depuración de problemas y la generación de alertas, contribuyendo a la confiabilidad operacional de SoftDomiFood.
    *   **Criterios de Aceptación:**
        *   **Dado que** el sistema está en un entorno de producción, **cuando** los servicios (`api/`, `worker/`) generan eventos (ej. inicio de solicitud, errores, actualizaciones de estado), **entonces** los logs se emiten en formato JSON, incluyendo campos clave como `timestamp`, `level`, `service`, `message`, `correlationId` (si aplica) y detalles específicos del contexto.
        *   **Dado que** se revisa el código de los módulos `api/` y `worker/`, **cuando** se encuentran llamadas a `print()` o `console.log()` utilizadas para propósitos de logging en producción, **entonces** estas son reemplazadas por la solución de logging estructurado definida.
        *   **Dado que** los logs estructurados se envían a una herramienta de agregación (ej. ELK Stack, Grafana Loki), **cuando** se consultan, **entonces** permiten búsquedas y filtrados eficientes por campos específicos, demostrando la mejora en la depuración y análisis.
    *   **Prioridad:** Alta
    *   **Feature:** FT-014 - Mantenibilidad y Calidad de Código
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** FT-016 (Implica que la plataforma de observabilidad ya consume estos logs)
    *   **Versión / Release:** 1.0

*   **US-036: Implementar un Sistema Integral de Observabilidad (Logs, Métricas, Tracing, Alertas)**
    *   **Descripción:**
        Como operador,
        Quiero implementar un sistema de observabilidad completo para SoftDomiFood, incluyendo logs estructurados, métricas de rendimiento, trazabilidad distribuida y alertas proactivas,
        Para mitigar el **riesgo RS-005 (Falta de observabilidad)**, monitorear el estado y rendimiento del sistema en producción, diagnosticar problemas rápidamente y asegurar la confiabilidad operativa.
    *   **Criterios de Aceptación:**
        *   **Dado que** los servicios (`api/`, `worker/`) están en ejecución en producción, **cuando** ocurren eventos, **entonces** se generan logs estructurados (JSON, según US-029) que son centralizados en una plataforma de agregación (ej. Grafana Loki, ELK Stack) y son consultables de forma eficiente.
        *   **Dado que** los servicios (`api/`, `worker/`, RabbitMQ, PostgreSQL) están activos, **cuando** se monitorean, **entonces** se recogen métricas clave de rendimiento (CPU, memoria, latencia de solicitudes, tasa de errores, tamaño de cola de mensajes) y se visualizan en un dashboard (ej. Grafana).
        *   **Dado que** se realiza una solicitud de cliente (ej. crear pedido) que atraviesa múltiples servicios (frontend -> `api/` -> RabbitMQ -> `worker/` -> PostgreSQL), **cuando** se implementa la trazabilidad distribuida (ej. OpenTelemetry), **entonces** se puede seguir el flujo completo de la solicitud a través de todos los componentes.
        *   **Dado que** una métrica crítica excede un umbral predefinido (ej. tasa de errores > 5%, latencia > 500ms), **cuando** se configura una alerta, **entonces** el equipo de operaciones es notificado automáticamente a través de un canal definido (ej. Slack, email) en un plazo de [X] minutos.
    *   **Prioridad:** Alta
    *   **Feature:** FT-016 - Confiabilidad y Operación
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-029
    *   **Versión / Release:** 1.0

**5. Escalabilidad y Rendimiento**

*   **US-033: Implementar Estrategia de Caché con Invalidación Basada en Eventos**
    *   **Descripción:**
        Como desarrollador,
        Quiero implementar una estrategia de caché distribuida (ej. Redis) para datos de lectura frecuente y críticos (ej. menú de productos, cupones activos) en el backend FastAPI,
        Para optimizar el rendimiento del sistema, reducir la latencia de respuesta y disminuir la carga sobre la base de datos PostgreSQL, asegurando que los datos en caché estén siempre actualizados mediante invalidación basada en eventos.
    *   **Criterios de Aceptación:**
        *   **Dado que** se accede a datos frecuentemente consultados (ej. `GET /products`, `GET /coupons`) por múltiples clientes, **cuando** se implementa la caché, **entonces** el tiempo de respuesta para solicitudes repetidas de estos datos se reduce en al menos [X]% (ej. 50%) en comparación con la lectura directa de la base de datos.
        *   **Dado que** los datos en caché se modifican en la base de datos (ej. un administrador edita un producto), **cuando** se produce la actualización, **entonces** el sistema publica un evento de invalidación en RabbitMQ, y el mecanismo de caché lo consume para invalidar o actualizar la entrada correspondiente en la caché.
        *   **Dado que** la caché está activa, **cuando** se monitorean las métricas del sistema (US-036), **entonces** se observa una reducción en la carga de consultas a la base de datos para los datos cacheados.
    *   **Prioridad:** Media
    *   **Feature:** FT-015 - Escalabilidad y Rendimiento
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** FT-012 (para el mecanismo de eventos), US-036 (para métricas)
    *   **Versión / Release:** 1.1

*   **US-034: Asegurar el Despliegue y Escalabilidad Flexible de Servicios con Podman Compose**
    *   **Descripción:**
        Como operador,
        Quiero que el sistema SoftDomiFood sea completamente desplegable y escalable horizontalmente utilizando `podman-compose.yml`,
        Para garantizar la flexibilidad operativa, alta disponibilidad y capacidad de adaptación a diferentes cargas de trabajo, cumpliendo con el requisito de escalabilidad.
    *   **Criterios de Aceptación:**
        *   **Dado que** se requiere desplegar el sistema por primera vez o después de una actualización, **cuando** se ejecuta el comando `podman-compose up`, **entonces** todos los servicios (backend `api/`, `worker/`, `database/`, `frontend/`, `admin-frontend/`, RabbitMQ, caché si aplica) se inician correctamente, son accesibles y operan de forma interconectada según lo esperado.
        *   **Dado que** se necesita aumentar la capacidad de un servicio (ej. `api/` o `worker/`) para manejar más carga, **cuando** se ajusta el número de réplicas en la configuración de Podman Compose, **entonces** el servicio escala horizontalmente añadiendo nuevas instancias que se integran y responden a la carga de forma balanceada, sin interrupciones en los servicios existentes.
        *   **Dado que** el sistema está desplegado con Podman Compose, **cuando** una instancia de un servicio falla, **entonces** Podman intenta reiniciar automáticamente la instancia o las demás instancias activas continúan operando, manteniendo la disponibilidad del servicio.
    *   **Prioridad:** Alta
    *   **Feature:** FT-015 - Escalabilidad y Rendimiento
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

**6. Testabilidad y Calidad de Código Automatizada**

*   **US-040: Establecer Cobertura Integral de Pruebas Unitarias, de Integración y E2E**
    *   **Descripción:**
        Como desarrollador,
        Quiero establecer una cobertura integral de pruebas unitarias, de integración y End-to-End (E2E) para todos los componentes críticos de SoftDomiFood, incluyendo el flujo de pedidos y el `worker/`,
        Para mitigar el **riesgo RS-008 (Falta de cobertura de pruebas)**, garantizar la estabilidad, el correcto funcionamiento del sistema y la confiabilidad ante cambios futuros.
    *   **Criterios de Aceptación:**
        *   **Dado que** se ejecutan las pruebas unitarias para el backend `api/` y el `worker/`, **cuando** se completan, **entonces** se alcanza un porcentaje de cobertura de código superior al 80% y todas las pruebas pasan exitosamente, validando la lógica individual de componentes.
        *   **Dado que** se ejecutan las pruebas de integración, **cuando** se completan, **entonces** la interacción entre componentes clave (ej. `api/` con PostgreSQL, `api/` con RabbitMQ, `worker/` con RabbitMQ y PostgreSQL) funciona correctamente, asegurando que las integraciones son estables.
        *   **Dado que** se ejecutan las pruebas E2E, **cuando** se completan, **entonces** el flujo crítico de creación, seguimiento y gestión de pedidos (desde la interfaz del cliente hasta la actualización por el administrador) funciona de principio a fin, simulando la experiencia real del usuario.
        *   **Dado que** se ha establecido la cobertura de pruebas, **cuando** se realiza un `push` o `Pull Request`, **entonces** estas pruebas se ejecutan automáticamente como parte del pipeline de CI (US-035), bloqueando la integración si alguna falla.
    *   **Prioridad:** Alta
    *   **Feature:** FT-017 - Pruebas Automatizadas
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-035
    *   **Versión / Release:** 1.0

*   **US-041: Automatizar el Análisis Estático de Seguridad (SAST) en el Pipeline de CI**
    *   **Descripción:**
        Como desarrollador de seguridad,
        Quiero integrar y automatizar herramientas de Análisis Estático de Seguridad (SAST) en el pipeline de Integración Continua de SoftDomiFood,
        Para detectar y reportar vulnerabilidades de seguridad en el código fuente de forma temprana y proactiva, reduciendo el riesgo de introducir defectos de seguridad en producción.
    *   **Criterios de Aceptación:**
        *   **Dado que** se realiza un `push` a una rama de desarrollo o se abre un `Pull Request`, **cuando** se ejecuta el pipeline de CI (US-035), **entonces** la herramienta SAST analiza automáticamente el código de los servicios backend (`api/`, `worker/`) y frontends, buscando patrones de vulnerabilidades comunes (ej. inyección SQL, XSS, secretos expuestos).
        *   **Dado que** la herramienta SAST detecta una vulnerabilidad de seguridad crítica o de alto impacto, **cuando** finaliza el análisis, **entonces** el pipeline de CI falla o emite una advertencia clara, y se genera un informe detallado que incluye la ubicación del problema, su descripción y recomendaciones de corrección.
        *   **Dado que** se ha integrado SAST, **cuando** se revisan los resultados de los análisis, **entonces** se observa una reducción en la cantidad de nuevas vulnerabilidades introducidas con cada ciclo de desarrollo, y el equipo tiene un plan para abordar las vulnerabilidades existentes.
    *   **Prioridad:** Alta
    *   **Feature:** FT-017 - Pruebas Automatizadas
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Dependencias:** US-035
    *   **Versión / Release:** 1.0

*   **US-042: Implementar Linters y Pre-commit Hooks para Forzar Estándares de Calidad de Código**
    *   **Descripción:**
        Como desarrollador,
        Quiero integrar linters automáticos y configurar pre-commit hooks para todos los repositorios de código de SoftDomiFood (Python, TypeScript, React),
        Para asegurar la calidad, consistencia y estilo del código, detectar errores comunes de forma temprana (antes de la subida al repositorio), y mejorar la experiencia de desarrollo.
    *   **Criterios de Aceptación:**
        *   **Dado que** un desarrollador intenta realizar un `git commit`, **cuando** se ejecuta el pre-commit hook, **entonces** el código modificado se formatea automáticamente (ej. con Black para Python, Prettier para JS/TS) y se valida contra las reglas del linter configurado (ej. ESLint, Flake8).
        *   **Dado que** el linter o el formateador detecta un error de estilo, un problema de calidad de código o una violación de las reglas (ej. uso de `any` no justificado, SQL embebido), **cuando** se ejecuta el pre-commit hook, **entonces** el commit es bloqueado, y se muestra un mensaje claro indicando los problemas que deben corregirse antes de permitir el commit.
        *   **Dado que** se ha implementado esta medida, **cuando** se revisan los `Pull Requests`, **entonces** la cantidad de comentarios relacionados con el estilo o la calidad básica del código se reduce significativamente, permitiendo un enfoque en la lógica de negocio.
    *   **Prioridad:** Alta
    *   **Feature:** FT-018 - Experiencia de Desarrollo
    *   **Épica:** EP-002 - Optimización de la Operación y Calidad del Sistema
    *   **Versión / Release:** 1.0

---

Estas historias de usuario abordan de manera específica los puntos clave de mejora y los riesgos identificados en el documento, proporcionando una base sólida para un backlog de refinamiento técnico y operativo para SoftDomiFood.