import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { IngredientSearchRequest, IngredientSearchResponse } from '../types/api';
import { Ingredient } from '../types';
import './IngredientList.css';

const IngredientList: React.FC = () => {
  const navigate = useNavigate();
  const [ingredients, setIngredients] = useState<Ingredient[]>([]);
  const [newIngredient, setNewIngredient] = useState('');
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState<string[]>([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadIngredients();
    loadCategories();
    // Also load from localStorage for backward compatibility
    const storedIngredients = localStorage.getItem('detectedIngredients');
    if (storedIngredients) {
      const localIngredients = JSON.parse(storedIngredients);
      setIngredients(prev => [...prev, ...localIngredients]);
    }
  }, []);

  useEffect(() => {
    // Debounce search
    const timeoutId = setTimeout(() => {
      if (searchTerm || selectedCategory) {
        searchIngredients();
      } else {
        loadIngredients();
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedCategory]);

  const loadIngredients = async (pageNum: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const request: IngredientSearchRequest = {
        limit: 20,
        offset: (pageNum - 1) * 20
      };

      const response = await apiService.searchIngredients(request);
      
      if (response.data) {
        const convertedIngredients = response.data.ingredients.map(ing => ({
          name: ing.canonical_name,
          source: 'api' as const,
          id: ing.ingredient_id,
          category: ing.category,
          allergen: ing.allergen
        }));

        if (pageNum === 1) {
          setIngredients(convertedIngredients);
        } else {
          setIngredients(prev => [...prev, ...convertedIngredients]);
        }
        
        setHasMore(response.data.has_more);
        setPage(pageNum);
      } else if (response.error) {
        setError(response.error);
        loadMockData();
      }
    } catch (err) {
      console.error('Failed to load ingredients:', err);
      setError(err instanceof Error ? err.message : 'Failed to load ingredients');
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const searchIngredients = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const request: IngredientSearchRequest = {
        query: searchTerm || undefined,
        category: selectedCategory || undefined,
        limit: 20,
        offset: 0
      };

      const response = await apiService.searchIngredients(request);
      
      if (response.data) {
        const convertedIngredients = response.data.ingredients.map(ing => ({
          name: ing.canonical_name,
          source: 'api' as const,
          id: ing.ingredient_id,
          category: ing.category,
          allergen: ing.allergen
        }));

        setIngredients(convertedIngredients);
        setHasMore(response.data.has_more);
        setPage(1);
      } else if (response.error) {
        setError(response.error);
        loadMockData();
      }
    } catch (err) {
      console.error('Failed to search ingredients:', err);
      setError(err instanceof Error ? err.message : 'Failed to search ingredients');
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    try {
      // Get unique categories from ingredients
      const response = await apiService.searchIngredients({ limit: 100 });
      if (response.data) {
        const uniqueCategories = [...new Set(
          response.data.ingredients
            .map(ing => ing.category)
            .filter(Boolean)
        )];
        setCategories(uniqueCategories);
      }
    } catch (err) {
      console.error('Failed to load categories:', err);
    }
  };

  const loadMockData = () => {
    const mockIngredients: Ingredient[] = [
      { name: 'Tomatoes', source: 'api' },
      { name: 'Onions', source: 'api' },
      { name: 'Garlic', source: 'api' },
      { name: 'Beef', source: 'api' },
      { name: 'Cilantro', source: 'api' },
      { name: 'Bell Peppers', source: 'api' }
    ];
    
    setIngredients(mockIngredients);
    setHasMore(false);
  };

  const addIngredient = () => {
    if (newIngredient.trim()) {
      const ingredient: Ingredient = {
        name: newIngredient.trim(),
        source: 'text'
      };
      const updatedIngredients = [...ingredients, ingredient];
      setIngredients(updatedIngredients);
      localStorage.setItem('detectedIngredients', JSON.stringify(updatedIngredients));
      setNewIngredient('');
    }
  };

  const removeIngredient = (index: number) => {
    const updatedIngredients = ingredients.filter((_, i) => i !== index);
    setIngredients(updatedIngredients);
    localStorage.setItem('detectedIngredients', JSON.stringify(updatedIngredients));
  };

  const startEditing = (index: number) => {
    setEditingIndex(index);
  };

  const saveEdit = (index: number, newName: string) => {
    if (newName.trim()) {
      const updatedIngredients = ingredients.map((ingredient, i) =>
        i === index ? { ...ingredient, name: newName.trim() } : ingredient
      );
      setIngredients(updatedIngredients);
      localStorage.setItem('detectedIngredients', JSON.stringify(updatedIngredients));
    }
    setEditingIndex(null);
  };

  const cancelEdit = () => {
    setEditingIndex(null);
  };

  const clearAllIngredients = () => {
    if (window.confirm('Are you sure you want to delete all ingredients?')) {
      setIngredients([]);
      localStorage.removeItem('detectedIngredients');
    }
  };

  const proceedToSuggestions = () => {
    if (ingredients.length > 0) {
      // Save ingredients to localStorage for recommendations
      localStorage.setItem('uploadedIngredients', JSON.stringify(ingredients));
      navigate('/suggestions');
    }
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadIngredients(page + 1);
    }
  };

  const handleIngredientClick = (ingredient: Ingredient) => {
    if (ingredient.id) {
      navigate(`/ingredient/${ingredient.id}`);
    }
  };

  if (loading && ingredients.length === 0) {
    return (
      <div className="ingredient-list-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading ingredients...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="ingredient-list-container">
      <div className="container">
        <div className="ingredient-list-header">
          <h1>Ingredient List</h1>
          <p>Manage your ingredients to suggest suitable dishes</p>
          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
              <button onClick={() => loadIngredients()} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}
        </div>

        {/* Search and Filter Section */}
        <div className="search-filter-section">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search ingredients..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input"
            />
          </div>
          <div className="filter-controls">
            <div className="filter-group">
              <label className="form-label">Category</label>
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="form-input"
              >
                <option value="">All Categories</option>
                {categories.map(category => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="add-ingredient-section">
          <div className="add-form">
            <input
              type="text"
              placeholder="Add new ingredient..."
              value={newIngredient}
              onChange={(e) => setNewIngredient(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && addIngredient()}
              className="form-input"
            />
            <button 
              className="btn btn-primary"
              onClick={addIngredient}
              disabled={!newIngredient.trim()}
            >
              Add
            </button>
          </div>
        </div>

        <div className="ingredients-section">
          <div className="section-header">
            <h2>Available Ingredients ({ingredients.length})</h2>
            {ingredients.length > 0 && (
              <button 
                className="btn btn-outline btn-sm"
                onClick={clearAllIngredients}
              >
                Clear All
              </button>
            )}
          </div>

          {ingredients.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon"></div>
              <h3>No ingredients yet</h3>
              <p>Add ingredients to start getting dish suggestions</p>
            </div>
          ) : (
            <div className="ingredients-grid">
              {ingredients.map((ingredient, index) => (
                <div key={index} className="ingredient-item">
                  <div 
                    className="ingredient-info"
                    onClick={() => ingredient.id && handleIngredientClick(ingredient)}
                    style={{ cursor: ingredient.id ? 'pointer' : 'default' }}
                  >
                    <div className="ingredient-icon">
                    </div>
                    {editingIndex === index ? (
                      <input
                        type="text"
                        defaultValue={ingredient.name}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            saveEdit(index, e.currentTarget.value);
                          } else if (e.key === 'Escape') {
                            cancelEdit();
                          }
                        }}
                        onBlur={(e) => saveEdit(index, e.target.value)}
                        autoFocus
                        className="edit-input"
                      />
                    ) : (
                      <span className="ingredient-name">{ingredient.name}</span>
                    )}
                    {ingredient.category && (
                      <span className="ingredient-category">{ingredient.category}</span>
                    )}
                  </div>
                  
                  <div className="ingredient-actions">
                    {editingIndex === index ? (
                      <>
                        <button
                          className="action-btn save"
                          onClick={(e) => {
                            const input = e.currentTarget.parentElement?.parentElement?.querySelector('.edit-input') as HTMLInputElement;
                            if (input) saveEdit(index, input.value);
                          }}
                        >
                          ✓
                        </button>
                        <button
                          className="action-btn cancel"
                          onClick={cancelEdit}
                        >
                          ✕
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          className="action-btn edit"
                          onClick={() => startEditing(index)}
                          title="Edit"
                        >
                        </button>
                        <button
                          className="action-btn remove"
                          onClick={() => removeIngredient(index)}
                          title="Delete"
                        >
                        </button>
                      </>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {ingredients.length > 0 && (
          <div className="action-section">
            <button 
              className="btn btn-primary btn-lg"
              onClick={proceedToSuggestions}
            >
              View Dish Suggestions
            </button>
          </div>
        )}

        {hasMore && (
          <div className="load-more-section">
            <button 
              className="btn btn-outline"
              onClick={loadMore}
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Load More'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default IngredientList;

