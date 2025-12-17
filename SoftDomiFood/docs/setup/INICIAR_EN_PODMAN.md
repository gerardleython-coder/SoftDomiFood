# Pasos para ejecutar SoftDomiFood con Podman

## Comandos a ejecutar paso a paso

Copia y pega estos comandos en PowerShell uno por uno:

### 1. Crear red
```powershell
podman network rm softdomifood-network 2>$null
podman network create softdomifood-network
```

### 2. Crear volúmenes
```powershell
podman volume create softdomifood_postgres_data
podman volume create softdomifood_rabbitmq_data
```

### 3. Iniciar PostgreSQL
```powershell
podman run -d --name softdomifood-db --network softdomifood-network -e POSTGRES_USER=softdomifood_user -e POSTGRES_PASSWORD=softdomifood_pass -e POSTGRES_DB=softdomifood_db -p 5432:5432 -v softdomifood_postgres_data:/var/lib/postgresql/data postgres:15-alpine
```

### 4. Iniciar RabbitMQ
```powershell
podman run -d --name softdomifood-rabbitmq --network softdomifood-network -e RABBITMQ_DEFAULT_USER=admin -e RABBITMQ_DEFAULT_PASS=admin123 -p 5672:5672 -p 15672:15672 -v softdomifood_rabbitmq_data:/var/lib/rabbitmq rabbitmq:3-management-alpine
```

### 5. Esperar a que los servicios estén listos
```powershell
Start-Sleep -Seconds 15
```

### 6. Construir e iniciar API
```powershell
cd C:\Users\rutadelacarpeta..\SoftDomiFood
podman build -t softdomifood-api ./api
podman run -d --name softdomifood-api --network softdomifood-network -e DATABASE_URL=postgresql://softdomifood_user:softdomifood_pass@softdomifood-db:5432/softdomifood_db -e RABBITMQ_URL=amqp://admin:admin123@softdomifood-rabbitmq:5672/ -e JWT_SECRET=your-super-secret-jwt-key-change-in-production -e JWT_EXPIRES_IN=7d -e PORT=5000 -e "CORS_ORIGIN=http://localhost:3000,http://localhost:3001" -p 5000:5000 -v ${PWD}/api:/app:z softdomifood-api
```

### 7. Construir e iniciar Worker
```powershell
podman build -t softdomifood-worker ./worker
podman run -d --name softdomifood-worker --network softdomifood-network -e DATABASE_URL=postgresql://softdomifood_user:softdomifood_pass@softdomifood-db:5432/softdomifood_db -e RABBITMQ_URL=amqp://admin:admin123@softdomifood-rabbitmq:5672/ -v ${PWD}/worker:/app:z softdomifood-worker
```

### 8. Construir e iniciar Frontend Cliente
```powershell
podman build -t softdomifood-frontend ./frontend
podman run -d --name softdomifood-frontend --network softdomifood-network -e VITE_API_URL=http://localhost:5000/api -p 3000:3000 -v ${PWD}/frontend:/app:z softdomifood-frontend
```

### 9. Construir e iniciar Frontend Admin
```powershell
podman build -t softdomifood-admin-frontend ./admin-frontend
podman run -d --name softdomifood-admin-frontend --network softdomifood-network -e VITE_API_URL=http://localhost:5000/api -p 3001:3001 -v ${PWD}/admin-frontend:/app:z softdomifood-admin-frontend
```

### 10. Verificar que todo está corriendo
```powershell
podman ps
```

## URLs de acceso

- **Frontend Cliente**: http://localhost:3000
- **Frontend Admin**: http://localhost:3001
- **API**: http://localhost:5000
- **RabbitMQ Management**: http://localhost:15672 (usuario: admin, contraseña: admin123)

## Comandos útiles

### Ver logs
```powershell
# Logs de la API
podman logs -f softdomifood-api

# Logs de un contenedor específico
podman logs -f <nombre-contenedor>
```

### Detener todo
```powershell
podman stop softdomifood-admin-frontend softdomifood-frontend softdomifood-worker softdomifood-api softdomifood-rabbitmq softdomifood-db
```

### Eliminar todo (contenedores, volúmenes e imágenes)
```powershell
# Detener y eliminar contenedores
podman stop softdomifood-admin-frontend softdomifood-frontend softdomifood-worker softdomifood-api softdomifood-rabbitmq softdomifood-db
podman rm softdomifood-admin-frontend softdomifood-frontend softdomifood-worker softdomifood-api softdomifood-rabbitmq softdomifood-db

# Eliminar volúmenes
podman volume rm softdomifood_postgres_data softdomifood_rabbitmq_data

# Eliminar red
podman network rm softdomifood-network

# Eliminar imágenes
podman rmi softdomifood-api softdomifood-worker softdomifood-frontend softdomifood-admin-frontend
```

### Reiniciar un contenedor
```powershell
podman restart <nombre-contenedor>
```

### Ver estado de todos los contenedores
```powershell
podman ps -a
```
