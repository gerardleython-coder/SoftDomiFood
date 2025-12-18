import React, { useState, useEffect } from 'react';
import AdminLayout from '../components/admin/AdminLayout';
import OrderManagement from '../components/admin/OrderManagement';
import ProductManagement from '../components/admin/ProductManagement';
import CustomerManagement from '../components/admin/CustomerManagement';
import CouponManagement from '../components/admin/CouponManagement';
import ReviewsManagement from '../components/admin/ReviewsManagement';
import StatsCard from '../components/admin/StatsCard';
import { adminAPI, productsAPI } from '../utils/api';
import { Package2, DollarSign, Edit, User, Ticket, MessageSquare } from 'lucide-react';

const AdminPage = ({ switchToClient, adminUser, onLogout, toast }) => {
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [coupons, setCoupons] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState({ todayOrders: 0, todayRevenue: 0 });
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('orders'); // 'orders', 'products', 'customers', 'coupons', 'reviews'

  // Load real data from API
  useEffect(() => {
    loadData();

    // Actualizar datos cada 5 segundos para mantener estadísticas actualizadas
    const interval = setInterval(() => {
      loadOrders(); // Recargar pedidos actualiza las estadísticas
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      await Promise.all([loadProducts(), loadOrders(), loadCustomers(), loadCoupons(), loadReviews()]);
    } catch (error) {
      console.error('Error loading admin data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCustomers = async () => {
    try {
      const data = await adminAPI.getAllCustomers();
      const customersList = data.customers || data || [];
      setCustomers(customersList);
    } catch (error) {
      console.error('Error loading customers:', error);
      setCustomers([]);
    }
  };

  const loadCoupons = async () => {
    try {
      const data = await adminAPI.coupons.getAll();
      const couponsList = data.coupons || data || [];
      setCoupons(couponsList);
    } catch (error) {
      console.error('Error loading coupons:', error);
      setCoupons([]);
    }
  };

  const loadReviews = async () => {
    try {
      const data = await adminAPI.reviews.getAll();
      const reviewsList = data.reviews || data || [];
      setReviews(reviewsList);
    } catch (error) {
      console.error('Error loading reviews:', error);
      setReviews([]);
    }
  };

  const loadProducts = async () => {
    try {
      const data = await productsAPI.getAll();
      setProducts(data.products || data || []);
    } catch (error) {
      console.error('Error loading products:', error);
      setProducts([]);
    }
  };

  const loadOrders = async () => {
    try {
      const data = await adminAPI.getAllOrders();
      const ordersList = data.orders || data || [];
      setOrders(ordersList);
      calculateStats(ordersList);
    } catch (error) {
      console.error('Error loading orders:', error);
      setOrders([]);
    }
  };

  const calculateStats = (ordersList) => {
    if (!ordersList || ordersList.length === 0) {
      setStats({ todayOrders: 0, todayRevenue: 0 });
      return;
    }

    // Obtener fecha actual en Colombia (UTC-5)
    const nowUTC = new Date();
    const nowColombia = new Date(nowUTC.toLocaleString('en-US', { timeZone: 'America/Bogota' }));
    const todayColombia = new Date(nowColombia.getFullYear(), nowColombia.getMonth(), nowColombia.getDate());

    console.log('Today Colombia:', todayColombia.toISOString());

    // Filtrar solo pedidos del día actual y que no estén cancelados
    const todayOrders = ordersList.filter(order => {
      if (!order.createdAt) {
        console.warn('Order without createdAt:', order.id);
        return false;
      }

      try {
        // El backend guarda en UTC sin timezone, agregamos 'Z' para que JavaScript lo interprete como UTC
        const createdAtString = typeof order.createdAt === 'string' ? order.createdAt : order.createdAt.toString();
        const dateWithTz = createdAtString.endsWith('Z') ? createdAtString : createdAtString + 'Z';
        const orderDate = new Date(dateWithTz);

        // Verificar que la fecha sea válida
        if (isNaN(orderDate.getTime())) {
          console.warn('Invalid date:', order.createdAt);
          return false;
        }

        // Convertir fecha del pedido a zona horaria de Colombia
        const orderDateColombia = new Date(orderDate.toLocaleString('en-US', { timeZone: 'America/Bogota' }));
        const orderDateOnly = new Date(orderDateColombia.getFullYear(), orderDateColombia.getMonth(), orderDateColombia.getDate());

        const isToday = orderDateOnly.getTime() === todayColombia.getTime();
        const isNotCancelled = order.status?.toLowerCase() !== 'cancelled';

        console.log('Order:', order.id.substring(0, 8), 'Created:', orderDateOnly.toISOString(), 'IsToday:', isToday, 'Status:', order.status);

        return isToday && isNotCancelled;
      } catch (error) {
        console.error('Error processing order date:', error, order);
        return false;
      }
    });

    // Calcular ingresos solo de pedidos no cancelados del día
    const todayRevenue = todayOrders.reduce((sum, order) => {
      const total = parseFloat(order.total) || 0;
      return sum + total;
    }, 0);

    console.log('Stats calculated:', {
      totalOrders: ordersList.length,
      todayOrders: todayOrders.length,
      todayRevenue: todayRevenue,
      filteredOrders: todayOrders.map(o => ({ id: o.id.substring(0, 8), total: o.total, status: o.status }))
    });

    setStats({
      todayOrders: todayOrders.length,
      todayRevenue: todayRevenue
    });
  };

  const handleAdminOrderStatus = async (orderId, newStatus) => {
    try {
      await adminAPI.updateOrderStatus(orderId, newStatus);
      // Recargar pedidos después de actualizar
      await loadOrders();
      toast.success('Estado del pedido actualizado correctamente');
    } catch (error) {
      console.error('Error updating order status:', error);
      const errorMessage = error.response?.data?.detail || 'Error al actualizar el estado del pedido';
      toast.error(errorMessage);
    }
  };

  const handleDeleteProduct = async (productId) => {
    // Nota: La API no tiene endpoint de delete, pero podemos marcarlo como no disponible
    try {
      await adminAPI.updateProduct(productId, { isAvailable: false });
      await loadProducts();
      toast.success('Producto deshabilitado correctamente');
    } catch (error) {
      console.error('Error deleting product:', error);
      toast.error('Error al deshabilitar el producto');
    }
  };

  const handleAddProduct = async (productData) => {
    try {
      await adminAPI.createProduct(productData);
      await loadProducts();
      toast.success('Producto agregado correctamente');
      return true;
    } catch (error) {
      console.error('Error adding product:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al agregar el producto';
      toast.error(errorMessage);
      return false;
    }
  };

  const handleEditProduct = async (productId, productData) => {
    try {
      await adminAPI.updateProduct(productId, productData);
      await loadProducts();
      toast.success('Producto actualizado correctamente');
      return true;
    } catch (error) {
      console.error('Error updating product:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar el producto';
      toast.error(errorMessage);
      return false;
    }
  };

  const handleAddCoupon = async (couponData) => {
    try {
      await adminAPI.coupons.create(couponData);
      await loadCoupons();
      toast.success('Cupón creado correctamente');
      return true;
    } catch (error) {
      console.error('Error adding coupon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al crear el cupón';
      toast.error(errorMessage);
      return false;
    }
  };

  const handleEditCoupon = async (couponId, couponData) => {
    try {
      await adminAPI.coupons.update(couponId, couponData);
      await loadCoupons();
      toast.success('Cupón actualizado correctamente');
      return true;
    } catch (error) {
      console.error('Error updating coupon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar el cupón';
      toast.error(errorMessage);
      return false;
    }
  };

  const handleDeleteCoupon = async (couponId) => {
    try {
      await adminAPI.coupons.delete(couponId);
      await loadCoupons();
      toast.success('Cupón eliminado correctamente');
      return true;
    } catch (error) {
      console.error('Error deleting coupon:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al eliminar el cupón';
      toast.error(errorMessage);
      return false;
    }
  };

  const handleDeleteReview = async (reviewId) => {
    try {
      await adminAPI.reviews.delete(reviewId);
      await loadReviews();
      toast.success('Reseña eliminada correctamente');
      return true;
    } catch (error) {
      console.error('Error deleting review:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Error al eliminar la reseña';
      toast.error(errorMessage);
      return false;
    }
  };

  if (loading) {
    return (
      <AdminLayout switchToClient={switchToClient} adminUser={adminUser} onLogout={onLogout}>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando datos...</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout switchToClient={switchToClient} adminUser={adminUser} onLogout={onLogout}>
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Panel de Control</h3>
            <nav className="space-y-2">
              <button
                onClick={() => setActiveView('orders')}
                className={`w-full flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  activeView === 'orders'
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Package2 className="w-4 h-4" />
                <span>Pedidos</span>
              </button>
              <button
                onClick={() => setActiveView('products')}
                className={`w-full flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  activeView === 'products'
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Edit className="w-4 h-4" />
                <span>Productos</span>
              </button>
              <button
                onClick={() => setActiveView('customers')}
                className={`w-full flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  activeView === 'customers'
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <User className="w-4 h-4" />
                <span>Clientes</span>
              </button>
              <button
                onClick={() => setActiveView('coupons')}
                className={`w-full flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  activeView === 'coupons'
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <Ticket className="w-4 h-4" />
                <span>Cupones</span>
              </button>
              <button
                onClick={() => setActiveView('reviews')}
                className={`w-full flex items-center space-x-2 p-2 rounded-lg transition-colors ${
                  activeView === 'reviews'
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <MessageSquare className="w-4 h-4" />
                <span>Reseñas</span>
              </button>
            </nav>
          </div>

          {/* Stats Cards */}
          <div className="mt-6 space-y-4">
            <StatsCard
              title="Pedidos Hoy"
              value={stats.todayOrders}
              icon={Package2}
              color="bg-blue-100"
            />
            <StatsCard
              title="Ingresos Hoy"
              value={`$${stats.todayRevenue.toFixed(2)}`}
              icon={DollarSign}
              color="bg-green-100"
            />
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-3">
          {activeView === 'orders' && (
            <OrderManagement
              orders={orders}
              onStatusChange={handleAdminOrderStatus}
            />
          )}

          {activeView === 'products' && (
            <ProductManagement
              products={products}
              onAddProduct={handleAddProduct}
              onEditProduct={handleEditProduct}
              onDeleteProduct={handleDeleteProduct}
            />
          )}

          {activeView === 'customers' && (
            <CustomerManagement
              customers={customers}
              loading={loading}
            />
          )}

          {activeView === 'coupons' && (
            <CouponManagement
              coupons={coupons}
              onAddCoupon={handleAddCoupon}
              onEditCoupon={handleEditCoupon}
              onDeleteCoupon={handleDeleteCoupon}
            />
          )}

          {activeView === 'reviews' && (
            <ReviewsManagement
              reviews={reviews}
              onDelete={handleDeleteReview}
              isLoading={loading}
            />
          )}
        </div>
      </div>
    </AdminLayout>
  );
};

export default AdminPage;
