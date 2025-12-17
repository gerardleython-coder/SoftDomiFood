import React, { useState } from 'react';
import { Trash2, Tag, X } from 'lucide-react';
import { couponsAPI } from '../../utils/api';

const Cart = ({ cart, onUpdateQuantity, onRemoveFromCart, totalPrice, onCouponApplied, appliedCoupon, toast, onClose }) => {
  const [couponCode, setCouponCode] = useState('');
  const [isValidatingCoupon, setIsValidatingCoupon] = useState(false);

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) {
      toast?.error('Por favor ingresa un código de cupón');
      return;
    }

    setIsValidatingCoupon(true);
    try {
      const response = await couponsAPI.validate(couponCode.toUpperCase().trim());

      if (response.valid) {
        const couponData = {
          code: couponCode.toUpperCase().trim(),
          discountType: response.coupon.discount_type || response.coupon.discountType,
          amount: response.coupon.amount,
          percentage: response.coupon.percentage,
        };

        onCouponApplied(couponData);
        toast?.success(`¡Cupón aplicado! ${couponData.discountType === 'PERCENTAGE' ? `${couponData.percentage}% de descuento` : `$${couponData.amount} de descuento`}`);
        setCouponCode('');
      } else {
        toast?.error(response.message || 'Cupón inválido');
      }
    } catch (error) {
      console.error('Error validating coupon:', error);
      const errorMessage = error.response?.data?.detail || error.response?.data?.message || 'Error al validar el cupón';
      toast?.error(errorMessage);
    } finally {
      setIsValidatingCoupon(false);
    }
  };

  const handleRemoveCoupon = () => {
    onCouponApplied(null);
    toast?.info('Cupón removido');
  };

  const calculateDiscount = () => {
    if (!appliedCoupon) return 0;

    if (appliedCoupon.discountType === 'PERCENTAGE') {
      return (totalPrice * appliedCoupon.percentage) / 100;
    } else {
      return Math.min(appliedCoupon.amount, totalPrice);
    }
  };

  const discount = calculateDiscount();
  const finalTotal = Math.max(totalPrice - discount, 0);

  if (cart.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-800">Carrito</h3>
          {onClose && (
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
              title="Cerrar carrito"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
        <p className="text-gray-500 text-center py-8">Tu carrito está vacío</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 sticky top-24">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-gray-800">Carrito</h3>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
            title="Cerrar carrito"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
        {cart.map(item => (
          <div key={item.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex-1">
              <h4 className="font-medium text-gray-800">{item.name}</h4>
              <p className="text-sm text-gray-600">${item.price} x {item.quantity}</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity - 1)}
                className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
              >
                -
              </button>
              <span className="w-8 text-center">{item.quantity}</span>
              <button
                onClick={() => onUpdateQuantity(item.id, item.quantity + 1)}
                className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300"
              >
                +
              </button>
              <button
                onClick={() => onRemoveFromCart(item.id)}
                className="ml-2 text-red-500 hover:text-red-700"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Sección de cupón */}
      <div className="border-t pt-4 mb-4">
        <div className="flex items-center mb-2">
          <Tag className="w-4 h-4 text-orange-600 mr-2" />
          <span className="text-sm font-medium text-gray-700">¿Tienes un cupón?</span>
        </div>

        {appliedCoupon ? (
          <div className="flex items-center justify-between bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center">
              <Tag className="w-4 h-4 text-green-600 mr-2" />
              <div>
                <p className="text-sm font-semibold text-green-800">{appliedCoupon.code}</p>
                <p className="text-xs text-green-600">
                  {appliedCoupon.discountType === 'PERCENTAGE'
                    ? `${appliedCoupon.percentage}% de descuento`
                    : `$${appliedCoupon.amount} de descuento`}
                </p>
              </div>
            </div>
            <button
              onClick={handleRemoveCoupon}
              className="text-green-600 hover:text-green-800"
              title="Remover cupón"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <div className="flex space-x-2">
            <input
              type="text"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleApplyCoupon()}
              placeholder="Código de cupón"
              className="flex-1 p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm uppercase"
              disabled={isValidatingCoupon}
            />
            <button
              onClick={handleApplyCoupon}
              disabled={isValidatingCoupon || !couponCode.trim()}
              className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed text-sm font-medium"
            >
              {isValidatingCoupon ? 'Validando...' : 'Aplicar'}
            </button>
          </div>
        )}
      </div>

      <div className="border-t pt-4">
        <div className="space-y-2">
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-600">Subtotal:</span>
            <span className="text-gray-800">${totalPrice.toFixed(2)}</span>
          </div>

          {appliedCoupon && discount > 0 && (
            <div className="flex justify-between items-center text-sm">
              <span className="text-green-600">Descuento:</span>
              <span className="text-green-600">-${discount.toFixed(2)}</span>
            </div>
          )}

          <div className="flex justify-between items-center pt-2 border-t">
            <span className="text-lg font-semibold text-gray-800">Total:</span>
            <span className="text-2xl font-bold text-orange-600">${finalTotal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
