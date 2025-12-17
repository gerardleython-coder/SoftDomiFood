# 🍟 SoftDomiFood - Sistema de Pedidos de Domicilio

Sistema completo de gestión de pedidos online para restaurantes con arquitectura de microservicios.

## 🚀 Inicio Rápido

```bash
cd SoftDomiFood
docker-compose up -d
```

**Accesos:**
- 🌐 Cliente: http://localhost:3000
- 👨‍💼 Admin: http://localhost:3001
- 📊 API Docs: http://localhost:5000/docs

## 📚 Documentación

Toda la documentación del proyecto está organizada en [`SoftDomiFood/docs/`](SoftDomiFood/docs/README.md):

- **[🏗️ Arquitectura](SoftDomiFood/docs/architecture/)** - Diseño del sistema y contexto de negocio
- **[⚙️ Setup](SoftDomiFood/docs/setup/)** - Guías de instalación y configuración
- **[🐛 Fixes](SoftDomiFood/docs/fixes/)** - Historial de correcciones
- **[🧪 Testing](SoftDomiFood/docs/testing/)** - Pruebas y auditorías

### Documentación Principal
- 📖 [README Completo del Proyecto](SoftDomiFood/README.md)
- 🔧 [Guía de Desarrollo Local](SoftDomiFood/docs/setup/DESARROLLO-LOCAL.md)
- 🐳 [Iniciar con Podman](SoftDomiFood/docs/setup/INICIAR_EN_PODMAN.md)

## 🏛️ Estructura del Proyecto

```
SoftDomiFood/
├── api/              # Backend FastAPI (Producer)
├── worker/           # Worker Node.js (Consumer)
├── frontend/         # App Cliente (React)
├── admin-frontend/   # Panel Admin (React)
├── database/         # Migraciones SQL
├── qa_automated/     # Tests Automatizados
├── scripts/          # Scripts Utilidad
└── docs/            # 📚 Documentación Completa
```

## 🛠️ Stack Tecnológico

- **Backend**: FastAPI (Python) + PostgreSQL
- **Worker**: Node.js + Prisma
- **Frontend**: React + Vite + TailwindCSS
- **Message Broker**: RabbitMQ
- **Testing**: Pytest + Playwright

## 🔑 Credenciales por Defecto

**Admin:**
- Email: `admin@softdomifood.com`
- Password: `admin123`

**Cliente de Prueba:**
- Email: `cliente@test.com`
- Password: `password123`

## 📦 Requisitos

- Docker & Docker Compose
- Node.js 18+ (para desarrollo local)
- Python 3.11+ (para desarrollo local)

---

**📘 Para información detallada, consulta la [documentación completa](SoftDomiFood/docs/README.md)**
