import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { RecipeSearchRequest, RecipeSearchResponse } from '../types/api';
import { FoodSuggestion } from '../types';
import './FoodList.css';

const FoodList: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [allFoods, setAllFoods] = useState<FoodSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cuisines, setCuisines] = useState<string[]>(['All']);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadRecipes();
    loadCuisines();
  }, []);

  useEffect(() => {
    // Debounce search
    const timeoutId = setTimeout(() => {
      if (searchTerm || selectedCuisine || selectedDifficulty) {
        searchRecipes();
      } else {
        loadRecipes();
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [searchTerm, selectedCuisine, selectedDifficulty]);

  const loadRecipes = async (pageNum: number = 1) => {
    setLoading(true);
    setError(null);
    
    try {
      const request: RecipeSearchRequest = {
        limit: 20,
        offset: (pageNum - 1) * 20
      };

      const response = await apiService.searchRecipes(request);
      
      if (response.data) {
        const convertedRecipes = response.data.recipes.map(recipe => ({
          id: recipe.recipe_id,
          name: recipe.title,
          description: recipe.instructions || `Delicious ${recipe.cuisine} dish`,
          ingredients: recipe.ingredients?.map(ing => ing.ingredient_name) || [],
          cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
          difficulty: 'Medium', // Default difficulty
          cuisine: recipe.cuisine || 'Unknown',
          mealType: ['Lunch', 'Dinner'], // Default meal types
          dietaryTags: recipe.allergens || [],
          image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
        }));

        if (pageNum === 1) {
          setAllFoods(convertedRecipes);
        } else {
          setAllFoods(prev => [...prev, ...convertedRecipes]);
        }
        
        setHasMore(response.data.has_more);
        setPage(pageNum);
      } else if (response.error) {
        setError(response.error);
        loadMockData();
      }
    } catch (err) {
      console.error('Failed to load recipes:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recipes');
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const searchRecipes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const request: RecipeSearchRequest = {
        query: searchTerm || undefined,
        cuisine: selectedCuisine || undefined,
        limit: 20,
        offset: 0
      };

      const response = await apiService.searchRecipes(request);
      
      if (response.data) {
        const convertedRecipes = response.data.recipes.map(recipe => ({
          id: recipe.recipe_id,
          name: recipe.title,
          description: recipe.instructions || `Delicious ${recipe.cuisine} dish`,
          ingredients: recipe.ingredients?.map(ing => ing.ingredient_name) || [],
          cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
          difficulty: 'Medium',
          cuisine: recipe.cuisine || 'Unknown',
          mealType: ['Lunch', 'Dinner'],
          dietaryTags: recipe.allergens || [],
          image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
        }));

        setAllFoods(convertedRecipes);
        setHasMore(response.data.has_more);
        setPage(1);
      } else if (response.error) {
        setError(response.error);
        loadMockData();
      }
    } catch (err) {
      console.error('Failed to search recipes:', err);
      setError(err instanceof Error ? err.message : 'Failed to search recipes');
      loadMockData();
    } finally {
      setLoading(false);
    }
  };

  const loadCuisines = async () => {
    try {
      const response = await apiService.getCuisines();
      if (response.data) {
        setCuisines(['All', ...response.data.cuisines]);
      }
    } catch (err) {
      console.error('Failed to load cuisines:', err);
    }
  };

  const loadMockData = () => {
    const mockFoods: FoodSuggestion[] = [
      {
        id: '1',
        name: 'Beef Stew',
        description: 'Traditional beef stew with rich broth',
        ingredients: ['Beef', 'Carrots', 'Potatoes', 'Onions'],
        cookingTime: '2 hours',
        difficulty: 'Medium',
        cuisine: 'Vietnamese',
        mealType: ['Lunch', 'Dinner'],
        dietaryTags: ['Gluten Free'],
        image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
      },
      {
        id: '2',
        name: 'Tomato Salad',
        description: 'Fresh tomato salad with olive oil',
        ingredients: ['Tomatoes', 'Cilantro', 'Onions', 'Olive Oil'],
        cookingTime: '15 minutes',
        difficulty: 'Easy',
        cuisine: 'International',
        mealType: ['Breakfast', 'Lunch'],
        dietaryTags: ['Vegan', 'Gluten Free'],
        image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop'
      },
      {
        id: '3',
        name: 'Stir-fried Bell Peppers',
        description: 'Crispy stir-fried bell peppers with garlic and soy sauce',
        ingredients: ['Bell Peppers', 'Garlic', 'Soy Sauce', 'Cooking Oil'],
        cookingTime: '20 minutes',
        difficulty: 'Easy',
        cuisine: 'Asian',
        mealType: ['Lunch', 'Dinner'],
        dietaryTags: ['Vegan', 'Gluten Free'],
        image: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop'
      }
    ];
    
    setAllFoods(mockFoods);
    setHasMore(false);
  };

  const handleViewDetails = (foodId: string) => {
    navigate(`/food/${foodId}`);
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      loadRecipes(page + 1);
    }
  };

  const difficulties = ['All', 'Easy', 'Medium', 'Hard'];

  // No need for client-side filtering since we're using API search
  const filteredFoods = allFoods;

  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'Easy';
      case 'Medium': return 'Medium';
      case 'Hard': return 'Hard';
      default: return difficulty;
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'var(--color-success)';
      case 'Medium': return 'var(--color-warning)';
      case 'Hard': return 'var(--color-error)';
      default: return 'var(--text-secondary)';
    }
  };

  if (loading && allFoods.length === 0) {
    return (
      <div className="food-list-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading recipes...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="food-list-container">
      <div className="container">
        <div className="food-list-header">
          <h1>Food List</h1>
          <p>Discover all dishes available in the system</p>
          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
              <button onClick={() => loadRecipes()} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}
        </div>

        <div className="filters-section">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search dishes..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-input"
            />
          </div>

          <div className="filter-controls">
            <div className="filter-group">
              <label className="form-label">Cuisine</label>
              <select
                value={selectedCuisine}
                onChange={(e) => setSelectedCuisine(e.target.value)}
                className="form-input"
              >
                {cuisines.map(cuisine => (
                  <option key={cuisine} value={cuisine === 'All' ? '' : cuisine}>
                    {cuisine}
                  </option>
                ))}
              </select>
            </div>

            <div className="filter-group">
              <label className="form-label">Difficulty</label>
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="form-input"
              >
                {difficulties.map(difficulty => (
                  <option key={difficulty} value={difficulty === 'All' ? '' : difficulty}>
                    {difficulty === 'All' ? difficulty : getDifficultyText(difficulty)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        <div className="results-info">
          <p>Found {filteredFoods.length} dishes</p>
        </div>

        <div className="foods-grid">
          {filteredFoods.map((food) => (
            <div key={food.id} className="food-card">
              <div className="card-image">
                <img src={food.image} alt={food.name} />
              <div className="card-overlay">
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => handleViewDetails(food.id)}
                >
                  View Details
                </button>
              </div>
              </div>
              
              <div className="card-content">
                <div className="card-header">
                  <h3>{food.name}</h3>
                  <div className="cuisine-tag">{food.cuisine}</div>
                </div>
                
                <p className="description">{food.description}</p>
                
                <div className="card-meta">
                  <div className="meta-item">
                    <span className="meta-icon"></span>
                    <span>{food.cookingTime}</span>
                  </div>
                  <div 
                    className="meta-item difficulty"
                    style={{ color: getDifficultyColor(food.difficulty) }}
                  >
                    <span className="meta-icon"></span>
                    <span>{getDifficultyText(food.difficulty)}</span>
                  </div>
                </div>

                <div className="ingredients-preview">
                  <div className="ingredients-list">
                    {food.ingredients.slice(0, 3).map((ingredient, index) => (
                      <span key={index} className="ingredient-tag">
                        {ingredient}
                      </span>
                    ))}
                    {food.ingredients.length > 3 && (
                      <span className="ingredient-tag more">
                        +{food.ingredients.length - 3}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {filteredFoods.length === 0 && !loading && (
          <div className="no-results">
            <div className="no-results-icon"></div>
            <h3>No dishes found</h3>
            <p>Try changing your search terms or filters</p>
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

export default FoodList;

