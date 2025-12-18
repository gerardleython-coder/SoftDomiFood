import React, { useState, useEffect } from 'react';
import { Trash2, Star, AlertCircle } from 'lucide-react';

const ReviewsManagement = ({ reviews = [], onDelete, isLoading = false }) => {
  const [filteredReviews, setFilteredReviews] = useState([]);
  const [sortBy, setSortBy] = useState('date');
  const [filterRating, setFilterRating] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    let filtered = [...reviews];

    // Filtrar por búsqueda (nombre de usuario o producto)
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      filtered = filtered.filter(r =>
        r.user_name?.toLowerCase().includes(search) ||
        r.product_name?.toLowerCase().includes(search) ||
        r.user_email?.toLowerCase().includes(search)
      );
    }

    // Filtrar por rating
    if (filterRating !== 'all') {
      const rating = parseInt(filterRating);
      filtered = filtered.filter(r => r.rating === rating);
    }

    // Ordenar
    if (sortBy === 'date') {
      filtered.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    } else if (sortBy === 'rating-high') {
      filtered.sort((a, b) => b.rating - a.rating);
    } else if (sortBy === 'rating-low') {
      filtered.sort((a, b) => a.rating - b.rating);
    }

    setFilteredReviews(filtered);
  }, [reviews, sortBy, filterRating, searchTerm]);

  const handleDelete = async (reviewId) => {
    if (onDelete) {
      await onDelete(reviewId);
      setDeleteConfirm(null);
    }
  };

  const renderStars = (rating) => {
    return (
      <div className="flex gap-1">
        {[...Array(5)].map((_, i) => (
          <Star
            key={i}
            size={16}
            className={i < rating ? "fill-yellow-400 text-yellow-400" : "text-gray-300"}
          />
        ))}
      </div>
    );
  };

  const formatDate = (dateString) => {
    const dateWithTz = dateString.endsWith('Z') ? dateString : dateString + 'Z';
    const date = new Date(dateWithTz);
    return date.toLocaleString('es-CO', {
      timeZone: 'America/Bogota',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Controles de filtro */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <h3 className="font-semibold text-gray-900">Filtros y búsqueda</h3>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Búsqueda */}
          <input
            type="text"
            placeholder="Buscar por usuario o producto..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          />

          {/* Filtro por rating */}
          <select
            value={filterRating}
            onChange={(e) => setFilterRating(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="all">Todos los ratings</option>
            <option value="5">★★★★★ - 5 estrellas</option>
            <option value="4">★★★★ - 4 estrellas</option>
            <option value="3">★★★ - 3 estrellas</option>
            <option value="2">★★ - 2 estrellas</option>
            <option value="1">★ - 1 estrella</option>
          </select>

          {/* Ordenar */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-orange-500"
          >
            <option value="date">Más recientes primero</option>
            <option value="rating-high">Rating más alto</option>
            <option value="rating-low">Rating más bajo</option>
          </select>
        </div>

        <p className="text-sm text-gray-600">
          Mostrando {filteredReviews.length} de {reviews.length} reseñas
        </p>
      </div>

      {/* Tabla de reseñas */}
      {filteredReviews.length > 0 ? (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Usuario</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Producto</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Rating</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Comentario</th>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700">Fecha</th>
                  <th className="px-6 py-3 text-center font-semibold text-gray-700">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {filteredReviews.map((review) => (
                  <tr key={review.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{review.user_name}</p>
                        <p className="text-xs text-gray-500">{review.user_email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-gray-900">{review.product_name}</p>
                      <p className="text-xs text-gray-500">${review.product_price}</p>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col gap-2">
                        {renderStars(review.rating)}
                        <span className="text-xs text-gray-600 font-semibold">
                          {review.rating}/5
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="text-gray-700 max-w-xs truncate">
                        {review.comment || '(Sin comentario)'}
                      </p>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {formatDate(review.createdAt)}
                    </td>
                    <td className="px-6 py-4 text-center">
                      {deleteConfirm === review.id ? (
                        <div className="flex gap-2 justify-center">
                          <button
                            onClick={() => handleDelete(review.id)}
                            className="px-3 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600 transition"
                          >
                            Confirmar
                          </button>
                          <button
                            onClick={() => setDeleteConfirm(null)}
                            className="px-3 py-1 bg-gray-300 text-gray-700 text-xs rounded hover:bg-gray-400 transition"
                          >
                            Cancelar
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setDeleteConfirm(review.id)}
                          className="inline-flex items-center gap-2 px-3 py-1 text-red-600 hover:bg-red-50 rounded transition"
                        >
                          <Trash2 size={16} />
                          <span className="text-xs">Eliminar</span>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <AlertCircle size={32} className="mx-auto text-gray-400 mb-3" />
          <p className="text-gray-600">
            {reviews.length === 0 ? 'No hay reseñas en el sistema' : 'No se encontraron reseñas con los filtros aplicados'}
          </p>
        </div>
      )}
    </div>
  );
};

export default ReviewsManagement;
