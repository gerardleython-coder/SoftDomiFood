# Plan de Pruebas Maestro

## 1. Introducción

### 1.1 Objetivo
Definir la estrategia, el alcance, los entornos y el enfoque de pruebas para validar las Historias de Usuario (HU) aprobadas del sistema, asegurando calidad funcional, no funcional y alineación con los criterios INVEST.

### 1.2 Contexto del Proyecto
El sistema permite a los clientes acceder de forma rápida y confiable, realizar pedidos con direcciones existentes o nuevas, confirmar pedidos sin bloqueos, proteger la información sensible y garantizar la ejecución exacta de pedidos programados.

### 1.3 Documentos de Referencia
- Backlog refinado de Historias de Usuario (HU-01 a HU-06)
- Documento de Historias de Usuario aprobado
- Arquitectura lógica del sistema

---

## 2. Alcance de las Pruebas

### 2.1 En Alcance (In-Scope)
Se validarán las siguientes Historias de Usuario:

- **HU-01** – Acceso rápido y confiable al sistema
- **HU-02** – Finalizar un pedido usando una dirección existente
- **HU-03** – Añadir una nueva dirección válida al realizar un pedido
- **HU-04** – Creación instantánea de pedidos sin bloqueos
- **HU-05** – Protección segura de la información del sistema
- **HU-06** – Entrega de pedidos programados a la hora exacta

Incluye:
- Cumplimiento de criterios de aceptación
- Flujos end-to-end de pedido
- Pruebas funcionales y no funcionales
- Seguridad y manejo de datos sensibles
- Precisión temporal y manejo de zonas horarias

### 2.2 Fuera de Alcance (Out-of-Scope)
No se probará:

- Logística física de entrega de pedidos
- Integraciones con terceros no controlados por el sistema
- Configuración interna de herramientas de CI/CD
- Detalles puramente estéticos de la interfaz
- Optimización de infraestructura no observable por el usuario

### 2.3 Supuestos y Restricciones
- El sistema maneja fechas y horas internamente en UTC
- Los entornos de prueba estarán disponibles y estables
- Los datos de prueba no corresponden a información real
- Las tareas técnicas (CI/CD, refactorización profunda) no se validan como HU

---

## 3. Entorno de Pruebas

### 3.1 Arquitectura del Entorno

- **Contenedores:** Docker / Podman
- **Orquestación:** Docker Compose para QA
- **Base de Datos:** Instancias aisladas por ambiente
- **Mensajería:** Simulada en QA cuando aplique

### 3.2 Ambientes

| Ambiente | Propósito | Configuración Clave |
|--------|----------|---------------------|
| Desarrollo | Pruebas unitarias | Datos mock, servicios simulados |
| QA | Pruebas de integración y sistema | Infraestructura similar a producción |
| Producción | Pruebas de aceptación | Monitoreo y observabilidad habilitados |

### 3.3 Datos de Prueba

- Usuarios con distintos perfiles
- Direcciones válidas e inválidas
- Pedidos inmediatos y programados
- Escenarios de alta concurrencia
- Casos límite de tiempo (DST, zonas horarias)

---

## 4. Estrategia de Pruebas

### 4.1 Tipos de Pruebas

- **Pruebas Unitarias**
  - Lógica de negocio
  - Validaciones de datos

- **Pruebas de Integración**
  - Comunicación frontend-backend
  - Persistencia de pedidos y direcciones

- **Pruebas de Sistema**
  - Flujos completos de usuario
  - Confirmación y programación de pedidos

- **Pruebas de Rendimiento**
  - Tiempos de respuesta (P90 / P95)
  - Concurrencia

- **Pruebas de Seguridad**
  - Manejo de secretos
  - Auditoría de accesos

- **Pruebas de Precisión Temporal**
  - Programación exacta de pedidos
  - Conversión UTC ↔ hora local

### 4.2 Enfoque Manual vs Automatizado

| Tipo de Prueba | Enfoque |
|---------------|--------|
| Unitarias | Automatizadas |
| Integración | Automatizadas |
| Sistema | Mixto |
| Rendimiento | Automatizadas |
| Seguridad | Mixto |
| Aceptación | Manual |

---

## 5. Entregables de Pruebas

- Plan de Pruebas Maestro (este documento)
- Casos de prueba trazados a HU
- Evidencias de ejecución
- Reportes de defectos
- Informe final de calidad

---

## 6. Criterios de Aceptación y Salida

### 6.1 Criterios de Aprobación

- 100% de criterios de aceptación validados
- Sin defectos críticos abiertos
- Métricas de rendimiento dentro de lo definido

### 6.2 Criterios de Suspensión

- Inestabilidad del ambiente
- Bloqueos críticos sin workaround
- Datos de prueba corruptos

---

## 7. Riesgos y Mitigación

| Riesgo | Impacto | Mitigación |
|------|--------|-----------|
| Degradación de rendimiento | Alto | Pruebas de carga tempranas |
| Errores de zona horaria | Alto | Pruebas exhaustivas UTC |
| Exposición de datos | Alto | Pruebas de seguridad |
| Dependencias no controladas | Medio | Aislamiento de entornos |

---

## 8. Roles y Responsabilidades

- **QA Lead:** Definición y control del plan
- **QA Engineer:** Diseño y ejecución de pruebas
- **Desarrollo:** Corrección de defectos
- **PO / Negocio:** Validación de aceptación

---

## 9. Historial de Versiones

| Versión | Fecha | Descripción |
|-------|------|------------|
| 1.0 | 2026-03-18 | Versión inicial del Plan de Pruebas Maestro |

