# Desarrollo Local (Windows PowerShell)

Esta guía resume los pasos exactos para levantar en local los 4 proyectos principales del monorepo: `api` (FastAPI), `frontend` (cliente), `admin-frontend` (administrador) y `worker` (Node.js/TypeScript). Incluye la configuración requerida de PostgreSQL y RabbitMQ.

Requisitos previos:
- Windows con PowerShell 5.1 (shell por defecto)
- Python 3.11+ (para `api`)
- Node.js 20+ (para `frontend`, `admin-frontend` y `worker`)
- PostgreSQL instalado y corriendo localmente
- RabbitMQ corriendo localmente (management opcional)

Rutas del workspace (ejemplos generales):
- `\SoftDomiFood\api`
- `\SoftDomiFood\frontend`
- `\SoftDomiFood\admin-frontend`
- `\SoftDomiFood\worker`
- Scripts: `\SoftDomiFood\scripts\...` y `\SoftDomiFood\scripts\ops\...`

---

## 1) Base de Datos PostgreSQL

Crear base y usuario locales (ajusta si ya existen):

```powershell
# Abrir psql con tu instalación local
# Ajusta usuario/contraseña si usas otros
psql -U postgres -h localhost -p 5432

-- En la consola psql:
CREATE USER softdomifood_user WITH PASSWORD 'softdomifood_pass';
CREATE DATABASE softdomifood_db OWNER softdomifood_user;
GRANT ALL PRIVILEGES ON DATABASE softdomifood_db TO softdomifood_user;
```

Verifica que PostgreSQL esté accesible en `localhost:5432`.

---

## 2) RabbitMQ

Instala y enciende RabbitMQ localmente. Credenciales recomendadas (management opcional):
- URL de conexión: `amqp://admin:admin123@localhost:5672/`
- Management UI: `http://localhost:15672` (usuario: `admin`, contraseña: `admin123`)

Asegúrate de que el servicio esté arriba antes de iniciar `api` y `worker`.

---

## 3) API (FastAPI)

Ruta: `\SoftDomiFood\api`

```powershell
# Desde la carpeta api
cd "\SoftDomiFood\api"

# Crear y activar entorno virtual
python -m venv venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt

# Config variables de entorno (para esta sesión)
$env:DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"
$env:RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
$env:JWT_SECRET = "your-super-secret-jwt-key-change-in-production"
$env:CORS_ORIGIN = "http://localhost:3000,http://localhost:3001"

# Inicializar tablas si fuera necesario (el app lo verifica al arrancar)
# Opcional: ejecutar seeding de datos de prueba
python seed_data.py

# Iniciar servidor (modo desarrollo con reload)
python -m uvicorn main:app --reload --host 127.0.0.1 --port 5000
```

Notas:
- Si usas inputs `datetime-local` en frontends, asegúrate que la API convierta cadenas a `datetime` al crear/actualizar cupones.
- Documentación interactiva: `http://localhost:5000/docs`.

---

## 4) Frontend Cliente (React + Vite)

Ruta: `\SoftDomiFood\frontend`

```powershell
cd "\SoftDomiFood\frontend"

# Instalar dependencias
npm install

# Configurar URL de la API (Vite)
# Crea .env si no existe
"VITE_API_URL=http://localhost:5000/api" | Out-File -FilePath .env -Encoding UTF8

# Iniciar en modo desarrollo
npm run dev
# Acceder: http://localhost:3000
```

---

## 5) Frontend Admin (React + Vite)

Ruta: `\SoftDomiFood\admin-frontend`

```powershell
cd "\SoftDomiFood\admin-frontend"

# Instalar dependencias
npm install

# Configurar URL de la API (Vite)
"VITE_API_URL=http://localhost:5000/api" | Out-File -FilePath .env -Encoding UTF8

# Iniciar en modo desarrollo
npm run dev
# Acceder: http://localhost:3001
```

---

## 6) Worker (Node.js + TypeScript)

Ruta: `\SoftDomiFood\worker`

```powershell
cd "\SoftDomiFood\worker"

# Instalar dependencias
npm install

# Variables de entorno (si el worker las requiere)
$env:RABBITMQ_URL = "amqp://admin:admin123@localhost:5672/"
$env:DATABASE_URL = "postgresql://softdomifood_user:softdomifood_pass@localhost:5432/softdomifood_db"

# Compilar (si aplica) e iniciar
npm run build; npm run start
```

---

## Orden recomendado de arranque

1. PostgreSQL (DB)
2. RabbitMQ
3. API (FastAPI)
4. Frontend Cliente (Vite)
5. Frontend Admin (Vite)
6. Worker (Node.js)

---

## Verificación rápida

- API en `http://localhost:5000` y `http://localhost:5000/docs`
- Cliente en `http://localhost:3000`
- Admin en `http://localhost:3001`
- RabbitMQ Management en `http://localhost:15672` (opcional)

---

## Tips y solución de problemas

- Si la API muestra errores de tipo para fechas (strings), revisa el parsing en los endpoints admin de cupones.
- CORS: asegúrate que `CORS_ORIGIN` incluya ambos frontends.
- Si Vite no arranca, revisa que el puerto no esté ocupado y que `.env` tenga la variable `VITE_API_URL` correcta.
- Si el worker no consume, valida que RabbitMQ esté arrancado y que la cola `order_queue` exista (la API la declara al iniciar).
- Scripts útiles:
	- Verificar tabla addresses: `\SoftDomiFood\scripts\verify_addresses_table.py`
	- Forzar creación de tablas: `\SoftDomiFood\scripts\force_create_tables.py`
	- Ops Docker/Podman: `\SoftDomiFood\scripts\ops\start-local.ps1`, `stop-local.ps1`, `clean-docker.ps1`, `start-podman.ps1`, `stop-podman.ps1`, `clean-podman.ps1`
