# Fix: Mejoras al sistema de Favoritos

## Problema identificado

Cuando intentabas eliminar un favorito, ocurrían errores:

1. **Conflicto de rutas en FastAPI** - La ruta `GET /favorites/check/{product_id}` conflictaba con `DELETE /favorites/{product_id}` porque FastAPI lee las rutas en orden de declaración
2. **Sin manejo de errores** - No había rollback si la operación fallaba en el backend
3. **Sin validaciones** - No se validaban IDs antes de hacer requests
4. **Sin optimistic updates** - La UI esperaba respuesta del servidor antes de actualizar estado

## Soluciones implementadas

### 1. Orden correcto de rutas (Backend)

**Archivo:** `api/routers/favorites.py`

Cambio: Movemos la ruta `GET /favorites/check/{product_id}` **antes** de `DELETE /favorites/{product_id}`

```python
# ✅ Correcto: Ruta específica primero
@router.get("/favorites")                     # general
@router.post("/favorites")                    # general
@router.get("/favorites/check/{product_id}")  # específico ANTES
@router.delete("/favorites/{product_id}")     # general
```

**Por qué:** FastAPI usa greedy matching. Si DELETE está primero, "check" se interpreta como un product_id.

### 2. Manejo de errores robusto (Backend)

**Archivo:** `api/routers/favorites.py`

Se agregaron try-catch a todas las rutas:

```python
@router.delete("/favorites/{product_id}")
async def delete_favorite(product_id: str, current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get('userId')
        if not user_id:
            raise HTTPException(status_code=401, detail="Usuario no autenticado")
        success = await remove_favorite(user_id, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Favorite not found")
        return {"message": "Favorite removed"}
    except HTTPException:  # Re-raise HTTP exceptions
        raise
    except Exception as e:  # Catch unexpected errors
        print(f"Error in delete_favorite: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar favorito")
```

### 3. Validaciones en el servicio (Frontend)

**Archivo:** `frontend/src/services/favorites.service.js`

```javascript
async remove(productId) {
  if (!productId) {
    throw new Error('productId is required');  // ✅ Valida antes de hacer request
  }
  try {
    const response = await apiClient.delete(`/favorites/${productId}`);
    return mapResponseToCamelCase(response.data);
  } catch (error) {
    console.error(`Error removing favorite ${productId}:`, error);  // ✅ Logging mejorado
    throw error;
  }
}
```

### 4. Optimistic Updates con Rollback (Frontend)

**Archivo:** `frontend/src/hooks/useFavorites.js`

Implementamos el patrón **Optimistic Update** con rollback automático:

```javascript
const removeFavorite = useCallback(async (productId) => {
  if (!productId) {
    throw new Error('productId is required');
  }
  
  // 1. Guardar estado anterior
  const previousFavorites = favorites;
  
  try {
    // 2. Actualizar UI inmediatamente (optimistic)
    setFavorites(prev => prev.filter(id => id !== productId));
    
    // 3. Hacer request al backend
    await favoritesService.remove(productId);
    
    // 4. Success: emitir evento
    window.dispatchEvent(new CustomEvent('favorite:removed', { detail: { productId } }));
    
  } catch (err) {
    // 5. Error: restaurar estado anterior
    setFavorites(previousFavorites);
    setError(`Error al eliminar favorito: ${err.message}`);
    console.error('Error removing favorite:', err);
    throw err;
  }
}, [favorites]);
```

**Beneficio:** La UI se actualiza inmediatamente mientras se hace la request. Si falla, volvemos al estado anterior.

Igual para `addFavorite()`:

```javascript
const addFavorite = useCallback(async (productId) => {
  if (!productId) {
    throw new Error('productId is required');
  }
  
  // No añadir duplicados
  if (favorites.includes(productId)) {
    return;
  }
  
  const previousFavorites = favorites;
  
  try {
    // Optimistic update
    setFavorites(prev => [...prev, productId]);
    
    // Request
    await favoritesService.add(productId);
    
    // Success
    window.dispatchEvent(new CustomEvent('favorite:added', { detail: { productId } }));
    
  } catch (err) {
    // Rollback
    setFavorites(previousFavorites);
    setError(`Error al añadir a favoritos: ${err.message}`);
    console.error('Error adding favorite:', err);
    throw err;
  }
}, [favorites]);
```

## Cómo funciona el flujo ahora

### Cuando quitas un favorito:

```
[Usuario hace click en ❤️]
    ↓
[removeFavorite(productId) se ejecuta]
    ↓
[Guardamos estado anterior: previousFavorites = [prod-1, prod-2]]
    ↓
[Actualizamos UI inmediatamente: setFavorites([prod-1])]  ← El ❤️ desaparece al instante
    ↓
[Enviamos DELETE /favorites/{productId} al backend]
    ↓
    ├─ ✅ SI RESPONDE BIEN → Evento 'favorite:removed', UI permanece actualizada
    │
    └─ ❌ SI FALLA → setFavorites(previousFavorites) → El ❤️ reaparece, muestra error
```

### Manejo de errores:

1. **400-499:** Error de cliente (validación, no existe, etc.)
   - UI revierte cambio
   - Muestra error específico del servidor

2. **500+:** Error del servidor
   - UI revierte cambio
   - Muestra "Error al eliminar favorito"
   - Logs en console del navegador y backend

3. **Validación local:** Si productId es vacío/null
   - Error inmediato sin hacer request

## Pruebas

### Test 1: Agregar y quitar favoritos

```javascript
// Usar el hook en un componente
const { isFavorite, toggleFavorite } = useFavorites();

// Click en botón
<button onClick={() => toggleFavorite('prod-123')}>
  {isFavorite('prod-123') ? '❤️' : '🤍'}
</button>
```

### Test 2: Ver cambios reflejados

- Favoritos se agregan/quitan **instantáneamente** en la UI
- Si hay error, vuelven al estado anterior automáticamente
- Ver logs en DevTools → Console para debugging

### Test 3: Verificar requests

En DevTools → Network:
```
DELETE /api/favorites/prod-123
Status: 200 OK
Response: { "message": "Favorite removed" }
```

Si falla:
```
DELETE /api/favorites/prod-123
Status: 500 Internal Server Error
Response: { "message": "Error al eliminar favorito" }
```

## Cambios resumidos

| Archivo | Cambio | Tipo |
|---------|--------|------|
| `api/routers/favorites.py` | Reordenar rutas + agregar error handling | Backend |
| `frontend/src/services/favorites.service.js` | Validar ID + mejorar logging | Frontend |
| `frontend/src/hooks/useFavorites.js` | Optimistic updates + rollback pattern | Frontend |

## Impacto

✅ **Mejor UX:** Acciones inmediatas sin esperar servidor
✅ **Resiliente:** Errores se recuperan automáticamente
✅ **Debuggable:** Logging mejorado en console
✅ **Sin CORS:** Las rutas ahora están en orden correcto
✅ **Validado:** No se envían requests con datos inválidos

## Next steps (Opcional)

1. Agregar notificación visual (toast) cuando ocurra error
2. Añadir loading state mientras se procesa la request
3. Crear tests unitarios para `useFavorites` hook
4. Implementar retry automático en caso de timeout

---

**Creado:** Diciembre 3, 2025
