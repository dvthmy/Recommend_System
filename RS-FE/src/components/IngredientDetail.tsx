import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { IngredientDetail as IngredientDetailType } from '../types/api';
import './IngredientDetail.css';

const IngredientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [ingredient, setIngredient] = useState<IngredientDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadIngredientDetail(id);
    }
  }, [id]);

  const loadIngredientDetail = async (ingredientId: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getIngredientDetail(ingredientId);
      
      if (response.data) {
        setIngredient(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      console.error('Failed to load ingredient detail:', err);
      setError(err instanceof Error ? err.message : 'Failed to load ingredient details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="ingredient-detail-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading ingredient details...</h3>
          </div>
        </div>
      </div>
    );
  }

  if (error || !ingredient) {
    return (
      <div className="ingredient-detail-container">
        <div className="container">
          <button 
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>
          <div className="error-state">
            <h3>Failed to load ingredient</h3>
            <p>{error || 'Ingredient not found'}</p>
            <button onClick={() => loadIngredientDetail(id!)} className="btn btn-primary">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ingredient-detail-container">
      <div className="container">
        <button 
          className="back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="ingredient-detail">
          <div className="detail-header">
            <div className="ingredient-image">
              <div className="ingredient-placeholder">
                <span className="ingredient-icon">🥬</span>
              </div>
            </div>
            <div className="ingredient-info">
              <div className="ingredient-badges">
                {ingredient.category && (
                  <span className="category-badge">{ingredient.category}</span>
                )}
                {ingredient.allergen && (
                  <span className="allergen-badge">⚠️ Allergen</span>
                )}
              </div>
              <h1>{ingredient.canonical_name}</h1>
              {ingredient.name && ingredient.name !== ingredient.canonical_name && (
                <p className="alternative-name">Also known as: {ingredient.name}</p>
              )}
              
              {ingredient.description && (
                <p className="ingredient-description">{ingredient.description}</p>
              )}

              <div className="ingredient-meta">
                {ingredient.category && (
                  <div className="meta-item">
                    <span className="meta-label">Category:</span>
                    <span className="meta-value">{ingredient.category}</span>
                  </div>
                )}
                {ingredient.allergen && (
                  <div className="meta-item">
                    <span className="meta-label">Allergen:</span>
                    <span className="meta-value warning">Yes</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="detail-content">
            <div className="content-grid">
              {ingredient.alternative_names && ingredient.alternative_names.length > 0 && (
                <div className="alternative-names-section">
                  <h2>Alternative Names</h2>
                  <div className="alternative-names-list">
                    {ingredient.alternative_names.map((name, index) => (
                      <span key={index} className="alternative-name-tag">
                        {name}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {ingredient.nutrition_info && (
                <div className="nutrition-section">
                  <h2>Nutrition Information</h2>
                  <div className="nutrition-grid">
                    {Object.entries(ingredient.nutrition_info).map(([key, value]) => (
                      <div key={key} className="nutrition-item">
                        <span className="nutrition-label">{key}:</span>
                        <span className="nutrition-value">{value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {ingredient.allergen && (
              <div className="allergen-warning">
                <h3>⚠️ Allergen Warning</h3>
                <p>This ingredient may cause allergic reactions in some people. Please check with your doctor if you have any food allergies.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default IngredientDetail;
