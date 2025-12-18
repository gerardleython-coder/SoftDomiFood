import React, { useState } from 'react';
import { Ticket, Plus, Edit2, Trash2, X, Calendar, Percent, DollarSign } from 'lucide-react';

const CouponManagement = ({ coupons, onAddCoupon, onEditCoupon, onDeleteCoupon }) => {
  const [isAddingCoupon, setIsAddingCoupon] = useState(false);
  const [editingCoupon, setEditingCoupon] = useState(null);
  const [formData, setFormData] = useState({
    code: '',
    description: '',
    discountType: 'PERCENTAGE',
    amount: '',
    percentage: '',
    validFrom: '',
    validTo: '',
    maxUses: '',
    perUserLimit: '',
    isActive: true
  });

  const resetForm = () => {
    setFormData({
      code: '',
      description: '',
      discountType: 'PERCENTAGE',
      amount: '',
      percentage: '',
      validFrom: '',
      validTo: '',
      maxUses: '',
      perUserLimit: '',
      isActive: true
    });
    setIsAddingCoupon(false);
    setEditingCoupon(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Validaciones básicas
    if (!formData.code.trim()) {
      alert('El código del cupón es obligatorio');
      return;
    }

    if (formData.discountType === 'PERCENTAGE' && (!formData.percentage || formData.percentage <= 0 || formData.percentage > 100)) {
      alert('El porcentaje debe estar entre 1 y 100');
      return;
    }

    if (formData.discountType === 'AMOUNT' && (!formData.amount || formData.amount <= 0)) {
      alert('El monto debe ser mayor a 0');
      return;
    }

    // Preparar datos para enviar
    const couponData = {
      code: formData.code.toUpperCase().trim(),
      description: formData.description.trim() || null,
      discountType: formData.discountType,
      amount: formData.discountType === 'AMOUNT' ? parseFloat(formData.amount) : null,
      percentage: formData.discountType === 'PERCENTAGE' ? parseFloat(formData.percentage) : null,
      validFrom: formData.validFrom || null,
      validTo: formData.validTo || null,
      maxUses: formData.maxUses ? parseInt(formData.maxUses) : null,
      perUserLimit: formData.perUserLimit ? parseInt(formData.perUserLimit) : null,
      isActive: formData.isActive
    };

    let success = false;
    if (editingCoupon) {
      success = await onEditCoupon(editingCoupon.id, couponData);
    } else {
      success = await onAddCoupon(couponData);
    }

    if (success) {
      resetForm();
    }
  };

  const handleEdit = (coupon) => {
    setFormData({
      code: coupon.code || '',
      description: coupon.description || '',
      discountType: coupon.discount_type || coupon.discountType || 'PERCENTAGE',
      amount: coupon.amount || '',
      percentage: coupon.percentage || '',
      validFrom: coupon.valid_from?.substring(0, 16) || coupon.validFrom?.substring(0, 16) || '',
      validTo: coupon.valid_to?.substring(0, 16) || coupon.validTo?.substring(0, 16) || '',
      maxUses: coupon.max_uses || coupon.maxUses || '',
      perUserLimit: coupon.per_user_limit || coupon.perUserLimit || '',
      isActive: coupon.is_active !== undefined ? coupon.is_active : (coupon.isActive !== undefined ? coupon.isActive : true)
    });
    setEditingCoupon(coupon);
    setIsAddingCoupon(true);
  };

  const handleDelete = async (couponId) => {
    if (window.confirm('¿Estás seguro de que deseas eliminar este cupón?')) {
      await onDeleteCoupon(couponId);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Sin límite';
    try {
      const dateWithTz = dateString.endsWith('Z') ? dateString : dateString + 'Z';
      return new Date(dateWithTz).toLocaleDateString('es-ES', {
        timeZone: 'America/Bogota',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch {
      return dateString;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <Ticket className="w-6 h-6 text-purple-600" />
          <h2 className="text-2xl font-bold text-gray-800">Gestión de Cupones</h2>
        </div>
        {!isAddingCoupon && (
          <button
            onClick={() => setIsAddingCoupon(true)}
            className="flex items-center space-x-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Crear Cupón</span>
          </button>
        )}
      </div>

      {/* Formulario de Crear/Editar Cupón */}
      {isAddingCoupon && (
        <div className="mb-6 bg-purple-50 p-6 rounded-lg border-2 border-purple-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">
              {editingCoupon ? 'Editar Cupón' : 'Nuevo Cupón'}
            </h3>
            <button
              onClick={resetForm}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Código */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Código del Cupón *
                </label>
                <input
                  type="text"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="DESC20"
                  required
                />
              </div>

              {/* Tipo de Descuento */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Tipo de Descuento *
                </label>
                <select
                  value={formData.discountType}
                  onChange={(e) => setFormData({ ...formData, discountType: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="PERCENTAGE">Porcentaje (%)</option>
                  <option value="AMOUNT">Monto Fijo ($)</option>
                </select>
              </div>

              {/* Valor del Descuento */}
              {formData.discountType === 'PERCENTAGE' ? (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Porcentaje de Descuento *
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={formData.percentage}
                      onChange={(e) => setFormData({ ...formData, percentage: e.target.value })}
                      className="w-full p-2 pl-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="15"
                      min="1"
                      max="100"
                      required
                    />
                    <Percent className="w-4 h-4 text-gray-400 absolute left-2 top-3" />
                  </div>
                </div>
              ) : (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Monto de Descuento *
                  </label>
                  <div className="relative">
                    <input
                      type="number"
                      value={formData.amount}
                      onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                      className="w-full p-2 pl-8 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      placeholder="5000"
                      min="1"
                      step="0.01"
                      required
                    />
                    <DollarSign className="w-4 h-4 text-gray-400 absolute left-2 top-3" />
                  </div>
                </div>
              )}

              {/* Descripción */}
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descripción
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Descuento especial para nuevos clientes"
                  rows="2"
                />
              </div>

              {/* Fecha Inicio */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Válido Desde
                </label>
                <input
                  type="datetime-local"
                  value={formData.validFrom}
                  onChange={(e) => setFormData({ ...formData, validFrom: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Fecha Fin */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Válido Hasta
                </label>
                <input
                  type="datetime-local"
                  value={formData.validTo}
                  onChange={(e) => setFormData({ ...formData, validTo: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              {/* Usos Máximos */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Usos Máximos Totales
                </label>
                <input
                  type="number"
                  value={formData.maxUses}
                  onChange={(e) => setFormData({ ...formData, maxUses: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Ilimitado"
                  min="1"
                />
              </div>

              {/* Límite por Usuario */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Usos por Usuario
                </label>
                <input
                  type="number"
                  value={formData.perUserLimit}
                  onChange={(e) => setFormData({ ...formData, perUserLimit: e.target.value })}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Ilimitado"
                  min="1"
                />
              </div>

              {/* Estado Activo */}
              <div className="md:col-span-2 flex items-center">
                <input
                  type="checkbox"
                  id="isActive"
                  checked={formData.isActive}
                  onChange={(e) => setFormData({ ...formData, isActive: e.target.checked })}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
                <label htmlFor="isActive" className="ml-2 text-sm font-medium text-gray-700">
                  Cupón Activo
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3 mt-4">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                {editingCoupon ? 'Actualizar' : 'Crear'} Cupón
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Cupones */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Código
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Descuento
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Vigencia
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Límites
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {coupons.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  No hay cupones creados. Crea uno para comenzar.
                </td>
              </tr>
            ) : (
              coupons.map((coupon) => {
                const discountType = coupon.discount_type || coupon.discountType;
                const isActive = coupon.is_active !== undefined ? coupon.is_active : coupon.isActive;

                return (
                  <tr key={coupon.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <div className="flex items-center">
                        <Ticket className="w-4 h-4 text-purple-600 mr-2" />
                        <div>
                          <div className="text-sm font-semibold text-gray-900">{coupon.code}</div>
                          {coupon.description && (
                            <div className="text-xs text-gray-500">{coupon.description}</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm text-gray-900">
                        {discountType === 'PERCENTAGE' ? (
                          <span className="flex items-center">
                            <Percent className="w-3 h-3 mr-1" />
                            {coupon.percentage}%
                          </span>
                        ) : (
                          <span className="flex items-center">
                            <DollarSign className="w-3 h-3 mr-1" />
                            ${coupon.amount}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-xs text-gray-600">
                        <div className="flex items-center">
                          <Calendar className="w-3 h-3 mr-1" />
                          {formatDate(coupon.valid_from || coupon.validFrom)}
                        </div>
                        <div className="flex items-center mt-1">
                          <Calendar className="w-3 h-3 mr-1" />
                          {formatDate(coupon.valid_to || coupon.validTo)}
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4 text-xs text-gray-600">
                      <div>Total: {coupon.max_uses || coupon.maxUses || '∞'}</div>
                      <div>Usuario: {coupon.per_user_limit || coupon.perUserLimit || '∞'}</div>
                    </td>
                    <td className="px-4 py-4">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                        isActive
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {isActive ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(coupon)}
                          className="text-blue-600 hover:text-blue-800 transition-colors"
                          title="Editar"
                        >
                          <Edit2 className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(coupon.id)}
                          className="text-red-600 hover:text-red-800 transition-colors"
                          title="Eliminar"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default CouponManagement;
