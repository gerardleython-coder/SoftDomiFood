import React, { useMemo, useState } from 'react';
import {
  MapPin,
  Clock,
  Package,
  CheckCircle,
  X,
  User,
  CreditCard,
  DollarSign,
  CalendarClock
} from 'lucide-react';

const OrderManagement = ({ orders = [], onStatusChange }) => {
  const [statusFilter, setStatusFilter] = useState('ALL');

  const normalizeStatus = (s) => String(s || 'PENDING').toUpperCase();

  const formatDateTime = (dateString) => {
    if (!dateString) return 'N/A';
    // El backend guarda en UTC sin timezone, agregamos 'Z' para que JavaScript lo interprete como UTC
    const dateWithTz = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const d = new Date(dateWithTz);
    if (isNaN(d.getTime())) return 'N/A';
    return d.toLocaleString('es-CO', {
      timeZone: 'America/Bogota',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status) => {
    const statusLower = String(status || '').toLowerCase();
    switch (statusLower) {
      case 'scheduled': return 'bg-gray-100 text-gray-800';
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
    const statusLower = String(status || '').toLowerCase();
    switch (statusLower) {
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

  const getPaymentIcon = (method) => {
    switch (String(method || 'CASH').toUpperCase()) {
      case 'CARD': return <CreditCard className="w-4 h-4" />;
      case 'CASH': return <DollarSign className="w-4 h-4" />;
      default: return <DollarSign className="w-4 h-4" />;
    }
  };

  const getPaymentColor = (method) => {
    switch (String(method || 'CASH').toUpperCase()) {
      case 'CARD': return 'bg-blue-100 text-blue-800';
      case 'CASH': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const statusLabel = (status) => {
    const s = normalizeStatus(status);
    const map = {
      ALL: 'Todos',
      SCHEDULED: 'Programado',
      PENDING: 'Pendiente',
      CONFIRMED: 'Confirmado',
      PREPARING: 'Preparando',
      READY: 'Listo',
      ON_DELIVERY: 'En camino',
      DELIVERED: 'Entregado',
      CANCELLED: 'Cancelado'
    };
    return map[s] || s;
  };

  const allStatuses = useMemo(() => {
    const set = new Set(orders.map(o => normalizeStatus(o.status)).filter(Boolean));
    return ['ALL', ...Array.from(set)];
  }, [orders]);

  const filteredOrders = useMemo(() => {
    if (statusFilter === 'ALL') return orders;
    return orders.filter(o => normalizeStatus(o.status) === statusFilter);
  }, [orders, statusFilter]);

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Pedidos Recientes</h2>

        <div className="flex space-x-2">
          <select
            className="p-2 border border-gray-300 rounded-lg text-sm"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
          >
            {allStatuses.map((s) => (
              <option key={s} value={s}>
                {s === 'ALL' ? 'Todos los estados' : statusLabel(s)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filteredOrders.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay pedidos registrados</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredOrders.map(order => {
            const orderDate = order.createdAt ? new Date(order.createdAt).toLocaleDateString('es-ES') : 'N/A';
            const customerName = order.customer_name || 'Cliente';
            const customerPhone = order.customer_phone || 'N/A';
            const customerEmail = order.customer_email || 'N/A';
            const address = order.delivery_street
              ? `${order.delivery_street}, ${order.delivery_city}, ${order.delivery_state}`
              : 'Dirección no disponible';

            const items = order.items || [];
            const statusUpper = normalizeStatus(order.status);
            const statusLower = statusUpper.toLowerCase();

            // ✅ soporta camelCase y snake_case por si acaso
            const scheduledFor = order.scheduledFor || order.scheduled_for;

            const isScheduled = statusUpper === 'SCHEDULED';

            return (
              <div key={order.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-semibold text-gray-800">Pedido #{String(order.id).substring(0, 8)}</h3>

                    <div className="flex items-center space-x-4 mt-1 flex-wrap">
                      <div className="flex items-center space-x-1">
                        <User className="w-4 h-4 text-gray-500" />
                        <span className="text-sm text-gray-600">{customerName}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-600">Tel: {customerPhone}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-sm text-gray-600">Email: {customerEmail}</span>
                      </div>
                    </div>

                    <p className="text-sm text-gray-600">Fecha: {orderDate}</p>

                    {/* ✅ NUEVO: Mensaje con fecha de despacho programado */}
                    {isScheduled && scheduledFor && (
                      <div className="mt-2 inline-flex items-center gap-2 text-sm text-blue-700 bg-blue-50 px-3 py-1 rounded-lg">
                        <CalendarClock className="w-4 h-4" />
                        <span>
                          Despacho programado para: <b>{formatDateTime(scheduledFor)}</b>
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPaymentColor(order.paymentMethod || 'CASH')}`}>
                      {getPaymentIcon(order.paymentMethod || 'CASH')}
                      <span className="ml-1">{(String(order.paymentMethod || 'CASH').toUpperCase()) === 'CARD' ? 'Tarjeta' : 'Efectivo'}</span>
                    </span>

                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(statusLower)}`}>
                      {getStatusIcon(statusLower)}
                      <span className="ml-1">{statusLabel(statusUpper)}</span>
                    </span>
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-sm text-gray-600 mb-2">Productos:</p>
                  <div className="text-sm text-gray-700 space-y-1">
                    {items.length > 0 ? (
                      items.map((item, index) => (
                        <div key={index} className="flex justify-between pl-4">
                          <span>{item.quantity}x {item.product_name || item.productName || 'Producto'}</span>
                          <span>${((item.price || 0) * (item.quantity || 0)).toFixed(2)}</span>
                        </div>
                      ))
                    ) : (
                      <p className="text-gray-500 pl-4">No hay productos en este pedido</p>
                    )}
                  </div>
                </div>

                <div className="mb-3">
                  <p className="text-sm text-gray-600 mb-1">
                    <MapPin className="inline w-4 h-4 mr-1" />
                    {address}
                  </p>
                </div>

                {/* Desglose de precios con cupón si aplica */}
                <div className="space-y-1">
                  {order.coupon_code && order.discount_applied > 0 ? (
                    <>
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>Subtotal:</span>
                        <span>${((parseFloat(order.total) || 0) + (parseFloat(order.discount_applied) || 0)).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between text-sm text-green-600 font-medium">
                        <span>Cupón ({order.coupon_code}):</span>
                        <span>-${(parseFloat(order.discount_applied) || 0).toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between font-semibold text-gray-800 pt-1 border-t border-gray-200">
                        <span>Total:</span>
                        <span>${(parseFloat(order.total) || 0).toFixed(2)}</span>
                      </div>
                    </>
                  ) : (
                    <div className="flex justify-between font-semibold text-gray-800">
                      <span>Total:</span>
                      <span>${(parseFloat(order.total) || 0).toFixed(2)}</span>
                    </div>
                  )}
                </div>

                {/* ✅ Acciones del administrador */}
                <div className="flex space-x-2 mt-4">
                  {statusLower !== 'delivered' && statusLower !== 'cancelled' && (
                    <>
                      {/* PENDING: Mostrar botón Preparar (casos manuales/excepcionales) */}
                      {statusLower === 'pending' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'PREPARING')}
                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                        >
                          Preparar
                        </button>
                      )}

                      {/* CONFIRMED: Pedido validado, listo para preparar */}
                      {statusLower === 'confirmed' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'PREPARING')}
                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                        >
                          Preparar
                        </button>
                      )}

                      {/* SCHEDULED: Admin puede liberar manualmente cuando sea necesario */}
                      {statusLower === 'scheduled' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'PENDING')}
                          className="px-3 py-1 bg-blue-500 text-white text-sm rounded hover:bg-blue-600 transition-colors"
                        >
                          Liberar para preparar
                        </button>
                      )}

                      {/* PREPARING: Mostrar botón Listo */}
                      {statusLower === 'preparing' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'READY')}
                          className="px-3 py-1 bg-green-500 text-white text-sm rounded hover:bg-green-600 transition-colors"
                        >
                          Listo
                        </button>
                      )}

                      {/* READY: Mostrar botón Entregado */}
                      {statusLower === 'ready' && (
                        <button
                          onClick={() => onStatusChange(order.id, 'DELIVERED')}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition-colors"
                        >
                          Entregado
                        </button>
                      )}

                      {/* CANCELAR: Siempre disponible excepto para entregados/cancelados */}
                      <button
                        onClick={() => onStatusChange(order.id, 'CANCELLED')}
                        className="px-3 py-1 bg-red-500 text-white text-sm rounded hover:bg-red-600 transition-colors"
                      >
                        Cancelar
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default OrderManagement;
