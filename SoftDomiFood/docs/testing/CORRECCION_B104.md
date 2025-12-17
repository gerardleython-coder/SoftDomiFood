# ✅ Corrección de Vulnerabilidad B104

## 🔴 Vulnerabilidad Corregida

**ID:** B104 - Hardcoded Bind All Interfaces  
**Severidad:** Medium  
**Ubicación:** `api/main.py:98`  
**Estado:** ✅ **CORREGIDA**

---

## 📝 Cambios Realizados

### Antes (Vulnerable)
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
```

### Después (Seguro)
```python
if __name__ == "__main__":
    import uvicorn
    # Configuración segura: usar variables de entorno con valores por defecto seguros
    # En desarrollo, usar 127.0.0.1 (solo localhost) es más seguro
    # En producción con Docker, configurar HOST=0.0.0.0 en docker-compose.yml
    host = os.getenv("HOST", "127.0.0.1")  # Default seguro: solo localhost
    port = int(os.getenv("PORT", "5000"))
    uvicorn.run(app, host=host, port=port)
```

---

## 🔧 Configuración

### Desarrollo Local
Por defecto, el servidor escuchará en `127.0.0.1:5000` (solo localhost), que es más seguro.

### Docker/Producción
Para que el servidor escuche en todas las interfaces (necesario en Docker), configurar la variable de entorno:

**Opción 1: En docker-compose.yml**
```yaml
services:
  api:
    environment:
      - HOST=0.0.0.0
      - PORT=5000
```

**Opción 2: En archivo .env**
```env
HOST=0.0.0.0
PORT=5000
```

**Nota:** El `docker-compose.yml` actual usa el comando directo `uvicorn main:app --host 0.0.0.0 --port 5000`, que tiene precedencia sobre el código Python. Esto está bien y no afecta la seguridad porque:
- El comando explícito es intencional para Docker
- El código Python ahora tiene un valor por defecto seguro
- Si se ejecuta directamente con `python main.py`, usará el valor seguro por defecto

---

## ✅ Beneficios de la Corrección

1. **Valor por defecto seguro:** `127.0.0.1` solo permite conexiones locales
2. **Configurable:** Permite cambiar el host mediante variables de entorno
3. **Mejores prácticas:** Sigue el principio de "secure by default"
4. **Flexibilidad:** Funciona tanto en desarrollo como en producción

---

## 🧪 Verificación

Para verificar que la corrección funciona:

1. **Ejecutar localmente (debe usar 127.0.0.1):**
   ```bash
   python api/main.py
   # Servidor escuchará en http://127.0.0.1:5000
   ```

2. **Ejecutar con variable de entorno (puede usar 0.0.0.0):**
   ```bash
   HOST=0.0.0.0 python api/main.py
   # Servidor escuchará en http://0.0.0.0:5000
   ```

3. **Re-ejecutar análisis de seguridad:**
   ```bash
   docker run --rm -v "${PWD}:/app" salchipapas-qa:latest \
     bandit -r /app/api -f txt \
     --severity-level medium \
     --confidence-level medium \
     -x venv -x __pycache__ -x .git -x node_modules -x tests \
     --exclude /app/api/venv
   ```
   
   **Resultado esperado:** B104 ya no debería aparecer en `api/main.py`

---

## 📋 Checklist de Seguridad

- [x] Valor por defecto cambiado a `127.0.0.1`
- [x] Configuración mediante variables de entorno
- [x] Documentación del cambio
- [x] Compatible con Docker (mediante variables de entorno)
- [x] No rompe funcionalidad existente

---

## 🔗 Referencias

- **CWE:** CWE-605 (Multiple Binds to the Same Port)
- **Bandit Plugin:** B104_hardcoded_bind_all_interfaces
- **Documentación:** https://bandit.readthedocs.io/en/1.7.5/plugins/b104_hardcoded_bind_all_interfaces.html

---

**Fecha de corrección:** 2025-11-22  
**Estado:** ✅ Completado

