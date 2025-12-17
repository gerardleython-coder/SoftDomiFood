# Scripts de Utilidad

Esta carpeta contiene scripts auxiliares organizados por propósito.

## Estructura

### `/utils/`
Scripts de verificación y debugging:
- `check_admin.py` - Verifica si existe usuario admin en la BD
- `check_columns.py` - Verifica columnas de tablas en la BD
- `check_coupons_table.py` - Verifica estructura de tabla cupones

### `/database/`
Scripts relacionados con operaciones de base de datos:
- `force_create_tables.py` - Fuerza la creación de tablas (uso temporal)
- `verify_addresses_table.py` - Verifica la tabla addresses

### `/ops/`
Scripts operacionales (PowerShell):
- `backup-database.ps1` - Crea backup de la base de datos
- `create-initial-backup.ps1` - Crea backup inicial
- `initialize-database.ps1` - Inicializa la base de datos
- `restore-database.ps1` - Restaura base de datos desde backup

## Uso

### Scripts de Verificación
```bash
# Desde el contenedor de la API
docker exec softdomifood-api python scripts/utils/check_admin.py
docker exec softdomifood-api python scripts/utils/check_columns.py
docker exec softdomifood-api python scripts/utils/check_coupons_table.py
```

### Scripts de Base de Datos
```bash
# Desde el contenedor de la API
docker exec softdomifood-api python scripts/database/verify_addresses_table.py
```

### Scripts Operacionales
```powershell
# Desde la raíz del proyecto en Windows
.\scripts\ops\initialize-database.ps1
.\scripts\ops\backup-database.ps1
.\scripts\ops\restore-database.ps1
```

## Notas

- Los scripts de Python requieren acceso a las variables de entorno y a la base de datos
- Los scripts de PowerShell están diseñados para ejecutarse desde la raíz del proyecto
- Para scripts de seed/inicialización, ver la carpeta `/api/` (seed_data.py, init_db.py)
