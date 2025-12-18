import React, { useState, useEffect } from 'react';
import { User, MapPin, Mail, Phone, Calendar, ChevronDown, ChevronUp } from 'lucide-react';

const CustomerManagement = ({ customers, loading }) => {
  const [expandedCustomers, setExpandedCustomers] = useState(new Set());

  const toggleCustomer = (customerId) => {
    const newExpanded = new Set(expandedCustomers);
    if (newExpanded.has(customerId)) {
      newExpanded.delete(customerId);
    } else {
      newExpanded.add(customerId);
    }
    setExpandedCustomers(newExpanded);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
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

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Cargando clientes...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
          <User className="w-6 h-6 text-blue-600" />
          Gestión de Clientes
        </h2>
        <span className="text-sm text-gray-500 bg-gray-100 px-3 py-1 rounded-full">
          {customers?.length || 0} {customers?.length === 1 ? 'cliente' : 'clientes'}
        </span>
      </div>

      {!customers || customers.length === 0 ? (
        <div className="text-center py-12">
          <User className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 text-lg">No hay clientes registrados aún</p>
        </div>
      ) : (
        <div className="space-y-4">
          {customers.map((customer) => {
            const isExpanded = expandedCustomers.has(customer.id);
            const addresses = customer.addresses || [];

            return (
              <div
                key={customer.id}
                className="border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
              >
                {/* Customer Header */}
                <div
                  className="p-4 cursor-pointer flex items-center justify-between"
                  onClick={() => toggleCustomer(customer.id)}
                >
                  <div className="flex items-center space-x-4 flex-1">
                    <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                      <User className="w-6 h-6 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-800">
                        {customer.name || 'Sin nombre'}
                      </h3>
                      <div className="flex flex-wrap items-center gap-4 mt-1 text-sm text-gray-600">
                        <span className="flex items-center gap-1">
                          <Mail className="w-4 h-4" />
                          {customer.email}
                        </span>
                        {customer.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            {customer.phone}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          Registrado: {formatDate(customer.createdAt)}
                        </span>
                        <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                          {addresses.length} {addresses.length === 1 ? 'dirección' : 'direcciones'}
                        </span>
                      </div>
                    </div>
                  </div>
                  <button className="ml-4 p-2 hover:bg-gray-100 rounded-lg transition-colors">
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-600" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-600" />
                    )}
                  </button>
                </div>

                {/* Expanded Content - Addresses */}
                {isExpanded && (
                  <div className="border-t border-gray-200 bg-gray-50 p-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      Direcciones de Entrega
                    </h4>
                    {addresses.length === 0 ? (
                      <p className="text-gray-500 text-sm italic">Este cliente no tiene direcciones registradas</p>
                    ) : (
                      <div className="space-y-3">
                        {addresses.map((address) => (
                          <div
                            key={address.id}
                            className={`bg-white rounded-lg p-4 border-2 ${
                              address.isDefault
                                ? 'border-blue-500 bg-blue-50'
                                : 'border-gray-200'
                            }`}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                {address.isDefault && (
                                  <span className="inline-block bg-blue-500 text-white text-xs font-semibold px-2 py-1 rounded mb-2">
                                    Dirección Principal
                                  </span>
                                )}
                                <div className="mt-2 space-y-1 text-sm">
                                  <p className="font-semibold text-gray-800">
                                    {address.street}
                                  </p>
                                  <p className="text-gray-600">
                                    {address.city}, {address.state}
                                  </p>
                                  <p className="text-gray-600">
                                    Código Postal: {address.zipCode}
                                  </p>
                                  <p className="text-gray-600">
                                    {address.country}
                                  </p>
                                  {address.instructions && (
                                    <div className="mt-2 pt-2 border-t border-gray-200">
                                      <p className="text-xs text-gray-500 font-medium mb-1">
                                        Instrucciones adicionales:
                                      </p>
                                      <p className="text-sm text-gray-700 italic">
                                        {address.instructions}
                                      </p>
                                    </div>
                                  )}
                                  <p className="text-xs text-gray-400 mt-2">
                                    Creada: {formatDate(address.createdAt)}
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default CustomerManagement;
