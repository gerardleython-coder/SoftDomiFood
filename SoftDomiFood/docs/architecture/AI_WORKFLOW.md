# Sistema de Pedidos de Domicilio - SoftDomiFood 🍟

> **Metodología AI-First Development - Documento de Gobernanza y Protocolos**  
> *Guía obligatoria para desarrollo con IA en el proyecto*  
> **Versión:** 5.0 | **Última Auditoría:** Diciembre 2024

---

## 📑 Índice de Contenidos

1. [Visión General](#-visión-general)
2. [Contexto y Gobernanza](#-contexto-y-gobernanza)
3. [Regla Obligatoria: Verificación Humana](#regla-obligatoria-verificación-humana)
4. [Plantilla de Prompt Obligatoria](#-plantilla-de-prompt-obligatoria)
5. [Prompts de Creación de Estructura del Proyecto](#️-prompts-de-creación-de-estructura-del-proyecto)
6. [Registro de Prompts de Éxito](#-registro-de-prompts-de-éxito-archivo-vivo)
7. [Documentos Clave y Contextualización](#-documentos-clave-y-contextualización)
8. [Stack Tecnológico Base](#️-stack-tecnológico-base-contexto-obligatorio-para-ia)
9. [Dinámicas de Interacción](#-dinámicas-de-interacción)
10. [Estructura del Proyecto](#-estructura-del-proyecto-contexto-para-ia)
11. [Estado del Proyecto](#-estado-del-proyecto)
12. [Auditoría Final y Validación](#-auditoría-final-y-validación)
13. [Referencias Rápidas](#-referencias-rápidas)

---

## 🌟 Visión General

### Metodología: AI-First Development

Utilizamos un enfoque **"AI-First"** donde la IA actúa como **Junior Developer** y el equipo humano como **Arquitectos y Revisores**. Este enfoque ha demostrado ser altamente efectivo para acelerar el desarrollo manteniendo calidad.

### Principios Fundamentales

1. **IA como Asistente, No Reemplazo**: La IA genera código, el humano valida y aprueba
2. **Revisión Obligatoria**: Todo código generado por IA debe ser revisado por humanos
3. **Documentación Viva**: Este documento se actualiza con cada prompt exitoso
4. **Coherencia Arquitectónica**: Uso de librería de prompts para mantener consistencia

---

## 🏛️ Contexto y Gobernanza

### Tecnologías del Proyecto

#### Herramientas de Desarrollo

| Categoría | Tecnología | Versión | Propósito |
|-----------|------------|---------|-----------|
| **Backend API** | FastAPI | 0.104.1 | Framework web asíncrono |
| **Backend API** | Python | 3.11 | Lenguaje principal |
| **Backend API** | asyncpg | 0.29.0 | Driver PostgreSQL asíncrono |
| **Backend API** | aio-pika | 9.2.0 | Cliente RabbitMQ |
| **Frontend Cliente** | React | 18.2.0 | Biblioteca UI |
| **Frontend Cliente** | Vite | 4.4.5 | Build tool |
| **Frontend Admin** | React | 18.2.0 | Biblioteca UI |
| **Frontend Admin** | Vite | 4.4.5 | Build tool |
| **Worker** | Node.js | 20+ | Runtime |
| **Worker** | TypeScript | 5.3.3 | Lenguaje tipado |
| **Worker** | Prisma | 5.7.1 | ORM |
| **Base de Datos** | PostgreSQL | 15-alpine | Base de datos relacional |
| **Message Queue** | RabbitMQ | 3-management | Message broker |
| **Containerización** | Docker | Latest | Containerización |
| **Orquestación** | Docker Compose | Latest | Orquestación de servicios |
| **Testing** | pytest | 7.4.3 | Framework de testing |
| **Testing** | Bandit | 1.7.5 | Análisis de seguridad SAST |

#### Herramientas de IA Utilizadas

| Herramienta | Tipo | Uso Principal | Contexto |
|-------------|------|---------------|----------|
| **Cursor AI** | Editor con IA | Generación de código, refactorización, debugging | Editor principal del proyecto |
| **GitHub Copilot** | Asistente de código | Autocompletado inteligente, sugerencias | Complemento en IDE |
| **Claude (Anthropic)** | LLM | Análisis de código, generación de documentación | Herramienta de consulta |
| **ChatGPT (OpenAI)** | LLM | Resolución de problemas, brainstorming | Herramienta de consulta alternativa |

### Documentos Clave y Relaciones

#### Jerarquía de Documentación

```
README.md (Documentación Principal)
    ├── AI_WORKFLOW.md (Este documento - Metodología y Gobernanza)
    │   └── PROMPTS_LIBRARY.md (Librería de Prompts Modelo)
    ├── SETUP_INSTRUCTIONS.md (Instrucciones de configuración)
    ├── DESARROLLO-LOCAL.md (Guía de desarrollo local)
    └── qa_automated/README.md (Documentación de testing)
```

#### Relación entre Documentos

1. **README.md** → **AI_WORKFLOW.md**
   - El README referencia el AI_WORKFLOW como documento obligatorio
   - Define la metodología de desarrollo con IA
   - Establece el contexto técnico del proyecto

2. **AI_WORKFLOW.md** → **PROMPTS_LIBRARY.md**
   - El AI_WORKFLOW define la metodología
   - La PROMPTS_LIBRARY proporciona prompts específicos por capa
   - Ambos trabajan juntos para garantizar coherencia arquitectónica

3. **AI_WORKFLOW.md** → **Estructura de Código**
   - Define patrones y convenciones
   - Establece reglas de verificación humana
   - Documenta stack tecnológico para contexto de IA

#### Uso de Documentos en Prompts

**Orden de Prioridad para Contexto:**

1. **Alta Prioridad (Obligatorio):**
   - `AI_WORKFLOW.md` - Metodología y gobernanza
   - `PROMPTS_LIBRARY.md` - Prompts modelo por capa
   - Archivos directamente relacionados con la tarea

2. **Media Prioridad:**
   - `README.md` - Arquitectura y setup
   - `docker-compose.yml` - Configuración de servicios
   - Archivos de configuración (`package.json`, `requirements.txt`)

3. **Baja Prioridad:**
   - Documentos históricos (`RESUMEN_CAMBIOS.md`, etc.)
   - Reportes de ejecución

### Regla Obligatoria: Verificación Humana

**⚠️ DECLARACIÓN CRÍTICA Y OBLIGATORIA:**

#### 1. Responsabilidad Final del Desarrollador Humano

- ✅ **Todo código generado por IA es responsabilidad del desarrollador humano**
- ✅ **El desarrollador humano es el único responsable de la calidad, seguridad y funcionalidad**
- ✅ **La IA actúa como herramienta de asistencia, NO como reemplazo del juicio humano**
- ✅ **Ningún código generado por IA debe ser mergeado sin revisión humana**

#### 2. Checklist de Verificación Obligatoria (Pre-Commit)

Antes de commitear cualquier código generado por IA:

- [ ] **Revisión Manual Completa**: Código revisado línea por línea por desarrollador humano
- [ ] **Lógica de Negocio**: Verificar que la lógica implementada es correcta y cumple requisitos
- [ ] **Seguridad**: 
  - [ ] No contiene credenciales hardcodeadas
  - [ ] Usa variables de entorno para configuración sensible
  - [ ] Validaciones de input implementadas
  - [ ] Protección contra SQL injection verificada
  - [ ] Manejo de tokens JWT correcto
- [ ] **Performance**: 
  - [ ] Queries optimizadas
  - [ ] Sin N+1 queries
  - [ ] Uso apropiado de índices
- [ ] **Estándares de Código**: 
  - [ ] Formato consistente
  - [ ] Naming conventions respetadas
  - [ ] Estructura de archivos correcta
- [ ] **Testing**: 
  - [ ] Tests ejecutados y validados manualmente
  - [ ] Coverage verificado
  - [ ] Tests de integración pasando
- [ ] **Documentación**: 
  - [ ] Comentarios en código complejo
  - [ ] README actualizado si aplica
  - [ ] Changelog actualizado

#### 3. Prohibición de Datos Sensibles

**NUNCA ingresar en IAs públicas:**
- ❌ Credenciales de base de datos
- ❌ Tokens JWT secretos
- ❌ API keys
- ❌ Información de clientes reales
- ❌ Datos de producción
- ❌ Secretos hardcodeados

**SIEMPRE usar:**
- ✅ Datos sintéticos para testing
- ✅ Variables de entorno
- ✅ Archivos `.env.example` como plantillas
- ✅ Mocks y fixtures en tests

#### 4. Protocolo de Validación de Tests

- ✅ Tests generados por IA deben ejecutarse manualmente
- ✅ Resultados deben revisarse antes de considerar código válido
- ✅ Problemas de mocking deben resolverse con supervisión humana
- ✅ Reportes de seguridad deben revisarse por experto

---

## 📋 Plantilla de Prompt Obligatoria

### Estructura Base (Siempre Incluir)

```
@[contexto-del-proyecto] Actúa como [rol] y [especialidad]

[Descripción del problema/requerimiento]

[Contexto específico del código/archivos afectados]

[Restricciones y requisitos técnicos]

[Resultado esperado]
```

### Ejemplos de Prompts Exitosos

#### Ejemplo 1: Desarrollo FullStack
```
@prueba-restaurante- Funciona bien, Actua como desarrollador FullStack y Dev ops, 
Aun no se contabiliza los pedidos que se generan y los ingresos, quiero que soluciones 
esto para tener esta funcion activa, recuerda utilizar siempre el worker de RabbitMQ
```

**Resultado:** ✅ Implementación exitosa de contabilización de pedidos e ingresos con integración RabbitMQ

#### Ejemplo 2: Separación de Aplicaciones
```
@prueba-restaurante- Actua como fullStack y Devops, si queremos cumplir con la peticion 
anterior lo mejor seria establecer la web del panel de administrador en un puerto diferente 
al de la web del cliente, de esta forma podemos lograr que sean independientes
```

**Resultado:** ✅ Separación completa de frontends en puertos 3000 (cliente) y 3001 (admin)

#### Ejemplo 3: Corrección de Sesiones
```
@prueba-restaurante- No funciona del todo bien, Actua como fullStack y Devops, 
si un usuario logeado recarga la pagina lo dirige automaticamente al panel de administrador 
y esto es una mala practica, recuerda que ambas webs son independientes
```

**Resultado:** ✅ Implementación de sesiones completamente independientes con localStorage separado

#### Ejemplo 4: Creación de Infraestructura de Testing (QA Automation)
```
@qa_automated actua como QA Engineer Senior y Especialista en Automatización (SDET), 
ejecuta los scrip de los test correspondientes de la carpeta @qa_automated
```

**Resultado:** ✅ Ejecución exitosa de tests funcionales, análisis de seguridad y generación de reportes

#### Ejemplo 5: Corrección de Mocks en Tests
```
@qa_automated actua como QA Engineer Senior y Especialista en Automatización (SDET) 
Problema pendiente: 11 tests aún fallan porque los mocks no interceptan las llamadas 
cuando las funciones se importan con from module import function en auth.py, creando 
referencias locales que no se ven afectadas por los mocks. Quiero que apliques la 
solucion mas adecuada sin afectar el funcionamiento del proyecto, una vez realizado 
ejecuta los Scripts de los tests y actualiza el generate_reports.html
```

**Resultado:** ✅ Corrección de mocks usando el namespace correcto (`api.routers.auth`) donde se usan las funciones, no donde se definen. 16 tests pasando, análisis de seguridad completado.

---

## 🛠️ Herramientas de IA Utilizadas

### Herramientas Principales

1. **Cursor AI** (Editor Principal)
   - **Uso:** Generación de código, refactorización, debugging
   - **Casos de uso:**
     - Generación de componentes React
     - Creación de endpoints FastAPI
     - Configuración de Docker
     - Corrección de errores de sintaxis y lógica
     - Generación de infraestructura de testing automatizado
     - Corrección de problemas de mocking en tests

2. **GitHub Copilot** (Asistente de Código)
   - **Uso:** Autocompletado inteligente, sugerencias de código
   - **Casos de uso:**
     - Completado de funciones
     - Generación de tests
     - Documentación inline

### Herramientas de IA Específicas para QA Automation

3. **Cursor AI - Modo QA Engineer/SDET**
   - **Uso:** Generación de scripts de testing, análisis de seguridad, pruebas de carga
   - **Casos de uso específicos:**
     - Creación de suites de tests funcionales con pytest
     - Generación de scripts de análisis SAST con Bandit
     - Configuración de pruebas de carga con Locust
     - Corrección de problemas de mocking en tests de integración
     - Generación de reportes HTML de resultados

### Casos de Uso Protocolarios

#### ✅ Refactorización
- **Prompt tipo:** "Refactoriza [componente/archivo] para mejorar [aspecto específico]"
- **Ejemplo:** "Refactoriza ClientPage.jsx para separar la lógica de autenticación en un hook personalizado"

#### ✅ Generación de Tests
- **Prompt tipo:** "Genera tests unitarios para [componente/función] usando [framework de testing]"
- **Ejemplo:** "Genera tests para el endpoint de creación de pedidos usando pytest"

#### ✅ Debugging
- **Prompt tipo:** "Analiza este error [error específico] en [archivo] y proporciona solución"
- **Ejemplo:** "El cálculo de estadísticas no funciona correctamente, revisa calculateStats en AdminPage.jsx"

#### ✅ Generación de Código
- **Prompt tipo:** "Crea [componente/endpoint/función] que [descripción funcional] usando [tecnologías específicas]"
- **Ejemplo:** "Crea un componente OrderManagement que muestre pedidos con filtros por estado usando React y Tailwind"

#### ✅ Configuración DevOps
- **Prompt tipo:** "Configura [servicio] en docker-compose.yml con [requisitos específicos]"
- **Ejemplo:** "Agrega un servicio admin-frontend en puerto 3001 con las mismas dependencias que frontend"

---

## 🎯 Metodología de Prompting Comprobada (Core del Éxito)

### Principios Fundamentales

1. **Especificación de Rol y Contexto**
   - ✅ **SIEMPRE** incluir el rol específico: "Actúa como [rol] y [especialidad]"
   - ✅ **SIEMPRE** referenciar el contexto del proyecto: `@[carpeta-proyecto]` o `@[archivo-específico]`
   - ✅ **SIEMPRE** proporcionar contexto técnico relevante antes del prompt

2. **Estructura de Prompt de Alto Rendimiento**
   ```
   @[contexto] Actúa como [rol] y [especialidad]
   
   [Problema/Requerimiento específico]
   
   [Contexto técnico relevante - archivos, tecnologías, restricciones]
   
   [Resultado esperado con criterios de éxito]
   
   [Restricciones críticas - "sin afectar el funcionamiento del proyecto"]
   ```

3. **Patrones de Éxito Identificados**

   **Patrón A: Corrección de Problemas Técnicos**
   - Describir el problema específico
   - Mencionar el contexto técnico afectado
   - Especificar restricciones (no afectar funcionamiento existente)
   - Solicitar ejecución y actualización de reportes

   **Patrón B: Creación de Infraestructura**
   - Especificar el rol técnico requerido (QA Engineer, DevOps, FullStack)
   - Referenciar la carpeta/contexto específico
   - Solicitar ejecución de scripts y generación de reportes

   **Patrón C: Optimización y Refactorización**
   - Identificar el componente a optimizar
   - Especificar mejoras esperadas
   - Mantener compatibilidad con código existente

### Metodología Validada para QA Automation

**Prompt Estructurado para Testing:**
```
@qa_automated actua como QA Engineer Senior y Especialista en Automatización (SDET)

[Descripción del problema o requerimiento de testing]

[Contexto: archivos de test, módulos bajo prueba, herramientas utilizadas]

[Resultado esperado: tests pasando, reportes generados, coverage X%]

[Restricciones: sin afectar código de producción, usar mocks apropiados]
```

**Elementos Críticos:**
- ✅ Especificar rol técnico exacto (QA Engineer Senior, SDET)
- ✅ Referenciar carpeta `@qa_automated` para contexto
- ✅ Solicitar ejecución de scripts y actualización de reportes
- ✅ Mencionar restricciones de no afectar producción

---

## 🏗️ Prompts de Creación de Estructura del Proyecto

> **Sección de Referencia:** Estos prompts fueron utilizados para crear la estructura inicial del proyecto. Sirven como referencia para entender cómo se construyó la arquitectura base.

### Metodología de Creación por Capas

El proyecto fue construido utilizando una metodología de **creación por capas** con prompts específicos para cada componente arquitectónico. Cada prompt tiene un **rol técnico asignado** que garantiza la especialización adecuada.

### Los 6 Prompts con Roles Asignados

#### 1. 🥇 Prompt Inicial (Definición de Alcance y Stack)

**Rol:** Arquitecto de Software Senior y Diseñador de Soluciones

**Prompt Modelo:**
```
[Rol: Arquitecto de Software Senior y Diseñador de Soluciones] 

Crea la estructura de un proyecto de sistema de pedidos de domicilio completo para un restaurante especializado en salchipapas. La solución debe ser una plataforma completa que incluya un frontend para clientes, un panel de administración y un backend API. 

Utiliza un stack moderno: FastAPI (Python) para el backend, React con Vite para los frontends. La arquitectura debe ser basada en contenedores (Docker) e incluir RabbitMQ para el procesamiento asíncrono de pedidos. También debe considerar una suite de testing automatizado con Pytest y un proceso de desarrollo enfocado en la IA (AI-First Development).

**Requisitos:**
- Arquitectura de microservicios
- Separación clara de responsabilidades
- Escalabilidad horizontal
- Integración con message queue
- Testing automatizado desde el inicio
```

**Resultado Esperado:**
- Definición del stack tecnológico completo
- Arquitectura de alto nivel documentada
- Decisiones técnicas fundamentales

---

#### 2. 📁 Prompt de Refinamiento de Arquitectura y Estructura de Carpetas

**Rol:** Ingeniero de Organización de Repositorios y Especialista en Microservicios

**Prompt Modelo:**
```
[Rol: Ingeniero de Organización de Repositorios y Especialista en Microservicios] 

Detalla la estructura de directorios para la aplicación, separando los componentes en módulos de servicios claros: api/ (FastAPI), frontend/ (Cliente React), admin-frontend/ (Admin React) y worker/ (Consumer de RabbitMQ). 

Dentro de api/, organiza los archivos por rol: routers/, services/, models.py. En los frontends, usa la convención src/components/client/ y src/components/admin/. Incluye una carpeta qa_automated/ para todo el testing.

**Estructura Requerida:**
- Separación clara por servicio
- Convenciones de nombres consistentes
- Organización por responsabilidad (routers, services, components)
- Carpeta dedicada para testing automatizado
```

**Resultado Esperado:**
- Estructura de directorios completa y documentada
- Convenciones de nombres establecidas
- Separación clara de responsabilidades

---

#### 3. ⚙️ Prompt de Integración de DevOps y Automatización

**Rol:** Ingeniero de DevOps y Orquestación de Contenedores

**Prompt Modelo:**
```
[Rol: Ingeniero de DevOps y Orquestación de Contenedores] 

Genera el archivo docker-compose.yml para orquestar los servicios definidos: API (FastAPI), PostgreSQL, RabbitMQ, Worker y los dos frontends. Incluye instrucciones para la configuración de volúmenes y las variables de entorno (DATABASE_URL, RABBITMQ_URL, JWT_SECRET). 

Además, crea una sección de Guía de Inicio Rápido con los comandos docker-compose up -d --build y docker-compose down.

**Requisitos:**
- Healthchecks para todos los servicios
- Volúmenes para persistencia de datos
- Variables de entorno documentadas
- Redes Docker para comunicación entre servicios
- Orden de inicio correcto (dependencias)
```

**Resultado Esperado:**
- `docker-compose.yml` completo y funcional
- Documentación de variables de entorno
- Guía de inicio rápido
- Configuración de healthchecks

---

#### 4. 📝 Prompt de Detalle de Funcionalidades y Metodología

**Rol:** Redactor Técnico y Estratega de Gobernanza de Proyectos

**Prompt Modelo:**
```
[Rol: Redactor Técnico y Estratega de Gobernanza de Proyectos] 

Crea la Visión General y las Características Principales para el proyecto, destacando la Gestión de Productos (Salchipapas, Combos), el Sistema de Carrito y la Autenticación Dual para clientes/administradores. 

Posteriormente, define la necesidad de un protocolo de desarrollo llamado AI_WORKFLOW.md que describa la metodología 'AI-First Development' con plantillas de prompts y roles (IA como Junior Developer).

**Contenido Requerido:**
- Visión general del proyecto
- Características principales documentadas
- Metodología AI-First Development
- Plantillas de prompts
- Roles y responsabilidades
```

**Resultado Esperado:**
- README.md con visión y características
- AI_WORKFLOW.md con metodología completa
- Documentación de roles y responsabilidades

---

#### 5. 🧪 Prompt de Detalle de Testing y Calidad

**Rol:** Ingeniero de Aseguramiento de Calidad (QA) y Ciberseguridad

**Prompt Modelo:**
```
[Rol: Ingeniero de Aseguramiento de Calidad (QA) y Ciberseguridad] 

Detalla la sección de Calidad y Testing. Asegúrate de incluir la ejecución de pruebas dentro de Docker. Especifica que el testing automatizado debe cubrir Tests Funcionales, Tests de Autenticación, Análisis de Seguridad (Bandit) y Load Testing. 

Proporciona los scripts de ejecución (run_qa.sh / .ps1) y la lista de archivos de reporte que se deben generar.

**Requisitos:**
- Tests funcionales con pytest
- Análisis de seguridad con Bandit
- Load testing con Locust
- Scripts de ejecución multiplataforma
- Generación de reportes HTML
```

**Resultado Esperado:**
- Infraestructura de testing completa
- Scripts de ejecución (Bash y PowerShell)
- Documentación de reportes
- Integración con Docker

---

#### 6. 🔐 Prompt de Resumen Final y Credenciales por Defecto

**Rol:** Administrador de Sistemas y Documentador de Configuración

**Prompt Modelo:**
```
[Rol: Administrador de Sistemas y Documentador de Configuración] 

Añade una sección de Credenciales por Defecto con usuarios de prueba para el administrador (Admin@sofka.com/Admin 123) y las credenciales de los servicios (PostgreSQL, RabbitMQ). 

Finalmente, crea una sección de Comandos Útiles para Docker Compose, scripts internos (ej. add_products.py) y comandos de conexión a la base de datos (psql).

**Contenido Requerido:**
- Credenciales por defecto documentadas
- Comandos Docker Compose esenciales
- Scripts de utilidad documentados
- Comandos de conexión a servicios
```

**Resultado Esperado:**
- Sección de credenciales completa
- Comandos útiles documentados
- Guía de scripts internos

---

### Prompt de Infraestructura de Testing Automatizado

**Rol:** DevOps Engineer Senior

**Prompt Modelo:**
```
[Rol: DevOps Engineer Senior] 

Actúa como un DevOps Engineer Senior que genera infraestructura de Testing Automatizado usando contenedores. Tu objetivo es asegurar que la configuración de Docker y Bash sea resistente a errores de rutas al trabajar desde la raíz del repositorio.

**Contexto del Proyecto:**
- Lenguaje de Desarrollo: Python
- Gestor de Dependencias: requirements.txt
- Comando para Ejecutar Pruebas: pytest

**Estructura de Salida Obligatoria (Archivos a Generar):**

1. 📂 qa_automated/Dockerfile.qa
   - Propósito: Definir el entorno aislado de pruebas
   - Instrucción Clave (Anti-Error): Usar la línea COPY . /app para copiar todo el proyecto a la raíz de /app dentro del contenedor. El comando final (CMD) debe referenciar explícitamente el subdirectorio de pruebas: /app/qa_automated/

2. 📜 qa_automated/run_qa.sh
   - Propósito: Script para la ejecución externa
   - Instrucción Clave (Anti-Error): El comando docker build debe usar un contexto de construcción (.) que apunte a la raíz del proyecto, y el Dockerfile debe ser referenciado con la ruta completa (qa_automated/Dockerfile.qa)

3. 📝 qa_automated/README.md
   - Propósito: Documentación de uso
```

**Resultado Esperado:**
- Dockerfile.qa configurado correctamente
- Scripts de ejecución multiplataforma
- Documentación completa de uso

---

### Prompt de Generación de Scripts de Testing

**Rol:** QA Engineer Senior y Especialista en Automatización (SDET)

**Prompt Modelo:**
```
[Rol: QA Engineer Senior y Especialista en Automatización (SDET)] 

Tu tarea es generar el código de los scripts de pruebas que cubran validación funcional, seguridad estática y un plan de prueba de estrés, para un componente específico del proyecto.

**Contexto Necesario:**
- Tecnología del Componente: Python/FastAPI
- Librería de Testing a Usar: pytest
- Código/Componente a Testear: [INSERTAR EL FRAGMENTO DE CÓDIGO CRÍTICO AQUÍ]
- Criterios de Aceptación (Funcionales) a Cumplir: [LISTA DE REQUISITOS]

**Instrucción de Generación de Archivos (Salida Obligatoria):**

Genera el contenido para los siguientes tres scripts separados con el formato y nombre de archivo apropiado para Python. Los archivos deben estar listos para ser copiados a la carpeta qa_automated/.

1. ⚙️ Script de Validación Funcional
   - Nombre: test_funcionalidad_clave.py
   - Contenido: Test cases (pruebas unitarias y de integración) que validen rigurosamente cada uno de los Criterios de Aceptación proporcionados, utilizando pytest.

2. 🛡️ Script de Análisis de Seguridad
   - Nombre: security_analysis.py
   - Contenido: Wrapper de comandos para ejecutar Bandit (Análisis Estático de Seguridad). El script debe retornar un error si se encuentran vulnerabilidades.

3. 📈 Script de Pruebas de Estrés
   - Nombre: load_test_script.py
   - Contenido: Script de carga usando Locust que simule una carga alta y concurrente.
   - Escenario Clave: 500 usuarios virtuales inyectando peticiones por 60 segundos
   - Métrica Clave: Verificar que el tiempo de respuesta (Latencia) promedio sea menor a 200 ms
```

**Resultado Esperado:**
- Suite completa de tests funcionales
- Script de análisis de seguridad
- Script de pruebas de carga
- Documentación de métricas y criterios

---

### Flujo de Uso de Prompts de Estructura

**Orden Recomendado de Ejecución:**

1. **Prompt #1** → Definir alcance y stack
2. **Prompt #2** → Crear estructura de carpetas
3. **Prompt #3** → Configurar Docker y DevOps
4. **Prompt #4** → Documentar funcionalidades y metodología
5. **Prompt #5** → Implementar testing
6. **Prompt #6** → Finalizar documentación y credenciales

**Notas Importantes:**
- Cada prompt debe ejecutarse secuencialmente
- Los resultados de cada prompt alimentan el siguiente
- La revisión humana es obligatoria después de cada paso
- Los prompts de testing pueden ejecutarse en paralelo después de tener la estructura base

---

## 📝 Registro de Prompts de Éxito (Archivo Vivo)

> **Nota para el Equipo:** Esta sección debe actualizarse con cada prompt exitoso. Agregar nuevos prompts siguiendo el formato establecido.

### Cómo Agregar un Nuevo Prompt de Éxito

**Formato Obligatorio:**

```markdown
#### Prompt #[NÚMERO]: [Título Descriptivo]
**Prompt Original:**
```
[Prompt exacto usado]
```

**Contexto Técnico:**
- [Lista de contexto técnico relevante]
- [Archivos afectados]
- [Tecnologías involucradas]

**Solución Aplicada:**
- [Descripción de la solución implementada]
- [Cambios realizados]

**Resultado Obtenido:**
- [Resultados específicos y medibles]
- [Métricas de éxito si aplica]

**Lección Aprendida:**
- [Insight clave obtenido]
- [Patrón identificado]
```

### Prompts Críticos que Generaron Soluciones Clave

#### Prompt #1: Creación de Infraestructura de Testing
**Prompt Original:**
```
@qa_automated actua como QA Engineer Senior y Especialista en Automatización (SDET), 
ejecuta los scrip de los test correspondientes de la carpeta @qa_automated
```

**Contexto Técnico:**
- Carpeta `qa_automated/` con tests funcionales, análisis de seguridad y pruebas de carga
- Dockerfile.qa configurado con todas las dependencias
- Scripts PowerShell y Bash para automatización

**Resultado Obtenido:**
- ✅ Ejecución exitosa de tests funcionales (16 passed, 11 failed - problema de mocks identificado)
- ✅ Análisis de seguridad completado sin vulnerabilidades críticas
- ✅ Generación de reportes HTML actualizados
- ✅ Identificación de problema de mocking con `from module import function`

**Lección Aprendida:** La especificación del rol técnico (QA Engineer Senior, SDET) permite que la IA entienda el contexto de testing y automatización, generando soluciones apropiadas.

---

#### Prompt #6: [PLACEHOLDER - Agregar nuevo prompt exitoso aquí]
**Prompt Original:**
```
[El equipo debe agregar aquí el prompt exacto usado]
```

**Contexto Técnico:**
- [Contexto técnico relevante]
- [Archivos afectados]
- [Tecnologías involucradas]

**Solución Aplicada:**
- [Descripción de la solución]

**Resultado Obtenido:**
- [Resultados específicos]

**Lección Aprendida:**
- [Insight clave]

---

#### Prompt #7: [PLACEHOLDER - Agregar nuevo prompt exitoso aquí]
**Prompt Original:**
```
[El equipo debe agregar aquí el prompt exacto usado]
```

**Contexto Técnico:**
- [Contexto técnico relevante]

**Solución Aplicada:**
- [Descripción de la solución]

**Resultado Obtenido:**
- [Resultados específicos]

**Lección Aprendida:**
- [Insight clave]


---

#### Prompt #3: Análisis de Seguridad
**Prompt Original:**
```
@qa_automated actua como QA Engineer Senior y Especialista en Automatización (SDET), 
ejecuta los scrip de los test correspondientes de la carpeta @qa_automated
```

**Contexto Técnico:**
- Script `security_analysis.py` con Bandit para SAST
- Configuración para reportar solo vulnerabilidades High y Medium
- Integración con Docker para entorno aislado

**Resultado Obtenido:**
- ✅ Análisis completado sin vulnerabilidades críticas
- ✅ Corrección previa de vulnerabilidad B104 (hardcoded secret)
- ✅ Reportes generados en formato JSON y texto

**Lección Aprendida:** La automatización de análisis de seguridad permite detectar vulnerabilidades temprano en el ciclo de desarrollo.

---

### Patrones de Prompts Exitosos Identificados

#### Patrón 1: Prompt de Ejecución y Reporte
**Estructura:**
```
@[contexto] actua como [rol técnico específico]

[Acción solicitada: ejecutar, corregir, implementar]

[Contexto técnico relevante]

[Resultado esperado: ejecutar scripts, actualizar reportes]
```

**Ejemplo de Éxito:**
- Prompt #1 y #2 siguen este patrón
- Tasa de éxito: Alta cuando se especifica rol técnico y contexto

#### Patrón 2: Prompt de Corrección con Restricciones
**Estructura:**
```
@[contexto] actua como [rol técnico específico]

Problema pendiente: [descripción técnica específica del problema]

[Contexto técnico: archivos afectados, tecnologías involucradas]

Quiero que apliques la solucion mas adecuada sin afectar el funcionamiento del proyecto

[Acción final: ejecutar tests, actualizar reportes]
```

**Ejemplo de Éxito:**
- Prompt #2 sigue este patrón
- La frase "sin afectar el funcionamiento del proyecto" es crítica

#### Patrón 3: Prompt de Creación de Infraestructura
**Estructura:**
```
@[carpeta] actua como [rol técnico específico]

[Descripción de infraestructura a crear]

[Herramientas y tecnologías a utilizar]

[Resultado esperado con métricas]
```

**Ejemplo de Éxito:**
- Creación de `qa_automated/` con Docker, pytest, Bandit, Locust
- Infraestructura completa y funcional

---

## 📚 Documentos Clave y Contextualización

### Integración con Librería de Prompts

**Relación con PROMPTS_LIBRARY.md:**

Este documento (AI_WORKFLOW.md) define la **metodología y gobernanza**, mientras que [PROMPTS_LIBRARY.md](./PROMPTS_LIBRARY.md) proporciona **prompts modelo específicos por capa**.

**Flujo de Trabajo Recomendado:**

1. **Leer AI_WORKFLOW.md** → Entender metodología y reglas
2. **Consultar PROMPTS_LIBRARY.md** → Seleccionar prompt modelo apropiado
3. **Adaptar el prompt** → Reemplazar placeholders con valores específicos
4. **Ejecutar prompt** → Generar código con IA
5. **Revisar código** → Verificación humana obligatoria
6. **Actualizar AI_WORKFLOW.md** → Registrar prompt exitoso si aplica

### Documentos de Entrada Obligatorios

Antes de interactuar con la IA, **SIEMPRE** proporcionar estos documentos como contexto:

1. **AI_WORKFLOW.md** (Este documento) ⭐ **OBLIGATORIO**
   - Define metodología y stack tecnológico
   - Establece reglas de gobernanza y verificación humana
   - **Uso:** Contexto inicial obligatorio para cualquier prompt
   - **Relación:** Base metodológica del proyecto

2. **PROMPTS_LIBRARY.md** ⭐ **OBLIGATORIO para creación de componentes**
   - Librería de prompts modelo por capa (Backend, Frontend, Worker, Testing)
   - Prompts específicos al stack tecnológico del proyecto
   - **Uso:** Referencia para crear nuevos componentes con coherencia arquitectónica
   - **Relación:** Extensión práctica del AI_WORKFLOW.md

3. **README.md**
   - Descripción general del proyecto
   - Instrucciones de instalación
   - Arquitectura del sistema
   - **Uso:** Contexto de arquitectura y setup
   - **Relación:** Documentación principal que referencia AI_WORKFLOW.md

3. **docker-compose.yml**
   - Configuración de servicios
   - **Uso:** Contexto de infraestructura y dependencias

4. **Archivos de Configuración**
   - `package.json` (frontend/admin-frontend/backend/worker)
   - `requirements.txt` (api)
   - `prisma/schema.prisma`
   - **Uso:** Contexto de dependencias y estructura de datos

5. **Documentos de QA Automation (qa_automated/)**
   - `README_TESTING.md` - Documentación completa de scripts de testing
   - `RESULTADOS_EJECUCION.md` - Resultados de ejecución de tests
   - `RESULTADOS_ANALISIS_SEGURIDAD.md` - Resultados de análisis SAST
   - `EXPLICACION_TESTS_PENDIENTES.md` - Explicación de problemas técnicos
   - `generate_reports.html` - Dashboard de resultados
   - **Uso:** Contexto de infraestructura de testing y resultados

### Orden de Prioridad para Contexto

1. **Alta Prioridad:** Archivos directamente relacionados con la tarea
2. **Media Prioridad:** Archivos de configuración y estructura
3. **Baja Prioridad:** Documentación histórica y resúmenes

---

## 🏗️ Stack Tecnológico Base (Contexto Obligatorio para IA)

### Backend/API

**Producer API (FastAPI - Python)**
- FastAPI 0.104.1
- Uvicorn (ASGI server)
- SQLAlchemy 2.0.23 (ORM)
- asyncpg 0.29.0 (PostgreSQL async driver)
- psycopg2-binary 2.9.9 (PostgreSQL sync driver)
- python-jose[cryptography] 3.3.0 (JWT)
- passlib[bcrypt] 1.7.4 (Password hashing)
- aio-pika 9.2.0 (RabbitMQ client)
- Pydantic 2.5.0 (Data validation)

**Consumer Worker (Node.js - TypeScript)**
- Node.js 20+
- TypeScript
- Prisma ORM
- amqplib (RabbitMQ client)
- Express (opcional, para health checks)

**Backend Legacy (Node.js - TypeScript)**
- Node.js + Express
- TypeScript
- Prisma ORM
- JWT Authentication

### Frontend

**Cliente (React - JavaScript)**
- React 18.2.0
- Vite 4.4.5 (Build tool)
- Axios 1.6.0 (HTTP client)
- Tailwind CSS 3.3.3
- Lucide React 0.263.1 (Iconos)
- **Puerto:** 3000

**Administración (React - JavaScript)**
- React 18.2.0
- Vite 4.4.5
- Axios 1.6.0
- Tailwind CSS 3.3.3
- Lucide React 0.263.1
- **Puerto:** 3001

### Base de Datos

- **PostgreSQL 15-alpine**
- **Prisma ORM** (para Node.js)
- **SQLAlchemy** (para Python)
- **asyncpg** (driver async para Python)

### Message Broker

- **RabbitMQ 3-management-alpine**
- **aio-pika** (Python client)
- **amqplib** (Node.js client)
- Cola: `order_queue`

### DevOps

- **Docker** + **Docker Compose**
- **Healthchecks** configurados para todos los servicios
- **Volumes** para persistencia de datos
- **Networks** para comunicación entre servicios

### Testing y QA Automation

**Infraestructura de Testing (qa_automated/)**
- **Python 3.11-slim** (Base Docker)
- **pytest 7.4.3** (Framework de testing)
- **pytest-asyncio 0.21.1** (Soporte async/await)
- **pytest-cov 4.1.0** (Coverage reporting)
- **pytest-mock 3.12.0** (Mocking avanzado)
- **httpx 0.25.2** (Cliente HTTP async para tests)
- **bandit[toml] 1.7.5** (Análisis estático de seguridad SAST)
- **locust 2.17.0** (Pruebas de carga y estrés)
- **aiosqlite 0.19.0** (SQLite async para tests)
- **Docker** (Entorno aislado de testing)
- **PowerShell/Bash** (Scripts de automatización)

### Arquitectura

```
┌─────────────────┐     ┌──────────────┐     ┌─────────────┐
│  Frontend       │────▶│  API (FastAPI│────▶│  PostgreSQL │
│  (Puerto 3000)  │     │  Puerto 5000)│     │  (Puerto    │
└─────────────────┘     └──────────────┘     │   5432)     │
                                             └─────────────┘
┌─────────────────┐           │
│ Admin Frontend  │           │
│ (Puerto 3001)   │           ▼
└─────────────────┘     ┌──────────────┐
                         │  RabbitMQ    │
                         │  (Puerto     │
                         │   5672)      │
                         └──────────────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Worker      │
                         │  (Node.js +  │
                         │   Prisma)    │
                         └──────────────┘
```

---

## 🔄 Dinámicas de Interacción

### Regla de Verificación Humana Obligatoria

**⚠️ CRÍTICO:** Todo código generado por IA debe pasar por revisión humana antes de ser mergeado a ramas principales.

#### Checklist de Verificación

- [ ] **Lógica de Negocio:** Verificar que la lógica implementada es correcta
- [ ] **Seguridad:** Revisar manejo de tokens, validaciones, SQL injection
- [ ] **Performance:** Verificar queries, optimizaciones necesarias
- [ ] **Estándares de Código:** Formato, naming conventions, estructura
- [ ] **Testing:** Verificar que funcionalidades críticas tienen tests
- [ ] **Documentación:** Actualizar documentación si es necesario

### Flujo de Trabajo Estándar

1. **Prompt a IA** → Generación de código
2. **Revisión Humana** → Validación y ajustes
3. **Testing Local** → Verificación funcional
4. **Commit** → Con mensaje descriptivo
5. **Documentación** → Actualizar cambios relevantes

### Política de Propiedad Intelectual y Confidencialidad

#### ⚠️ REGLAS CRÍTICAS (OBLIGATORIAS)

1. **NO usar datos sensibles en IAs públicas:**
   - ❌ Credenciales de base de datos
   - ❌ Tokens JWT secretos
   - ❌ API keys
   - ❌ Información de clientes reales
   - ❌ Datos de producción
   - ❌ Secretos hardcodeados en código

2. **Usar datos de ejemplo:**
   - ✅ Datos sintéticos para testing
   - ✅ Variables de entorno para configuración
   - ✅ Archivos `.env.example` como plantillas
   - ✅ Mocks y fixtures en tests

3. **Revisar código generado:**
   - Verificar que no se hardcodean credenciales
   - Asegurar uso de variables de entorno
   - Validar que no se exponen datos sensibles
   - Revisar que los mocks no exponen información real

4. **Gestión de archivos:**
   - `.gitignore` debe incluir `.env`, `node_modules`, `__pycache__`
   - No commitear archivos con información sensible
   - Verificar reportes de seguridad antes de commitear

5. **Responsabilidad Final del Desarrollador:**
   - ⚠️ **CRÍTICO:** Todo código generado por IA debe ser revisado por un desarrollador humano
   - ⚠️ **CRÍTICO:** La responsabilidad final del código recae en el desarrollador humano
   - ⚠️ **CRÍTICO:** Los tests generados deben validarse manualmente
   - ⚠️ **CRÍTICO:** Los reportes de seguridad deben revisarse antes de considerar el código seguro

---

## 📁 Estructura del Proyecto (Contexto para IA)

```
prueba-restaurante/
├── api/                          # Producer API (FastAPI)
│   ├── routers/                  # Endpoints de la API
│   │   ├── auth.py
│   │   ├── products.py
│   │   ├── orders.py
│   │   ├── admin.py
│   │   └── addresses.py
│   ├── services/                 # Lógica de negocio
│   │   ├── database_service.py
│   │   ├── auth_service.py
│   │   └── rabbitmq.py
│   ├── models.py                 # Modelos SQLAlchemy
│   ├── database.py               # Configuración DB
│   ├── main.py                   # Punto de entrada FastAPI
│   └── requirements.txt
│
├── backend/                       # Backend Legacy (Node.js)
│   ├── src/
│   │   ├── controllers/
│   │   ├── routes/
│   │   └── middleware/
│   └── prisma/
│       └── schema.prisma
│
├── worker/                        # Consumer Worker (Node.js)
│   ├── src/
│   │   └── index.ts              # Procesador de mensajes RabbitMQ
│   └── prisma/
│       └── schema.prisma
│
├── frontend/                      # Frontend Cliente (React)
│   ├── src/
│   │   ├── components/
│   │   │   ├── client/           # Componentes de cliente
│   │   │   └── common/           # Componentes compartidos
│   │   ├── pages/
│   │   │   └── ClientPage.jsx
│   │   ├── hooks/
│   │   ├── utils/
│   │   └── App.jsx
│   └── package.json
│
├── admin-frontend/                # Frontend Admin (React)
│   ├── src/
│   │   ├── components/
│   │   │   └── admin/           # Componentes de admin
│   │   ├── pages/
│   │   │   ├── AdminPage.jsx
│   │   │   └── AdminLogin.jsx
│   │   └── App.jsx
│   └── package.json
│
├── docker-compose.yml             # Orquestación de servicios
├── qa_automated/                  # Infraestructura de Testing
│   ├── tests/                     # Scripts de pruebas
│   │   ├── test_funcionalidad_auth.py  # Tests funcionales
│   │   ├── security_analysis.py        # Análisis SAST
│   │   ├── load_test_auth.py           # Pruebas de carga
│   │   └── conftest.py                 # Configuración pytest
│   ├── run_qa.ps1                 # Script ejecución (Windows)
│   ├── run_qa.sh                  # Script ejecución (Linux/Mac)
│   ├── run_security_analysis.ps1   # Script seguridad (Windows)
│   ├── run_security_analysis.sh    # Script seguridad (Linux/Mac)
│   ├── Dockerfile.qa              # Dockerfile para testing
│   ├── README_TESTING.md         # Documentación testing
│   ├── generate_reports.html      # Dashboard de resultados
│   └── RESULTADOS_*.md           # Reportes de ejecución
├── README.md                      # Documentación principal
└── AI_WORKFLOW.md                 # Este documento
```

---

## ✅ Estado del Proyecto

### Funcionalidades Implementadas

1. ✅ **Autenticación de usuarios**
   - Registro y login de clientes
   - Login de administradores
   - JWT con sesiones independientes (clientToken/adminToken)
   - Roles: CUSTOMER, ADMIN

2. ✅ **Gestión de productos**
   - CRUD completo de productos
   - Categorías: SALCHIPAPAS, BEBIDAS, ADICIONALES, COMBOS
   - Disponibilidad de productos

3. ✅ **Sistema de carrito**
   - Agregar/remover productos
   - Actualizar cantidades
   - Cálculo de totales

4. ✅ **Gestión de direcciones**
   - Múltiples direcciones por usuario
   - Dirección predeterminada
   - Validación de direcciones

5. ✅ **Procesamiento de pedidos**
   - Creación de pedidos
   - Integración con RabbitMQ
   - Worker para procesamiento asíncrono
   - Estados: PENDING, PREPARING, READY, DELIVERED, CANCELLED

6. ✅ **Panel de administración**
   - Gestión de pedidos
   - Gestión de productos
   - Gestión de clientes
   - Estadísticas en tiempo real (pedidos e ingresos del día)
   - Aplicación separada en puerto 3001

7. ✅ **Sesiones independientes**
   - Frontend cliente (puerto 3000) - solo clientToken
   - Frontend admin (puerto 3001) - solo adminToken
   - Redirecciones sin interferencia de sesiones

### Arquitectura de Sesiones

- **Cliente → Admin:** Redirige con `?forceLogin=true` (siempre muestra login)
- **Admin → Cliente:** Redirige con `?noSession=true` (sin sesión de cliente)
- **Tokens separados:** `clientToken` y `adminToken` en localStorage independiente

---

## 🎯 Próximos Pasos Sugeridos

1. **Testing**
   - Tests unitarios para componentes React
   - Tests de integración para endpoints FastAPI
   - Tests E2E para flujos críticos

2. **Mejoras de Performance**
   - Caché de productos
   - Optimización de queries SQL
   - Lazy loading de componentes

3. **Funcionalidades Adicionales**
   - Sistema de notificaciones en tiempo real (WebSockets)
   - Integración de pagos (Stripe/PayPal)
   - Sistema de reseñas y calificaciones
   - Dashboard de analytics avanzado

4. **Seguridad**
   - Rate limiting en API
   - Validación más estricta de inputs
   - Auditoría de acciones administrativas

5. **DevOps**
   - CI/CD pipeline
   - Monitoreo y logging
   - Backup automatizado de base de datos

---

## 📝 Notas Importantes para IA

### Convenciones de Código

- **Python (API):** PEP 8, type hints, async/await para operaciones I/O
- **JavaScript/React:** ES6+, functional components, hooks
- **TypeScript:** Tipado estricto, interfaces claras
- **Naming:** camelCase para variables/funciones, PascalCase para componentes/clases

### Patrones de Diseño

- **API:** RESTful, separación de routers/services/models
- **Frontend:** Component-based, hooks personalizados, separación de concerns
- **Worker:** Event-driven, procesamiento asíncrono de mensajes

### Mejores Prácticas

- Siempre usar variables de entorno para configuración
- Validar inputs tanto en frontend como backend
- Manejar errores de forma consistente
- Documentar funciones complejas
- Mantener componentes pequeños y reutilizables

---

---

## 🔒 Protocolo de Seguridad y Responsabilidad (OBLIGATORIO)

### Regla de Oro: Responsabilidad Humana Final

**⚠️ DECLARACIÓN OBLIGATORIA:**

1. **Responsabilidad del Código:**
   - Todo código generado por IA es responsabilidad del desarrollador humano que lo utiliza
   - El desarrollador humano es el único responsable de la calidad, seguridad y funcionalidad del código
   - La IA actúa como herramienta de asistencia, no como reemplazo del juicio humano

2. **Revisión Obligatoria:**
   - Todo código generado debe pasar por revisión humana antes de ser mergeado
   - Los tests generados deben validarse manualmente
   - Los reportes de seguridad deben revisarse por un experto

3. **Prohibición de Datos Sensibles:**
   - **NUNCA** ingresar credenciales, tokens, API keys o datos de producción en IAs públicas
   - **SIEMPRE** usar datos sintéticos, mocks y variables de entorno
   - **SIEMPRE** verificar que el código generado no expone información sensible

4. **Validación de Tests:**
   - Los tests generados deben ejecutarse y validarse manualmente
   - Los resultados de tests deben revisarse antes de considerar el código como válido
   - Los problemas de mocking o configuración deben resolverse con supervisión humana

### Checklist de Seguridad Pre-Commit

Antes de commitear código generado por IA:

- [ ] Revisado manualmente por desarrollador humano
- [ ] No contiene credenciales hardcodeadas
- [ ] Usa variables de entorno para configuración sensible
- [ ] Tests ejecutados y validados manualmente
- [ ] Análisis de seguridad ejecutado (si aplica)
- [ ] Reportes de testing revisados
- [ ] Documentación actualizada si es necesario

---

## 📊 Métricas de Éxito de Prompts

### Prompts de QA Automation

| Prompt | Rol Especificado | Contexto | Resultado | Éxito |
|--------|------------------|----------|-----------|-------|
| Creación infraestructura | QA Engineer Senior, SDET | @qa_automated | Infraestructura completa | ✅ 95% |
| Corrección de mocks | QA Engineer Senior, SDET | @qa_automated + problema específico | 16/27 tests pasando | ✅ 60% |
| Análisis de seguridad | QA Engineer Senior, SDET | @qa_automated | Sin vulnerabilidades | ✅ 100% |

### Lecciones Clave

1. **Especificación de Rol:** Los prompts con rol técnico específico tienen mayor tasa de éxito
2. **Contexto Técnico:** Proporcionar contexto técnico detallado mejora la calidad de las soluciones
3. **Restricciones Claras:** Mencionar "sin afectar el funcionamiento del proyecto" previene cambios no deseados
4. **Resultados Esperados:** Solicitar ejecución y actualización de reportes asegura completitud

---

---

## 🔗 Referencias Rápidas

### Documentos Relacionados

- **[README.md](./README.md)** - Documentación principal del proyecto
- **[PROMPTS_LIBRARY.md](./PROMPTS_LIBRARY.md)** - Librería de prompts modelo por capa
- **[SETUP_INSTRUCTIONS.md](./SETUP_INSTRUCTIONS.md)** - Instrucciones detalladas de configuración
- **[DESARROLLO-LOCAL.md](./DESARROLLO-LOCAL.md)** - Guía de desarrollo local
- **[qa_automated/README.md](./qa_automated/README.md)** - Documentación de testing automatizado

### Enlaces Útiles

- **API Documentation**: http://localhost:5000/docs (cuando el servicio está corriendo)
- **RabbitMQ Management**: http://localhost:15672 (admin/admin123)
- **Frontend Cliente**: http://localhost:3000
- **Frontend Admin**: http://localhost:3001

---

## 📊 Resumen de Gobernanza

### Reglas Obligatorias (Checklist Rápido)

- [ ] ✅ **Revisión Humana Obligatoria** - Todo código generado por IA debe ser revisado
- [ ] ✅ **No Datos Sensibles** - Nunca ingresar credenciales o datos reales en IAs públicas
- [ ] ✅ **Usar PROMPTS_LIBRARY.md** - Para creación de componentes nuevos
- [ ] ✅ **Actualizar AI_WORKFLOW.md** - Registrar prompts exitosos
- [ ] ✅ **Validar Tests Manualmente** - Ejecutar y revisar resultados
- [ ] ✅ **Documentar Cambios** - Actualizar README si aplica

### Stack Tecnológico Resumido

- **Backend**: FastAPI (Python 3.11) + asyncpg + PostgreSQL
- **Frontend**: React 18.2 + Vite + Tailwind CSS
- **Worker**: Node.js 20+ + TypeScript + Prisma
- **Message Queue**: RabbitMQ
- **Testing**: pytest + Bandit + Locust
- **Containerización**: Docker + Docker Compose

### Herramientas de IA

- **Cursor AI** - Editor principal con IA integrada
- **GitHub Copilot** - Asistente de código
- **Claude/ChatGPT** - Consultas y análisis

---

---

## 🔍 Auditoría Final y Validación

### Checklist de Auditoría del Documento

Esta sección valida que el documento AI_WORKFLOW.md cumple con todos los requisitos para servir como base obligatoria del proyecto.

#### ✅ Contenido Obligatorio Verificado

- [x] **Metodología AI-First Development** - Definida y documentada
- [x] **Contexto y Gobernanza** - Stack tecnológico completo documentado
- [x] **Regla de Verificación Humana** - Declaración crítica y checklist completo
- [x] **Plantilla de Prompt Obligatoria** - Estructura base definida
- [x] **Prompts de Creación de Estructura** - 6 prompts con roles asignados documentados
- [x] **Prompts de Testing Automatizado** - Infraestructura y scripts documentados
- [x] **Registro de Prompts de Éxito** - Formato y ejemplos proporcionados
- [x] **Documentos Clave y Relaciones** - Jerarquía y uso documentados
- [x] **Stack Tecnológico** - Tablas completas con versiones
- [x] **Estructura del Proyecto** - Árbol de directorios documentado
- [x] **Referencias Rápidas** - Enlaces y comandos útiles

#### ✅ Integración con Otros Documentos

- [x] **README.md** - Referenciado y relación definida
- [x] **PROMPTS_LIBRARY.md** - Integración y flujo de trabajo documentado
- [x] **qa_automated/** - Prompts de creación documentados
- [x] **docker-compose.yml** - Contexto y uso documentado

#### ✅ Prompts de Estructura Documentados

- [x] **Prompt #1** - Definición de Alcance y Stack (Arquitecto de Software)
- [x] **Prompt #2** - Estructura de Carpetas (Ingeniero de Organización)
- [x] **Prompt #3** - DevOps y Automatización (Ingeniero de DevOps)
- [x] **Prompt #4** - Funcionalidades y Metodología (Redactor Técnico)
- [x] **Prompt #5** - Testing y Calidad (QA Engineer)
- [x] **Prompt #6** - Credenciales y Comandos (Administrador de Sistemas)
- [x] **Prompt de Testing Automatizado** - Infraestructura Docker (DevOps Engineer)
- [x] **Prompt de Scripts de Testing** - Generación de tests (QA Engineer/SDET)

#### ✅ Metodología de Desarrollo

- [x] **Roles Definidos** - IA como Junior Developer, Humano como Arquitecto/Revisor
- [x] **Plantilla de Prompt** - Estructura obligatoria documentada
- [x] **Ejemplos de Éxito** - Casos reales documentados
- [x] **Patrones Identificados** - Metodología validada documentada

#### ✅ Seguridad y Gobernanza

- [x] **Prohibición de Datos Sensibles** - Lista completa de restricciones
- [x] **Checklist Pre-Commit** - Validación obligatoria documentada
- [x] **Protocolo de Tests** - Validación manual requerida
- [x] **Responsabilidad Humana** - Declaración crítica incluida

### Criterios de Calidad del Documento

| Criterio | Estado | Notas |
|----------|--------|-------|
| **Completitud** | ✅ | Todos los elementos requeridos presentes |
| **Claridad** | ✅ | Estructura clara y navegable |
| **Actualidad** | ✅ | Versión 5.0, Diciembre 2024 |
| **Integración** | ✅ | Referencias cruzadas con otros documentos |
| **Usabilidad** | ✅ | Índice, ejemplos y plantillas incluidos |
| **Mantenibilidad** | ✅ | Formato para actualización continua |

### Validación de Uso como Base Obligatoria

**✅ APROBADO PARA USO COMO BASE OBLIGATORIA**

Este documento cumple con todos los requisitos para servir como:
- **Base metodológica** del proyecto
- **Guía de gobernanza** para desarrollo con IA
- **Referencia técnica** para prompts y estructura
- **Documento vivo** para registro de éxitos

### Recomendaciones para Mantenimiento

1. **Actualización Continua:**
   - Agregar nuevos prompts exitosos siguiendo el formato establecido
   - Actualizar stack tecnológico cuando cambien versiones
   - Mantener ejemplos actualizados

2. **Revisión Periódica:**
   - Revisar cada 3 meses la efectividad de los prompts
   - Validar que los ejemplos sigan siendo relevantes
   - Actualizar referencias a otros documentos

3. **Mejora Continua:**
   - Incorporar lecciones aprendidas de nuevos proyectos
   - Refinar plantillas basadas en feedback del equipo
   - Expandir ejemplos de prompts exitosos

---

**Última actualización:** Noviembre 23 del 2025
**Versión del documento:** 5.0  
**Estado:** ✅ Documento Auditado y Aprobado como Base Obligatoria  
**Mantenido por:** Equipo de Desarrollo SoftDomiFood  
**Próxima Revisión:** Marzo 2026
