# Guía de migración a nueva arquitectura

## Tabla de contenidos

1. [Resumen de cambios](#resumen)
2. [Cómo usar los nuevos servicios](#servicios)
3. [Cómo usar los custom hooks](#hooks)
4. [Cómo usar los helpers de dominio](#domain)
5. [Ejemplos de refactorización](#ejemplos)
6. [Running tests](#testing)

---

## Resumen de cambios {#resumen}

### Estructura de directorios

Se agregaron tres nuevos directorios en `frontend/src/`:

```
src/
├── domain/          # Lógica de negocio pura (sin UI, sin API)
├── services/        # Facades para operaciones de API
├── hooks/           # Custom hooks para gestión de estado
└── __tests__/       # Tests unitarios
```

### Archivos creados

**Domain layer (4 archivos):**
- `domain/orderStatus.js` — Mapeo de estados y acciones
- `domain/dateFormat.js` — Formatting y parsing de fechas
- `domain/orderFactory.js` — Factory para crear payloads
- `domain/validateOrder.js` — Validaciones de negocio

**Service facades (6 archivos):**
- `services/apiClient.js` — Cliente axios configurado
- `services/orders.service.js` — Operaciones de órdenes
- `services/products.service.js` — Operaciones de productos
- `services/favorites.service.js` — Operaciones de favoritos
- `services/reviews.service.js` — Operaciones de reseñas
- `services/auth.service.js` — Operaciones de autenticación
- `services/coupons.service.js` — Validación de cupones

**Custom hooks (5 archivos):**
- `hooks/useClientOrders.js` — Gestión de órdenes del cliente
- `hooks/useProducts.js` — Gestión de productos
- `hooks/useFavorites.js` — Gestión de favoritos
- `hooks/useReviews.js` — Gestión de reseñas

**Tests (4 archivos):**
- `__tests__/domain/orderFactory.test.js`
- `__tests__/domain/orderStatus.test.js`
- `__tests__/domain/dateFormat.test.js`
- `__tests__/domain/validateOrder.test.js`

---

## Cómo usar los nuevos servicios {#servicios}

### Import

```javascript
import ordersService from '../services/orders.service';
import productsService from '../services/products.service';
import favoritesService from '../services/favorites.service';
import reviewsService from '../services/reviews.service';
import authService from '../services/auth.service';
import couponsService from '../services/coupons.service';
```

### Ejemplos de uso

#### Orders Service

```javascript
// Crear orden
const order = await ordersService.createOrder({
  items: [...],
  addressId: 'addr-123',
  paymentMethod: 'credit_card',
  total: 250,
  couponCode: 'SAVE10',
  scheduledFor: '2025-12-05T14:00:00Z',
});

// Obtener mis órdenes
const myOrders = await ordersService.getMyOrders();

// Obtener orden por ID
const order = await ordersService.getOrderById('order-123');

// Cancelar orden
const updated = await ordersService.cancelOrder('order-123');
```

#### Products Service

```javascript
// Obtener todos los productos
const products = await productsService.getAll();

// Obtener producto por ID
const product = await productsService.getById('prod-123');

// Obtener reseñas de producto
const reviews = await productsService.getReviews('prod-123');
// Returns: { average: 4.5, total: 10, reviews: [...] }

// Verificar si user puede revisar
const canReview = await productsService.canReview('prod-123');
// Returns: { canReview: true, reason: null }
```

#### Favorites Service

```javascript
// Obtener favoritos
const favorites = await favoritesService.getAll();
// Returns: ['prod-1', 'prod-2', 'prod-3']

// Agregar a favoritos
await favoritesService.add('prod-123');

// Remover de favoritos
await favoritesService.remove('prod-123');

// Verificar si es favorito
const { exists } = await favoritesService.check('prod-123');
```

#### Reviews Service

```javascript
// Crear reseña
const review = await reviewsService.createReview({
  productId: 'prod-123',
  rating: 5,
  comment: 'Excelente producto!',
});

// Obtener reseñas del producto
const reviews = await reviewsService.getProductReviews('prod-123');

// Verificar si user puede revisar
const { canReview } = await reviewsService.canReviewProduct('prod-123');
```

#### Auth Service

```javascript
// Registrar
const user = await authService.register({
  name: 'Juan',
  email: 'juan@example.com',
  password: 'secure123',
});

// Login
const user = await authService.login({
  email: 'juan@example.com',
  password: 'secure123',
});

// Obtener perfil actual
const profile = await authService.getProfile();

// Logout
authService.logout();

// Verificar si autenticado
if (authService.isAuthenticated()) {
  // ...
}

// Obtener user almacenado
const storedUser = authService.getStoredUser();
```

#### Coupons Service

```javascript
// Validar cupón
const coupon = await couponsService.validate('SAVE10');
// Returns: { code: 'SAVE10', discountPercent: 10, ... }
```

### Manejo de errores

Todos los servicios lanzan errores normalizados:

```javascript
try {
  await ordersService.createOrder(payload);
} catch (error) {
  console.log(error.status);        // 400, 401, 500, etc.
  console.log(error.message);       // Mensaje legible
  console.log(error.data);          // Datos de error del backend
  console.log(error.original);      // Error original de axios
}
```

---

## Cómo usar los custom hooks {#hooks}

Los hooks encapsulan estado y servicios. Son la forma recomendada de acceder a datos en componentes.

### useClientOrders

```javascript
import { useClientOrders } from '../hooks/useClientOrders';

function MyOrdersPage() {
  const { orders, loading, error, loadOrders, createOrder, cancelOrder } = useClientOrders();

  // Orders se carga automáticamente en mount
  // Loading y error se manejan automáticamente

  const handleCreateOrder = async () => {
    try {
      const newOrder = await createOrder({
        cart: cartItems,
        orderForm: { addressId, paymentMethod },
        appliedCoupon: coupon,
        scheduledFor: scheduled ? scheduledDateTime : null,
      });
      console.log('Orden creada:', newOrder);
    } catch (err) {
      console.error('Error:', err.message);
    }
  };

  const handleCancel = async (orderId) => {
    try {
      await cancelOrder(orderId);
    } catch (err) {
      console.error('Error:', err.message);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      {orders.map(order => (
        <div key={order.id}>
          {order.status} - ${order.total}
          {order.status !== 'delivered' && (
            <button onClick={() => handleCancel(order.id)}>Cancelar</button>
          )}
        </div>
      ))}
    </div>
  );
}
```

### useProducts

```javascript
import { useProducts } from '../hooks/useProducts';

function ProductsPage() {
  const { products, loading, getProduct, getReviews, canReview } = useProducts();

  const handleViewDetails = async (productId) => {
    const product = await getProduct(productId);
    const reviews = await getReviews(productId);
    const { canReview: userCanReview } = await canReview(productId);
    console.log({ product, reviews, userCanReview });
  };

  if (loading) return <div>Cargando productos...</div>;

  return (
    <div>
      {products.map(product => (
        <div key={product.id} onClick={() => handleViewDetails(product.id)}>
          {product.name} - ${product.price}
        </div>
      ))}
    </div>
  );
}
```

### useFavorites

```javascript
import { useFavorites } from '../hooks/useFavorites';

function ProductCard({ product }) {
  const { favorites, isFavorite, toggleFavorite } = useFavorites();

  const handleToggle = async () => {
    try {
      await toggleFavorite(product.id);
    } catch (err) {
      console.error('Error:', err.message);
    }
  };

  return (
    <div>
      {product.name}
      <button onClick={handleToggle}>
        {isFavorite(product.id) ? '❤️' : '🤍'}
      </button>
    </div>
  );
}
```

### useReviews

```javascript
import { useReviews } from '../hooks/useReviews';

function ProductReviews({ productId }) {
  const { reviews, loading, createReview, checkCanReview } = useReviews(productId);

  const handleSubmitReview = async (rating, comment) => {
    try {
      const review = await createReview({ rating, comment });
      console.log('Reseña creada:', review);
    } catch (err) {
      console.error('Error:', err.message);
    }
  };

  const handleCheckCanReview = async () => {
    const { canReview, reason } = await checkCanReview();
    if (!canReview) {
      alert('No puedes revisar: ' + reason);
    }
  };

  if (loading) return <div>Cargando reseñas...</div>;

  return (
    <div>
      <h3>Promedio: {reviews.average} ({reviews.total} reseñas)</h3>
      <button onClick={handleCheckCanReview}>Escribir reseña</button>
      {reviews.reviews.map(review => (
        <div key={review.id}>
          <p>{review.userName}</p>
          <p>{review.rating}⭐</p>
          <p>{review.comment}</p>
        </div>
      ))}
    </div>
  );
}
```

---

## Cómo usar los helpers de dominio {#domain}

Los helpers de dominio no tienen efectos secundarios y son fáciles de testear.

### orderStatus

```javascript
import {
  ORDER_STATUSES,
  getStatusUI,
  isTerminalStatus,
  canReviewOrder,
  isScheduledOrder,
  getAllowedAdminActions,
} from '../domain/orderStatus';

// Obtener UI para estado
const ui = getStatusUI(order.status);
console.log(ui.label); // 'Pendiente', 'En preparación', etc.
console.log(ui.color); // 'bg-yellow-100'
console.log(ui.textColor); // 'text-yellow-800'

// Verificar si estado es terminal
if (isTerminalStatus(order.status)) {
  console.log('Esta orden no cambiará más');
}

// Verificar si la orden puede ser revisada
if (canReviewOrder(order.status)) {
  // Mostrar botón "Escribir reseña"
}

// Verificar si es orden programada
if (isScheduledOrder(order.status)) {
  console.log('Esta orden está programada para:', order.scheduledFor);
}

// Obtener acciones permitidas para admin
const actions = getAllowedAdminActions(order.status);
// ['startPreparing', 'cancel'] para pending
// ['cancel'] para scheduled
// [] para delivered
```

### dateFormat

```javascript
import {
  formatDateTime,
  formatDate,
  formatRelativeTime,
  parseLocalDateTimeToISO,
  isoToDatetimeLocal,
  isFutureDateTime,
  getHoursUntil,
} from '../domain/dateFormat';

// Formatear fecha/hora completa
const formatted = formatDateTime('2025-12-05T14:30:00Z');
// "05/12/2025, 14:30"

// Formatear solo fecha
const date = formatDate('2025-12-05T14:30:00Z');
// "5 de diciembre de 2025"

// Formatear relativo
const relative = formatRelativeTime('2025-12-04T14:30:00Z');
// "hace 1 día" (si hoy es 2025-12-05)

// Convertir de datetime-local a ISO
const iso = parseLocalDateTimeToISO('2025-12-05T14:30');
// "2025-12-05T14:30:00.000Z"

// Convertir de ISO a datetime-local (para <input type="datetime-local" />)
const localFormat = isoToDatetimeLocal('2025-12-05T14:30:00Z');
// "2025-12-05T14:30"

// Verificar si fecha es futura
if (isFutureDateTime('2025-12-05T14:30:00Z')) {
  console.log('Esta fecha es en el futuro');
}

// Obtener horas hasta una fecha
const hours = getHoursUntil('2025-12-05T14:30:00Z');
console.log(`Faltan ${hours} horas`);
```

### orderFactory

```javascript
import {
  createOrderPayload,
  validateOrderPayload,
  calculateOrderTotal,
  isCartEligibleForCoupon,
} from '../domain/orderFactory';

// Crear payload normalizado y validado
const payload = createOrderPayload({
  cart: cartItems,
  orderForm: { addressId, paymentMethod, notes },
  appliedCoupon: coupon,
  scheduledFor: isScheduled ? datetime : null,
});
// Throw error si falta algo

// Validar payload antes de enviar
const { valid, errors } = validateOrderPayload(payload);
if (!valid) {
  console.error('Errores:', errors);
}

// Calcular total con descuentos y impuestos
const totals = calculateOrderTotal(subtotal, coupon, taxPercent);
// { subtotal: 100, discount: 10, tax: 9, total: 99 }

// Verificar si carrito es elegible para cupón
const { eligible, reason } = isCartEligibleForCoupon(cart, coupon);
if (!eligible) {
  console.log('No es elegible:', reason);
}
```

### validateOrder

```javascript
import {
  validateScheduledOrder,
  validateOrderForm,
  validateCouponCode,
  validateCartNotEmpty,
  validateCartItems,
} from '../domain/validateOrder';

// Validar orden programada
const { valid, errors } = validateScheduledOrder(
  dateTime,
  48, // max hours
  { open: '09:00', close: '21:00' } // restaurant hours
);

// Validar formulario de orden
const formValidation = validateOrderForm({
  addressId: 'addr-1',
  paymentMethod: 'credit_card',
  scheduleEnabled: true,
  scheduledFor: datetime,
});

// Validar código de cupón
const { valid, error } = validateCouponCode('SAVE10');

// Validar carrito no vacío
const cartValid = validateCartNotEmpty(cart);

// Validar items del carrito
const itemsValid = validateCartItems(cart);
```

---

## Ejemplos de refactorización {#ejemplos}

### Antes: Componente mezclado

```javascript
// ❌ Lógica dispersa, duplicada, difícil de testear
function ClientPage() {
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [addressId, setAddressId] = useState('');
  const [paymentMethod, setPaymentMethod] = useState('');
  const [scheduleEnabled, setScheduleEnabled] = useState(false);
  const [scheduledFor, setScheduledFor] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // ... 10+ más estados

  useEffect(() => {
    setLoading(true);
    api.get('/orders')
      .then(res => setOrders(res.data))
      .catch(err => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    api.get('/addresses')
      .then(res => setAddresses(res.data))
      .catch(err => setError(err.message));
  }, []);

  const handlePlaceOrder = async () => {
    try {
      if (!cart.length) {
        setError('El carrito está vacío');
        return;
      }
      if (!addressId) {
        setError('Selecciona una dirección');
        return;
      }
      if (!paymentMethod) {
        setError('Selecciona un método de pago');
        return;
      }

      if (scheduleEnabled && !scheduledFor) {
        setError('Selecciona fecha/hora de entrega');
        return;
      }

      if (scheduleEnabled) {
        const date = new Date(scheduledFor);
        if (date < new Date()) {
          setError('La fecha debe ser en el futuro');
          return;
        }
        const hours = (date - new Date()) / (1000 * 60 * 60);
        if (hours > 48) {
          setError('Máximo 48 horas adelante');
          return;
        }
      }

      setLoading(true);
      const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
      const payload = {
        items: cart.map(item => ({
          productId: item.id,
          quantity: item.quantity,
          price: item.price,
        })),
        addressId,
        paymentMethod,
        total,
        scheduledFor: scheduleEnabled ? scheduledFor : null,
      };

      const res = await api.post('/orders', payload);
      const order = res.data;
      setOrders([order, ...orders]);
      setCart([]);
      setScheduleEnabled(false);
      setScheduledFor('');
      setError(null);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Cargando...</div>;
  if (error) return <div className="error">{error}</div>;

  return (
    <div>
      <h1>Mi compra</h1>
      {/* ... render */}
    </div>
  );
}
```

### Después: Con nueva arquitectura

```javascript
// ✅ Limpio, modular, testeable
import { useClientOrders } from '../hooks/useClientOrders';
import { useFavorites } from '../hooks/useFavorites';
import { createOrderPayload } from '../domain/orderFactory';

function ClientPage() {
  const { orders, loading, error, createOrder } = useClientOrders();
  const { isFavorite, toggleFavorite } = useFavorites();
  
  const [cart, setCart] = useState([]);
  const [orderForm, setOrderForm] = useState({
    addressId: '',
    paymentMethod: '',
    notes: '',
  });
  const [scheduleEnabled, setScheduleEnabled] = useState(false);
  const [scheduledFor, setScheduledFor] = useState('');
  const [localError, setLocalError] = useState(null);

  const handlePlaceOrder = async () => {
    try {
      setLocalError(null);
      // Factory + validación centralizada
      const order = await createOrder({
        cart,
        orderForm,
        scheduledFor: scheduleEnabled ? scheduledFor : null,
      });
      
      // Success
      setCart([]);
      setScheduleEnabled(false);
      setScheduledFor('');
      
      // Evento global para que UI reaccione
      window.dispatchEvent(new CustomEvent('order:created', { detail: order }));
    } catch (err) {
      // Error normalizado
      setLocalError(err.message);
    }
  };

  if (loading) return <Spinner />;

  return (
    <div>
      <h1>Mi compra</h1>
      {error && <Alert type="error">{error}</Alert>}
      {localError && <Alert type="error">{localError}</Alert>}
      <OrderForm
        cart={cart}
        onAddItem={...}
        onRemoveItem={...}
        orderForm={orderForm}
        onFormChange={setOrderForm}
        scheduleEnabled={scheduleEnabled}
        onScheduleEnabledChange={setScheduleEnabled}
        scheduledFor={scheduledFor}
        onScheduledForChange={setScheduledFor}
        onPlaceOrder={handlePlaceOrder}
      />
      <MyOrders orders={orders} />
    </div>
  );
}
```

---

## Running tests {#testing}

### Instalar dependencias (si no las tienes)

```bash
cd frontend
npm install --save-dev jest @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

### Configurar Jest

En `package.json`:

```json
{
  "jest": {
    "testEnvironment": "jsdom",
    "setupFilesAfterEnv": ["<rootDir>/src/setupTests.js"],
    "moduleNameMapper": {
      "\\.(css|less|scss|sass)$": "identity-obj-proxy"
    }
  }
}
```

Crear `src/setupTests.js`:

```javascript
import '@testing-library/jest-dom';
```

### Ejecutar tests

```bash
# Todos los tests
npm test

# Solo tests de dominio
npm test -- domain

# Con coverage
npm test -- --coverage

# Watch mode
npm test -- --watch

# Test específico
npm test -- orderFactory.test.js
```

### Añadir a CI/CD

En `.github/workflows/test.yml`:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd frontend && npm ci
      - run: cd frontend && npm test -- --coverage
      - uses: codecov/codecov-action@v3
```

---

## Siguiente paso: Refactorización progresiva

Ahora que tienes la infraestructura lista, puedes refactorizar componentes gradualmente:

1. **ClientPage.jsx** → usa `useClientOrders` + `useFavorites` + `useProducts`
2. **OrderForm.jsx** → simplificar, usar validadores de dominio
3. **AdminPage.jsx** → usa `getAllowedAdminActions` para botones
4. **ProductCard.jsx** → usa `useFavorites`, `useReviews`
5. **MyOrders.jsx** → usa `getStatusUI`, `formatDateTime`

Cada refactor es independiente y puede hacerse sin romper nada.

---

**Guía creada:** Diciembre 3, 2025
