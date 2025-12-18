import { useState, useEffect } from 'react';
import { MessageSquare, User } from 'lucide-react';
import StarRating from '../common/StarRating';
import api from '../../utils/api';

const ProductReviews = ({ productId }) => {
  const [reviewsData, setReviewsData] = useState({ reviews: [], average: 0, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadReviews();
  }, [productId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Escuchar evento global 'review-submitted' para refrescar lista cuando se crea una reseña
  useEffect(() => {
    const handler = (e) => {
      try {
        const pid = e?.detail?.productId;
        if (pid && pid === productId) {
          loadReviews();
        }
      } catch (err) {
        // ignore
      }
    };

    window.addEventListener('review-submitted', handler);
    return () => window.removeEventListener('review-submitted', handler);
  }, [productId]);

  const loadReviews = async () => {
    try {
      setLoading(true);
      setError('');
      const { data } = await api.get(`/products/${productId}/reviews`);
      setReviewsData({
        reviews: data?.reviews || [],
        average: data?.average || 0,
        total: data?.total || 0,
      });
    } catch (err) {
      console.error('Error loading reviews:', err);
      setError('Error al cargar las reseñas');
      setReviewsData({ reviews: [], average: 0, total: 0 });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    const dateWithTz = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const date = new Date(dateWithTz);
    return date.toLocaleDateString('es-ES', {
      timeZone: 'America/Bogota',
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-20 bg-gray-200 rounded"></div>
        <div className="h-20 bg-gray-200 rounded"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-6 text-red-600">
        <p>{error}</p>
      </div>
    );
  }

  if (reviewsData.total === 0) {
    return (
      <div className="text-center py-8">
        <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">Este producto aún no tiene reseñas</p>
        <p className="text-sm text-gray-400 mt-1">Sé el primero en compartir tu opinión</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="bg-gray-50 rounded-lg p-4 flex items-center gap-4">
        <div className="text-center">
          <div className="text-4xl font-bold text-gray-900">{reviewsData.average.toFixed(1)}</div>
          <StarRating rating={reviewsData.average} readonly size="md" />
          <p className="text-sm text-gray-600 mt-1">
            {reviewsData.total} {reviewsData.total === 1 ? 'reseña' : 'reseñas'}
          </p>
        </div>
      </div>

      {/* Reviews List */}
      <div className="space-y-4">
        {reviewsData.reviews.map((review) => (
          <div key={review.id} className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
                  <User className="w-4 h-4 text-orange-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{review.user_name || 'Usuario'}</p>
                  <p className="text-xs text-gray-500">{formatDate(review.createdAt)}</p>
                </div>
              </div>
              <StarRating rating={review.rating} readonly size="sm" />
            </div>
            {review.comment && (
              <p className="text-gray-700 text-sm mt-2 pl-10">{review.comment}</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductReviews;
