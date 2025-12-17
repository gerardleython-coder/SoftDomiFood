import React, { useState, useEffect } from 'react';
import ClientLayout from '../components/client/ClientLayout';
import ProductCard from '../components/client/ProductCard';
import Cart from '../components/client/Cart';
import OrderForm from '../components/client/OrderForm';
import MyOrders from '../components/client/MyOrders';
import FavoritesList from '../components/client/FavoritesList';
import { authAPI, productsAPI, ordersAPI, addressesAPI, favoritesAPI } from '../utils/api';
import { useFavorites } from '../hooks/useFavorites';

const ClientPage = ({ switchToAdmin, toast, adminUser = null, isAdminView = false }) => {
  // Use the useFavorites hook
  const { favorites, isFavorite, toggleFavorite, error: favoritesError } = useFavorites();

  const [user, setUser] = useState(null);
  const [cart, setCart] = useState([]);
  const [products, setProducts] = useState([]);
  const [addresses, setAddresses] = useState([]);
  const [orders, setOrders] = useState([]);
  const [activeTab, setActiveTab] = useState('menu');
  const [orderForm, setOrderForm] = useState({
    notes: '',
    addressId: '',
    paymentMethod: 'CASH'
  });
  // ✅ Pedido programado
  const [scheduleEnabled, setScheduleEnabled] = useState(false);
  const [scheduledFor, setScheduledFor] = useState(""); // formato datetime-local: yyyy-mm-ddThh:mm
  const [appliedCoupon, setAppliedCoupon] = useState(null);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [isCartVisible, setIsCartVisible] = useState(true);
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [registerData, setRegisterData] = useState({ email: '', password: '', name: '', phone: '' });
  // Categorías que coinciden con el backend y panel de administrador
  const categories = ['Todos', 'SALCHIPAPAS', 'BEBIDAS', 'ADICIONALES', 'COMBOS'];
  const [selectedCategory, setSelectedCategory] = useState('Todos');

  // Función para obtener etiquetas amigables de las categorías
  const getCategoryLabel = (category) => {
    if (category === 'Todos') return 'Todos';
    const labels = {
      'SALCHIPAPAS': 'Salchipapas',
      'BEBIDAS': 'Bebidas',
      'ADICIONALES': 'Adicionales',
      'COMBOS': 'Combos'
    };
    return labels[category] || category;
  };

  // Load real data from API
  useEffect(() => {
    // Verificar si hay un parámetro que indique que NO debe restaurar sesión
    const urlParams = new URLSearchParams(window.location.search);
    const noSession = urlParams.get('noSession') === 'true';

    if (noSession) {
      // Si viene desde admin, limpiar todos los tokens de cliente y NO restaurar sesión
      localStorage.removeItem('clientToken');
      localStorage.removeItem('clientUser');
      localStorage.removeItem('token');
      setUser(null);
      setAddresses([]);
      setOrders([]);
      // Limpiar el parámetro de la URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Solo cargar productos, no autenticación ni datos del usuario
      loadProducts();
      return;
    }

    // Guardar la vista actual si es vista de cliente normal
    if (!isAdminView) {
      localStorage.setItem('lastView', 'client');
    }

    loadProducts();
    if (!isAdminView) {
      loadAddresses();
      loadOrders();
      // useFavorites hook loads automatically
      checkAuth();
    }
    // Removido el caso de adminUser ya que esta es solo la app de cliente
  }, [isAdminView]);

  const checkAuth = async () => {
    // Si es vista de admin, no verificar autenticación de cliente
    if (isAdminView) {
      return;
    }

    // Usar token de cliente específico
    const token = localStorage.getItem('clientToken');
    if (token) {
      try {
        // Usar el token de cliente para obtener el perfil
        const profile = await authAPI.getProfile();
        setUser(profile);
      } catch (error) {
        console.error('Error loading profile:', error);
        localStorage.removeItem('clientToken');
        localStorage.removeItem('clientUser');
      }
    }
  };

  const loadProducts = async () => {
    try {
      const data = await productsAPI.getAll();
      // API returns {products: [...]} so we need to extract the array
      setProducts(data.products || data || []);
    } catch (error) {
      console.error('Error loading products:', error);
      setProducts([]); // Set empty array on error
    }
  };

  const loadAddresses = async () => {
    // Si es vista de admin, no cargar direcciones
    if (isAdminView) {
      return;
    }

    const token = localStorage.getItem('clientToken');
    if (!token) return; // Skip if not authenticated

    try {
      const data = await addressesAPI.getAll();
      // API returns {addresses: [...]} so we need to extract the array
      const addressesList = data.addresses || data || [];
      setAddresses(addressesList);

      // Set default address if none selected and addresses exist
      if (orderForm.addressId === '' && addressesList.length > 0) {
        const defaultAddress = addressesList.find(addr => addr.isDefault) || addressesList[0];
        if (defaultAddress) {
          setOrderForm(prev => ({
            ...prev,
            addressId: defaultAddress.id
          }));
        }
      }
    } catch (error) {
      console.error('Error loading addresses:', error);
      setAddresses([]); // Set empty array on error
    }
  };

  const handleAddressAdded = (newAddress) => {
    setAddresses(prev => [...prev, newAddress]);
    // Optionally set the new address as selected
    setOrderForm(prev => ({
      ...prev,
      addressId: newAddress.id
    }));
  };

  const handleToggleFavorite = async (productId) => {
    if (!user) {
      toast.error('Debes iniciar sesión para agregar favoritos');
      return;
    }

    try {
      await toggleFavorite(productId);
      if (isFavorite(productId)) {
        toast.success('Producto eliminado de favoritos');
      } else {
        toast.success('Producto agregado a favoritos');
      }
    } catch (error) {
      console.error('Error toggling favorite:', error);
      toast.error(favoritesError || 'Error al gestionar favorito');
    }
  };

  const loadOrders = async () => {
    // Si es vista de admin, no cargar pedidos del cliente
    if (isAdminView) {
      return;
    }

    const token = localStorage.getItem('clientToken');
    if (!token) return; // Skip if not authenticated

    try {
      const data = await ordersAPI.getAll();
      // API might return {orders: [...]} so we need to extract the array
      setOrders(data.orders || data || []);
    } catch (error) {
      console.error('Error loading orders:', error);
      setOrders([]); // Set empty array on error
    }
  };

  const addToCart = (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
      setCart(cart.map(item =>
        item.id === product.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity === 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item =>
        item.id === productId
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const getTotalPrice = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  const handlePlaceOrder = async () => {
    // Si es vista de admin, no permitir crear pedidos
    if (isAdminView) {
      toast.warning('Los administradores no pueden realizar pedidos desde esta vista');
      return;
    }

    if (cart.length === 0) {
      toast.warning('El carrito está vacío');
      return;
    }

    if (scheduleEnabled && !scheduledFor) {
      toast.warning('Debes elegir la fecha y hora para programar el pedido');
      return;
    }

    // Validación estricta: solo usuarios autenticados pueden crear pedidos
    const token = localStorage.getItem('clientToken');
    if (!token || !user) {
      toast.error('Debes iniciar sesión para realizar un pedido');
      setShowLogin(true);
      return;
    }

    if (!orderForm.addressId) {
      toast.warning('Debes seleccionar una dirección de entrega');
      return;
    }

    try {
      // Calcular el total
      const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

      const orderData = {
        items: cart.map(item => ({
          productId: item.id,
          quantity: item.quantity,
          price: item.price  // Incluir el precio
        })),
        addressId: orderForm.addressId,
        paymentMethod: orderForm.paymentMethod,
        notes: orderForm.notes || null,
        total: total,  // Incluir el total calculado
        couponCode: appliedCoupon ? appliedCoupon.code : null,
        scheduledFor: scheduleEnabled && scheduledFor ? scheduledFor : null,
      };

      await ordersAPI.create(orderData);
      setCart([]);
      setAppliedCoupon(null);  // Limpiar cupón aplicado
      setOrderForm({ notes: '', addressId: '', paymentMethod: 'CASH' });
      setScheduleEnabled(false);
      setScheduledFor("");
      toast.success('¡Pedido realizado con éxito!');
      loadOrders();
      setActiveTab('orders'); // Cambiar a la pestaña de pedidos
    } catch (error) {
      console.error('Error creating order:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error desconocido';
      if (error.response?.status === 401) {
        toast.error('Sesión expirada. Por favor inicia sesión nuevamente');
        handleLogout();
      } else {
        toast.error(`Error al crear el pedido: ${errorMessage}`);
      }
    }
  };

  const handleLogout = () => {
    // Solo remover token y datos de cliente, no afectar admin
    localStorage.removeItem('clientToken');
    localStorage.removeItem('clientUser');
    setUser(null);
    setAddresses([]);
    setOrders([]);
    setCart([]);
    setScheduleEnabled(false);
    setScheduledFor("");
    setActiveTab('menu');
    toast.info('Sesión cerrada correctamente');
  };

  const handleLogin = async () => {
    try {
      // Login como cliente (no admin)
      const response = await authAPI.login(loginData, false);
      setUser(response.user);
      setShowLogin(false);
      setLoginData({ email: '', password: '' });
      toast.success('¡Bienvenido!');
      // Guardar que estamos en vista de cliente
      localStorage.setItem('lastView', 'client');
      loadAddresses();
      loadOrders();
      // useFavorites hook loads automatically
    } catch (error) {
      console.error('Error logging in:', error);
      const errorMessage = error.response?.data?.detail || 'Error al iniciar sesión. Verifica tus credenciales.';
      toast.error(errorMessage);
    }
  };

  const handleRegister = async () => {
    try {
      const response = await authAPI.register(registerData);
      // El registro ya guarda el token en authAPI.register
      if (response.user) {
        setUser(response.user);
        toast.success('¡Registro exitoso! Bienvenido.');
        setShowRegister(false);
        // Guardar que estamos en vista de cliente
        localStorage.setItem('lastView', 'client');
        loadAddresses();
        loadOrders();
        // useFavorites hook loads automatically
      } else {
        toast.success('¡Registro exitoso! Ahora puedes iniciar sesión.');
        setShowRegister(false);
        setShowLogin(true);
      }
      setRegisterData({ email: '', password: '', name: '', phone: '' });
    } catch (error) {
      console.error('Error registering:', error);
      const errorMessage = error.response?.data?.detail || 'Error al registrarse. El email puede estar en uso.';
      toast.error(errorMessage);
    }
  };

  const filteredProducts = selectedCategory === 'Todos'
    ? products.filter(p => p.isAvailable)
    : products.filter(p => p.category === selectedCategory && p.isAvailable);

  return (
    <>
      <ClientLayout
        user={user}
        cartCount={cart.reduce((sum, item) => sum + item.quantity, 0)}
        onLogin={() => setShowLogin(true)}
        onCartClick={() => setIsCartVisible(!isCartVisible)}
        onLogout={handleLogout}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      >
        {activeTab === 'menu' ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Products Section */}
            <div className="lg:col-span-2">
              <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-800 mb-6">Nuestro Menú</h2>

                {/* Category Filter */}
                <div className="flex flex-wrap gap-2 mb-6">
                  {categories.map(category => (
                    <button
                      key={category}
                      onClick={() => setSelectedCategory(category)}
                      className={`px-4 py-2 rounded-full ${
                        selectedCategory === category
                          ? 'bg-orange-500 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {getCategoryLabel(category)}
                    </button>
                  ))}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {filteredProducts.map(product => (
                    <ProductCard
                      key={product.id}
                      product={product}
                      onAddToCart={addToCart}
                      isFavorite={isFavorite(product.id)}
                      onToggleFavorite={handleToggleFavorite}
                      isAuthenticated={!!user}
                    />
                  ))}
                </div>
              </div>
            </div>

            {/* Cart and Order Form Section */}
            <div className="lg:col-span-1 space-y-6">
              {isCartVisible && (
                <Cart
                  cart={cart}
                  onUpdateQuantity={updateQuantity}
                  onRemoveFromCart={removeFromCart}
                  totalPrice={getTotalPrice()}
                  onCouponApplied={setAppliedCoupon}
                  appliedCoupon={appliedCoupon}
                  toast={toast}
                  onClose={() => setIsCartVisible(false)}
                />
              )}

              {!isAdminView && (
                <OrderForm
                  addresses={addresses}
                  orderForm={orderForm}
                  onAddressChange={(e) => setOrderForm({...orderForm, addressId: e.target.value})}
                  onNotesChange={(e) => setOrderForm({...orderForm, notes: e.target.value})}
                  onPaymentMethodChange={(method) => setOrderForm({...orderForm, paymentMethod: method})}
                  onPlaceOrder={handlePlaceOrder}
                  onAddressAdded={handleAddressAdded}
                  disabled={cart.length === 0 || !user}
                  // Schedule props
                  scheduleEnabled={scheduleEnabled}
                  scheduledFor={scheduledFor}
                  onScheduleEnabledChange={setScheduleEnabled}
                  onScheduledForChange={setScheduledFor}
                />
              )}
            </div>
          </div>
        ) : activeTab === 'favorites' ? (
          <FavoritesList
            favorites={products.filter(p => isFavorite(p.id))}
            onAddToCart={addToCart}
            onToggleFavorite={handleToggleFavorite}
            favoriteIds={favorites}
            isAuthenticated={!!user}
          />
        ) : (
          !isAdminView && <MyOrders user={user} toast={toast} />
        )}
      </ClientLayout>

      {/* Login Modal */}
      {showLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">Iniciar Sesión</h3>
            <div className="space-y-4">
              <input
                type="email"
                placeholder="Email"
                value={loginData.email}
                onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
              <input
                type="password"
                placeholder="Contraseña"
                value={loginData.password}
                onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleLogin}
                className="flex-1 bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors"
              >
                Iniciar Sesión
              </button>
              <button
                onClick={() => {setShowLogin(false); setShowRegister(true);}}
                className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Registrarse
              </button>
            </div>
            <button
              onClick={() => setShowLogin(false)}
              className="mt-4 text-gray-500 hover:text-gray-700 text-sm"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      {/* Botón discreto para ir a vista admin - Solo visible si no es vista de admin */}
      {!isAdminView && switchToAdmin && (
        <button
          onClick={switchToAdmin}
          className="fixed bottom-4 right-4 bg-gray-600 hover:bg-gray-700 text-white text-xs px-3 py-2 rounded-lg shadow-md transition-all duration-300 opacity-50 hover:opacity-100 z-40"
          title="Panel de Administración"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
            <line x1="8" y1="21" x2="16" y2="21"></line>
            <line x1="12" y1="17" x2="12" y2="21"></line>
          </svg>
        </button>
      )}

      {/* Register Modal */}
      {showRegister && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold mb-4">Registrarse</h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Nombre"
                value={registerData.name}
                onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
              <input
                type="email"
                placeholder="Email"
                value={registerData.email}
                onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
              <input
                type="password"
                placeholder="Contraseña"
                value={registerData.password}
                onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
              <input
                type="tel"
                placeholder="Teléfono (opcional)"
                value={registerData.phone}
                onChange={(e) => setRegisterData({...registerData, phone: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded-lg"
              />
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={handleRegister}
                className="flex-1 bg-orange-500 text-white py-2 rounded-lg hover:bg-orange-600 transition-colors"
              >
                Registrarse
              </button>
              <button
                onClick={() => {setShowRegister(false); setShowLogin(true);}}
                className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-400 transition-colors"
              >
                Iniciar Sesión
              </button>
            </div>
            <button
              onClick={() => setShowRegister(false)}
              className="mt-4 text-gray-500 hover:text-gray-700 text-sm"
            >
              Cancelar
            </button>

          </div>
        </div>
      )}
    </>
  );
};

export default ClientPage;
