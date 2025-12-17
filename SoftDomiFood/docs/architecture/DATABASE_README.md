# Base de Datos - Backups y Restores

Esta carpeta contiene los backups de la base de datos que pueden ser compartidos entre los miembros del equipo.

## Estructura

```
database/
├── README.md              # Este archivo
├── backups/               # Backups de la base de datos (SQL dumps)
│   └── initial_data.sql  # Datos iniciales con productos, usuarios de ejemplo
└── .gitkeep              # Para mantener la carpeta en git
```

## Scripts Disponibles

### Backup de Base de Datos

Ejecutar desde la raíz del proyecto:
```powershell
.\scripts\backup-database.ps1
```

Esto creará un dump SQL en `database/backups/backup_YYYYMMDD_HHMMSS.sql`

### Restore de Base de Datos

Ejecutar desde la raíz del proyecto:
```powershell
.\scripts\restore-database.ps1 -BackupFile "database/backups/backup_20241123_104500.sql"
```

O restaurar los datos iniciales:
```powershell
.\scripts\restore-database.ps1 -BackupFile "database/backups/initial_data.sql"
```

## Compartir Datos con el Equipo

1. **Exportar datos actuales:**
   ```powershell
   .\scripts\backup-database.ps1
   ```

2. **Commit y push del backup:**
   ```powershell
   git add database/backups/backup_*.sql
   git commit -m "Backup de base de datos - [Fecha]"
   git push
   ```

3. **Para que tus compañeros restauren:**
   ```powershell
   git pull
   .\scripts\restore-database.ps1 -BackupFile "database/backups/backup_YYYYMMDD_HHMMSS.sql"
   ```

## Datos Iniciales

El archivo `initial_data.sql` contiene datos de ejemplo que se pueden usar para inicializar una base de datos limpia con:
- Usuario administrador
- Productos de ejemplo
- Usuarios de prueba
- Pedidos de ejemplo

Para restaurar datos iniciales:
```powershell
.\scripts\restore-database.ps1 -BackupFile "database/backups/initial_data.sql"
```

