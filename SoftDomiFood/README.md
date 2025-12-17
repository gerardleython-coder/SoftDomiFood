# 🍟 Sistema de Pedidos de Domicilio - SoftDomiFood

> **Plataforma completa de gestión de pedidos online para restaurantes**
> *Delivering Excellence, One Order at a Time*

**Estado del Proyecto:** 🟢 **En Desarrollo Activo - Fase Beta**

---

## 📋 Tabla de Contenidos

- [Visión General](#-visión-general)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Stack Tecnológico](#-stack-tecnológico)
- [Guía de Inicio Rápido](#-guía-de-inicio-rápido)
- [Calidad y Testing](#-calidad-y-testing)
- [Documentos Clave y Gobernanza](#-documentos-clave-y-gobernanza)
- [Configuración Avanzada](#-configuración-avanzada)
- [Credenciales por Defecto](#-credenciales-por-defecto)
- [Comandos Útiles](#-comandos-útiles)

---

## 🌟 Visión General

**SoftDomiFood** es un sistema completo de gestión de pedidos de domicilio diseñado para restaurantes, con enfoque especial en el negocio de salchipapas. El sistema proporciona una experiencia de usuario fluida tanto para clientes como para administradores, con arquitectura moderna basada en microservicios y procesamiento asíncrono de pedidos.

### Características Principales

- ✅ **Gestión de Productos**: Catálogo completo con categorías (Salchipapas, Bebidas, Adicionales, Combos)
- ✅ **Sistema de Carrito**: Carrito de compras con dropdown interactivo en el header
- ✅ **Autenticación Dual**: Sesiones independientes para clientes y administradores
- ✅ **Procesamiento de Pedidos**: Sistema asíncrono con RabbitMQ para procesamiento de pedidos
- ✅ **Gestión de Direcciones**: Múltiples direcciones de entrega por usuario
- ✅ **Panel Administrativo**: Dashboard completo con estadísticas en tiempo real
- ✅ **Historial de Pedidos**: Seguimiento completo del estado de pedidos
- ✅ **Testing Automatizado**: Suite completa de pruebas QA automatizadas

---

## 🏗️ Estructura del Proyecto

```
prueba-restaurante--Develop-JE/
│
├── 📁 api/                          # API Backend (FastAPI)
│   ├── routers/                     # Endpoints de la API
│   │   ├── auth.py                  # Autenticación y autorización
│   │   ├── products.py              # Gestión de productos
│   │   ├── orders.py                # Gestión de pedidos
│   │   ├── addresses.py             # Gestión de direcciones
│   │   ├── payments.py              # Procesamiento de pagos
│   │   └── admin.py                 # Endpoints administrativos
│   ├── services/                    # Lógica de negocio
│   │   ├── database_service.py      # Servicios de base de datos
│   │   ├── auth_service.py          # Servicios de autenticación
│   │   └── rabbitmq.py              # Integración con RabbitMQ
│   ├── models.py                    # Modelos de datos
│   ├── database.py                  # Configuración de BD
│   ├── init_db.py                   # Inicialización de BD
│   ├── main.py                      # Punto de entrada FastAPI
│   ├── requirements.txt             # Dependencias Python
│   ├── add_products.py              # Script para agregar productos
│   └── Dockerfile                   # Imagen Docker para API
│
├── 📁 frontend/                     # Frontend Cliente (React + Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── client/              # Componentes del cliente
│   │   │   │   ├── ClientLayout.jsx
│   │   │   │   ├── ProductCard.jsx
│   │   │   │   ├── Cart.jsx
│   │   │   │   ├── OrderForm.jsx
│   │   │   │   └── MyOrders.jsx
│   │   │   └── common/              # Componentes compartidos
│   │   ├── pages/
│   │   │   └── ClientPage.jsx       # Página principal del cliente
│   │   ├── hooks/                   # Custom hooks
│   │   ├── utils/                   # Utilidades
│   │   │   └── api.js               # Cliente API
│   │   └── App.jsx                  # Componente raíz
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── 📁 admin-frontend/               # Frontend Administrativo (React + Vite)
│   ├── src/
│   │   ├── components/
│   │   │   ├── admin/               # Componentes administrativos
│   │   │   │   ├── AdminLayout.jsx
│   │   │   │   ├── OrderManagement.jsx
│   │   │   │   ├── ProductManagement.jsx
│   │   │   │   ├── CustomerManagement.jsx
│   │   │   │   └── StatsCard.jsx
│   │   │   └── common/
│   │   ├── pages/
│   │   │   ├── AdminPage.jsx
│   │   │   └── AdminLogin.jsx
│   │   └── utils/
│   ├── package.json
│   └── Dockerfile
│
├── 📁 worker/                       # Worker Consumer (Node.js + TypeScript)
│   ├── src/
│   │   └── index.ts                 # Procesador de mensajes RabbitMQ
│   ├── prisma/
│   │   ├── schema.prisma            # Schema de Prisma
│   │   └── seed.ts                  # Datos de prueba
│   ├── package.json
│   └── Dockerfile
│
├── 📁 scripts/                      # Scripts utilitarios
│   ├── README.md                    # Documentación de scripts
│   ├── utils/                       # Scripts de verificación
│   │   ├── check_admin.py           # Verificar usuario admin
│   │   ├── check_columns.py         # Verificar columnas BD
│   │   └── check_coupons_table.py   # Verificar tabla cupones
│   ├── database/                    # Scripts BD (preparado para futuro)
│   ├── verify_addresses_table.py    # Verificar tabla addresses
│   ├── force_create_tables.py       # Forzar creación de tablas
│   └── ops/                         # Orquestación y mantenimiento
│       ├── initialize-database.ps1  # Inicializar BD
│       ├── backup-database.ps1      # Backup BD
│       └── restore-database.ps1     # Restaurar BD
│
├── 📁 qa_automated/                 # Testing Automatizado
│   ├── tests/                       # Tests automatizados
│   │   ├── conftest.py              # Configuración de pytest
│   │   ├── test_funcionalidad_auth.py
│   │   ├── security_analysis.py
│   │   ├── load_test_auth.py
│   │   └── example_test.py
│   ├── Dockerfile.qa                # Imagen Docker para testing
│   ├── run_qa.sh                    # Script de ejecución (Linux/Mac)
│   ├── run_qa.ps1                   # Script de ejecución (Windows)
│   ├── generate_reports.html        # Reportes de testing
│   └── README.md                    # Documentación de testing
│
├── 📄 docker-compose.yml            # Orquestación de servicios
├── 📄 AI_WORKFLOW.md                # Metodología de desarrollo con IA
├── 📄 SoftDomiFood/DESARROLLO-LOCAL.md  # Guía de desarrollo local
├── 📄 SETUP_INSTRUCTIONS.md         # Instrucciones de configuración
└── 📄 README.md                     # Este archivo
```

---

## 🛠️ Stack Tecnológico

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11 | Lenguaje principal del backend |
| **FastAPI** | 0.104.1 | Framework web asíncrono |
| **Uvicorn** | 0.24.0 | Servidor ASGI |
| **PostgreSQL** | 15-alpine | Base de datos relacional |
| **asyncpg** | 0.29.0 | Driver asíncrono para PostgreSQL |
| **SQLAlchemy** | 2.0.23 | ORM (opcional) |
| **Pydantic** | 2.5.0 | Validación de datos |
| **python-jose** | 3.3.0 | JWT tokens |
| **passlib** | 1.7.4 | Hashing de contraseñas |
| **aio-pika** | 9.2.0 | Cliente RabbitMQ asíncrono |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.2.0 | Biblioteca UI |
| **Vite** | 4.4.5 | Build tool y dev server |
| **TypeScript** | 5.3.3 | Tipado estático (worker) |
| **Tailwind CSS** | 3.3.3 | Framework CSS utility-first |
| **Axios** | 1.6.0 | Cliente HTTP |
| **Lucide React** | 0.263.1 | Iconos |

### Worker & Message Queue

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Node.js** | 20+ | Runtime para worker |
| **TypeScript** | 5.3.3 | Lenguaje del worker |
| **Prisma** | 5.7.1 | ORM para Node.js |
| **amqplib** | 0.10.3 | Cliente RabbitMQ |
| **RabbitMQ** | 3-management-alpine | Message broker |

### DevOps & Testing

| Tecnología | Propósito |
|------------|-----------|
| **Docker** | Containerización |
| **Docker Compose** | Orquestación de servicios |
| **pytest** | Framework de testing Python |
| **pytest-asyncio** | Testing asíncrono |
| **httpx** | Cliente HTTP para testing |

---

## 🚀 Guía de Inicio Rápido

### Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Docker Desktop** (versión 20.10 o superior)
- **Docker Compose** (incluido en Docker Desktop)
- **Git** (para clonar el repositorio)

> **Nota:** El proyecto está completamente containerizado, por lo que no necesitas instalar Python, Node.js u otras dependencias localmente.

### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd prueba-restaurante--Develop-JE/prueba-restaurante--Develop-JE
   ```

2. **Verificar Docker**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Iniciar los servicios**
   ```bash
   docker-compose up -d --build
   ```

   Este comando:
   - Construye las imágenes Docker necesarias
   - Inicia todos los servicios en modo detached
   - Configura la red interna entre servicios
   - Inicializa la base de datos automáticamente

### Ejecución

Una vez iniciados los servicios, el sistema estará disponible en:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| **Frontend Cliente** | http://localhost:3000 | Interfaz para clientes |
| **Frontend Admin** | http://localhost:3001 | Panel de administración |
| **API** | http://localhost:5000 | API REST |
| **API Docs** | http://localhost:5000/docs | Documentación interactiva (Swagger) |
| **RabbitMQ Management** | http://localhost:15672 | Interfaz de gestión RabbitMQ |

### Verificación del Estado

Para verificar que todos los servicios están corriendo:

```bash
docker-compose ps
```

Deberías ver todos los servicios con estado `Up` y `healthy` (para postgres y rabbitmq).

### Detener los Servicios

```bash
docker-compose down
```

Para detener y eliminar los contenedores:

```bash
docker-compose down -v  # También elimina los volúmenes
```

---

## 🧪 Calidad y Testing

### Testing Automatizado

El proyecto incluye una suite completa de pruebas automatizadas ejecutadas en contenedores Docker aislados.

#### Ejecutar Tests (Linux/Mac/WSL)

```bash
# Dar permisos de ejecución (solo primera vez)
chmod +x qa_automated/run_qa.sh

# Ejecutar todas las pruebas
./qa_automated/run_qa.sh
```

#### Ejecutar Tests (Windows PowerShell)

```powershell
# Ejecutar todas las pruebas
.\qa_automated\run_qa.ps1
```

#### Ejecutar Tests (Windows Git Bash/WSL)

```bash
bash qa_automated/run_qa.sh
```

### Opciones de Testing

```bash
# Ejecutar pruebas específicas
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py

# Ejecutar con más verbosidad
./qa_automated/run_qa.sh -v -s

# Ejecutar con reporte de coverage
./qa_automated/run_qa.sh --cov=/app/api --cov-report=html

# Ejecutar análisis de seguridad
./qa_automated/run_security_analysis.sh
```

### Tipos de Tests Incluidos

- ✅ **Tests Funcionales**: Validación de endpoints y flujos de negocio
- ✅ **Tests de Autenticación**: Validación de JWT y permisos
- ✅ **Análisis de Seguridad**: Detección de vulnerabilidades (Bandit)
- ✅ **Load Testing**: Pruebas de carga y rendimiento
- ✅ **Coverage Reports**: Reportes de cobertura de código

### Ver Reportes

Los reportes de testing se generan automáticamente y están disponibles en:

- **HTML Reports**: `qa_automated/generate_reports.html`
- **Security Reports**: `qa_automated/RESULTADOS_ANALISIS_SEGURIDAD.md`
- **Execution Results**: `qa_automated/RESULTADOS_EJECUCION.md`

Para más información sobre testing, consulta: [qa_automated/README.md](./qa_automated/README.md)

---

## 📖 Documentos Clave y Gobernanza

### Gobernanza y Protocolos

Este proyecto sigue metodologías específicas y protocolos establecidos para garantizar calidad y consistencia.

#### 🤖 AI Workflow - Metodología de Desarrollo con IA

**Documento Obligatorio:** [AI_WORKFLOW.md](./AI_WORKFLOW.md)

Este documento define la metodología **"AI-First Development"** utilizada en el proyecto:

- **Estrategia de Interacción**: La IA actúa como Junior Developer, el equipo humano como Arquitectos y Revisores
- **Plantilla de Prompts**: Estructura estándar para comunicarse con herramientas de IA
- **Ejemplos de Prompts Exitosos**: Casos de uso reales y resultados
- **Herramientas de IA Utilizadas**: Cursor AI, GitHub Copilot, y más
- **Protocolos de Testing con IA**: Cómo usar IA para generar y validar tests

> ⚠️ **Importante**: Todos los desarrolladores deben leer y seguir las directrices del AI_WORKFLOW.md antes de contribuir al proyecto.

#### 📚 Documentación Adicional

| Documento | Descripción |
|-----------|-------------|
| [DESARROLLO-LOCAL.md](./SoftDomiFood/DESARROLLO-LOCAL.md) | Guía para desarrollo local |
| [qa_automated/README.md](./qa_automated/README.md) | Documentación completa de testing |


### Contribución

Para contribuir al proyecto:

1. **Leer el AI_WORKFLOW.md** para entender la metodología
2. **Revisar la estructura del proyecto** en este README
3. **Ejecutar los tests** antes de hacer commit
4. **Seguir las convenciones de código** establecidas
5. **Documentar cambios significativos**

---

## ⚙️ Configuración Avanzada

### Variables de Entorno

El proyecto utiliza variables de entorno para configuración. Los valores por defecto están en `docker-compose.yml`:

#### API (FastAPI)
```env
DATABASE_URL=postgresql://salchipapas_user:salchipapas_pass@postgres:5432/salchipapas_db
RABBITMQ_URL=amqp://admin:admin123@rabbitmq:5672/
JWT_SECRET=your-super-secret-jwt-key-change-in-production
JWT_EXPIRES_IN=7d
PORT=5000
CORS_ORIGIN=http://localhost:3000,http://localhost:3001
```

#### Base de Datos
```env
POSTGRES_USER=salchipapas_user
POSTGRES_PASSWORD=salchipapas_pass
POSTGRES_DB=salchipapas_db
```

#### RabbitMQ
```env
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin123
```

> ⚠️ **Seguridad**: Cambia todas las credenciales por defecto en producción.

### Desarrollo Local (Sin Docker)

Para desarrollo local, consulta: [DESARROLLO-LOCAL.md](./DESARROLLO-LOCAL.md)

### Agregar Productos

Para agregar productos con imágenes al sistema:

```bash
docker exec salchipapas-api python add_products.py
```

Este script agrega 24+ productos predefinidos con imágenes de ejemplo.

---

## 🔐 Credenciales por Defecto

### Panel de Administración

| Campo | Valor |
|-------|-------|
| **Email** | `Admin@sofka.com` |
| **Contraseña** | `Admin 123` |

> **Nota**: La contraseña incluye un espacio entre "Admin" y "123".

### RabbitMQ Management

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin` |
| **Contraseña** | `admin123` |
| **URL** | http://localhost:15672 |

### Base de Datos

| Campo | Valor |
|-------|-------|
| **Host** | `localhost` |
| **Puerto** | `5432` |
| **Usuario** | `salchipapas_user` |
| **Contraseña** | `salchipapas_pass` |
| **Base de Datos** | `salchipapas_db` |

---

## 🛠️ Comandos Útiles

### Docker Compose

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f [nombre-servicio]

# Reiniciar un servicio
docker-compose restart [nombre-servicio]

# Reconstruir imágenes
docker-compose up -d --build

# Ver estado de servicios
docker-compose ps
```

### Desarrollo

```bash
# Ejecutar script de productos
docker exec salchipapas-api python add_products.py

# Acceder a la consola de la API
docker exec -it salchipapas-api bash

# Ver logs de la API
docker logs -f salchipapas-api

# Ver logs del frontend
docker logs -f salchipapas-frontend
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker exec -it salchipapas-db psql -U salchipapas_user -d salchipapas_db

# Backup de base de datos
docker exec salchipapas-db pg_dump -U salchipapas_user salchipapas_db > backup.sql

# Restaurar base de datos
docker exec -i salchipapas-db psql -U salchipapas_user salchipapas_db < backup.sql
```

### Testing

```bash
# Ejecutar todos los tests
./qa_automated/run_qa.sh

# Ejecutar tests específicos
./qa_automated/run_qa.sh tests/test_funcionalidad_auth.py

# Análisis de seguridad
./qa_automated/run_security_analysis.sh
```

---

## 📊 Arquitectura del Sistema

### Diagrama de Servicios

```
┌─────────────────┐
│   Frontend      │  http://localhost:3000
│   (Cliente)     │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐      ┌──────────────┐
│   API (FastAPI) │──────│  PostgreSQL  │
│  :5000          │      │  :5432       │
└────────┬────────┘      └──────────────┘
         │
         │ AMQP
         │
┌────────▼────────┐      ┌──────────────┐
│   RabbitMQ      │      │   Worker     │
│  :5672, :15672  │◄─────│  (Consumer)  │
└─────────────────┘      └──────────────┘
         │
         │
┌────────▼────────┐
│ Admin Frontend  │  http://localhost:3001
│   (Admin)       │
└─────────────────┘
```

### Flujo de Pedidos

1. **Cliente** realiza pedido desde Frontend
2. **API** recibe pedido y lo guarda en PostgreSQL
3. **API** publica mensaje en RabbitMQ
4. **Worker** consume mensaje y procesa pedido
5. **Worker** actualiza estado en base de datos
6. **Admin** puede ver y gestionar pedidos en tiempo real

---

## 🐛 Troubleshooting

### Problemas Comunes

#### Los servicios no inician

```bash
# Verificar logs
docker-compose logs

# Verificar que Docker Desktop esté corriendo
docker ps
```

#### Error de conexión a la base de datos

```bash
# Verificar que PostgreSQL esté healthy
docker-compose ps postgres

# Reiniciar PostgreSQL
docker-compose restart postgres
```

#### El frontend no se conecta a la API

- Verificar que `VITE_API_URL` esté configurado correctamente
- Verificar que la API esté corriendo: http://localhost:5000/docs
- Revisar CORS en la configuración de la API

#### Tests fallan

```bash
# Reconstruir imagen de testing
docker build -f qa_automated/Dockerfile.qa -t qa-test .

# Ejecutar tests con más verbosidad
./qa_automated/run_qa.sh -v -s
```

---

## 📝 Licencia

[Especificar licencia del proyecto]

---

## 👥 Equipo

[Información del equipo de desarrollo]

---

## 📞 Soporte

Para soporte o preguntas:

- **Issues**: [Crear un issue en el repositorio]
- **Documentación**: Consultar los documentos en la carpeta raíz
- **AI Workflow**: Ver [AI_WORKFLOW.md](./AI_WORKFLOW.md) para metodología de desarrollo

---

**Última actualización:** Noviembre 23 del 2025
**Versión:** 1.0.0-beta

---

<div align="center">

**Desarrollado con ❤️ usando metodología AI-First Development**

[⬆ Volver arriba](#-sistema-de-pedidos-de-domicilio---softdomifood)

</div>
