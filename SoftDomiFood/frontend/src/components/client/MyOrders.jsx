import React, { useState, useEffect } from 'react';
import { Clock, Package, CheckCircle, X, CalendarClock, MapPin, DollarSign, CreditCard, Star } from 'lucide-react';
import { ordersAPI } from '../../utils/api';
import ReviewModal from './ReviewModal';

const MyOrders = ({ user, toast }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewModalOpen, setReviewModalOpen] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);

  useEffect(() => {
    if (!user) return;
    // Evitar auto-refresh mientras el modal de reseña está abierto
    loadOrders();
    let intervalId = null;
    if (!reviewModalOpen) {
      intervalId = setInterval(loadOrders, 10000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [user, reviewModalOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadOrders = async () => {
    if (!user) return;

    try {
      setLoading(true);
      const data = await ordersAPI.getAll();
      const ordersList = data.orders || data || [];
      setOrders(ordersList);
    } catch (error) {
      console.error('Error loading orders:', error);
      toast?.error?.('Error al cargar tus pedidos');
      setOrders([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const s = status?.toLowerCase();
    switch (s) {
      case 'scheduled': return 'bg-blue-100 text-blue-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-blue-100 text-blue-800';
      case 'preparing': return 'bg-blue-100 text-blue-800';
      case 'ready': return 'bg-green-100 text-green-800';
      case 'on_delivery': return 'bg-purple-100 text-purple-800';
      case 'delivered': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    const s = status?.toLowerCase();
    switch (s) {
      case 'scheduled': return <CalendarClock className="w-4 h-4" />;
      case 'pending': return <Clock className="w-4 h-4" />;
      case 'confirmed': return <Clock className="w-4 h-4" />;
      case 'preparing': return <Package className="w-4 h-4" />;
      case 'ready': return <CheckCircle className="w-4 h-4" />;
      case 'on_delivery': return <Package className="w-4 h-4" />;
      case 'delivered': return <CheckCircle className="w-4 h-4" />;
      case 'cancelled': return <X className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const getStatusText = (status) => {
    const s = status?.toLowerCase();
    const map = {
      scheduled: 'Programado',
      pending: 'Pendiente',
      confirmed: 'Confirmado',
      preparing: 'En Preparación',
      ready: 'Listo',
      on_delivery: 'En Camino',
      delivered: 'Entregado',
      cancelled: 'Cancelado',
    };
    return map[s] || status;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    // El backend guarda en UTC sin timezone, agregamos 'Z' para que JavaScript lo interprete como UTC
    const dateWithTz = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const date = new Date(dateWithTz);
    return date.toLocaleString('es-CO', {
      timeZone: 'America/Bogota',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleReviewClick = (item) => {
    setSelectedProduct({
      id: item.product_id || item.productId,
      name: item.product_name || item.productName,
      category: item.product_category || item.productCategory,
      image: item.product_image || null,
    });
    setReviewModalOpen(true);
  };

  const handleReviewSubmitted = () => {
    toast?.success?.('¡Gracias por tu reseña!');
    loadOrders(); // Recargar pedidos
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando tus pedidos...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Mis Pedidos</h2>
        <button
          onClick={loadOrders}
          className="text-sm text-orange-600 hover:text-orange-700 font-medium"
        >
          Actualizar
        </button>
      </div>

      {orders.length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No tienes pedidos aún</p>
          <p className="text-gray-400 text-sm mt-2">Realiza tu primer pedido desde el menú</p>
        </div>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const status = (order.status || 'PENDING').toLowerCase();
            const items = order.items || [];

            return (
              <div
                key={order.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">
                      Pedido #{order.id.substring(0, 8)}
                    </h3>

                    <p className="text-sm text-gray-600 mt-1">
                      Fecha: {formatDate(order.createdAt)}
                    </p>

                    {/* ✅ Programado para */}
                    {order.scheduledFor && (
                      <p className="text-sm text-blue-700 mt-1 flex items-center gap-1">
                        <CalendarClock className="w-4 h-4" />
                        Programado para: {formatDate(order.scheduledFor)}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(status)}`}
                    >
                      {getStatusIcon(status)}
                      <span className="ml-1">{getStatusText(status)}</span>
                    </span>

                    {order.paymentMethod && (
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          order.paymentMethod === 'CARD'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {order.paymentMethod === 'CARD' ? (
                          <CreditCard className="w-3 h-3 mr-1" />
                        ) : (
                          <DollarSign className="w-3 h-3 mr-1" />
                        )}
                        {order.paymentMethod === 'CARD' ? 'Tarjeta' : 'Efectivo'}
                      </span>
                    )}
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-sm font-medium text-gray-700 mb-2">Productos:</p>
                  <div className="text-sm text-gray-600 space-y-2">
                    {items.length > 0 ? (
                      items.map((item, index) => (
                        <div key={index} className="flex justify-between items-center pl-4 py-1">
                          <div className="flex-1">
                            <span>
                              {item.quantity}x {item.product_name || item.productName || 'Producto'}
                            </span>
                          </div>
                          <div className="flex items-center gap-3">
                            <span className="font-medium">
                              ${((item.price || 0) * (item.quantity || 0)).toFixed(2)}
                            </span>
                            {/* Botón Calificar solo si el pedido está DELIVERED */}
                            {status === 'delivered' && (
                              <button
                                onClick={() => handleReviewClick(item)}
                                className="flex items-center gap-1 px-3 py-1 text-xs font-medium text-orange-600 hover:text-orange-700 hover:bg-orange-50 rounded-lg transition-colors"
                              >
                                <Star className="w-3.5 h-3.5" />
                                Calificar
                              </button>
                            )}
                          </div>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 pl-4">No hay productos en este pedido</p>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-gray-200">
                  <div className="flex items-center text-sm text-gray-600 mb-3">
                    <MapPin className="w-4 h-4 mr-1" />
                    <span>Dirección de entrega registrada</span>
                  </div>

                  <div className="space-y-2">
                    {order.coupon_code && order.discount_applied > 0 ? (
                      <>
                        <div className="flex justify-between text-sm text-gray-600">
                          <span>Subtotal:</span>
                          <span>
                            ${(
                              (parseFloat(order.total) || 0) + (parseFloat(order.discount_applied) || 0)
                            ).toFixed(2)}
                          </span>
                        </div>
                        <div className="flex justify-between text-sm text-green-600 font-medium">
                          <span>Cupón aplicado ({order.coupon_code}):</span>
                          <span>-${(parseFloat(order.discount_applied) || 0).toFixed(2)}</span>
                        </div>
                        <div className="flex justify-between font-bold text-lg text-gray-800 pt-2 border-t border-gray-200">
                          <span>Total:</span>
                          <span>${(parseFloat(order.total) || 0).toFixed(2)}</span>
                        </div>
                      </>
                    ) : (
                      <div className="flex justify-between font-bold text-lg text-gray-800">
                        <span>Total:</span>
                        <span>${(parseFloat(order.total) || 0).toFixed(2)}</span>
                      </div>
                    )}
                  </div>
                </div>

                {order.notes && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Notas:</span> {order.notes}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Modal de Reseña */}
      {selectedProduct && (
        <ReviewModal
          isOpen={reviewModalOpen}
          onClose={() => {
            setReviewModalOpen(false);
            setSelectedProduct(null);
          }}
          product={selectedProduct}
          onReviewSubmitted={handleReviewSubmitted}
        />
      )}
    </div>
  );
};

export default MyOrders;
