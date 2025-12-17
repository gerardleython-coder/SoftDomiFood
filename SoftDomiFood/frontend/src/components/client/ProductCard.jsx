import React, { useState, useEffect } from 'react';
import { Plus, Heart, User, MessageSquare } from 'lucide-react';
import StarRating from '../common/StarRating';
import api from '../../utils/api';

const ProductCard = ({ product, onAddToCart, isFavorite, onToggleFavorite, isAuthenticated }) => {
  const [reviewsSummary, setReviewsSummary] = useState({ average: 0, total: 0, reviews: [] });
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [showReviews, setShowReviews] = useState(false);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        setLoadingReviews(true);
        const { data } = await api.get(`/products/${product.id}/reviews`);
        if (!mounted) return;
        setReviewsSummary({
          average: data?.average || 0,
          total: data?.total || 0,
          reviews: data?.reviews || [],
        });
      } catch (err) {
        if (mounted) setReviewsSummary({ average: 0, total: 0, reviews: [] });
      } finally {
        if (mounted) setLoadingReviews(false);
      }
    };
    load();
    return () => { mounted = false; };
  }, [product.id]);

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
      <div className="relative">
        <img
          src={product.image || 'https://placehold.co/300x200/FF6B6B/FFFFFF?text=Producto'}
          alt={product.name}
          className="w-full h-48 object-cover"
        />
        {isAuthenticated && (
          <button
            onClick={() => onToggleFavorite(product.id)}
            className={`absolute top-3 right-3 p-2 rounded-full transition-all ${
              isFavorite
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-white text-gray-400 hover:text-red-500 hover:bg-gray-50'
            }`}
            title={isFavorite ? 'Quitar de favoritos' : 'Agregar a favoritos'}
          >
            <Heart className={`w-5 h-5 ${isFavorite ? 'fill-current' : ''}`} />
          </button>
        )}
      </div>
      <div className="p-6">
        <div className="flex justify-between items-start mb-2">
          <h3 className="text-xl font-semibold text-gray-800">{product.name}</h3>
          <span className="text-2xl font-bold text-orange-600">${product.price}</span>
        </div>
        <p className="text-gray-600 mb-4">{product.description}</p>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">{product.category}</span>
          <button
            onClick={() => onAddToCart(product)}
            className="bg-orange-500 text-white px-4 py-2 rounded-lg hover:bg-orange-600 transition-colors flex items-center space-x-2"
          >
            <Plus className="w-4 h-4" />
            <span>Agregar</span>
          </button>
        </div>

        {/* Toggle reviews link */}
        {reviewsSummary.total > 0 && (
          <div className="mt-3 px-6">
            <button
              onClick={() => setShowReviews((s) => !s)}
              className="text-sm text-blue-600 hover:underline inline-flex items-center gap-2"
            >
              <MessageSquare className="w-4 h-4" />
              <span>{showReviews ? 'Ocultar reseñas' : 'Ver reseñas'}</span>
            </button>
          </div>
        )}

        {/* Condensed reviews summary shown when toggled */}
        {showReviews && reviewsSummary.total > 0 && (
          <div className="px-6 pb-6">
            <div className="bg-gray-50 rounded-lg p-3 mb-4">
              <div className="flex items-center gap-4">
                <div className="text-center flex-shrink-0">
                  <div className="text-2xl font-bold text-gray-900">{reviewsSummary.average.toFixed(1)}</div>
                  <div className="mt-1"><StarRating rating={reviewsSummary.average} readonly size="sm" /></div>
                  <p className="text-xs text-gray-600 mt-1">{reviewsSummary.total} {reviewsSummary.total === 1 ? 'reseña' : 'reseñas'}</p>
                </div>
                <div className="flex-1 min-w-0">
                  {reviewsSummary.reviews[0] && (
                    <div className="border border-gray-100 rounded p-2">
                      <div className="flex flex-col gap-2">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                            <User className="w-4 h-4 text-orange-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-gray-900 truncate">{reviewsSummary.reviews[0].user_name || 'Usuario'}</p>
                            <p className="text-xs text-gray-500">{new Date(reviewsSummary.reviews[0].createdAt).toLocaleDateString('es-ES')}</p>
                          </div>
                        </div>
                        <div className="flex justify-start">
                          <StarRating rating={reviewsSummary.reviews[0].rating} readonly size="sm" />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductCard;
