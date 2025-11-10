import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { RecipeRecommendation, RecommendationRequest } from '../types/api';
import { FoodSuggestion } from '../types';
import './FoodSuggestions.css';

const FoodSuggestions: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [suggestions, setSuggestions] = useState<FoodSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [ratingModal, setRatingModal] = useState<{ isOpen: boolean; foodId: string | null }>({
    isOpen: false,
    foodId: null
  });
  const [userRating, setUserRating] = useState(0);

  useEffect(() => {
    if (user?.user_id) {
      loadRecommendations();
    }
  }, [user]);

  const loadRecommendations = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Get ingredients from localStorage (from upload step)
      const uploadedIngredients = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
      const ingredientIds = uploadedIngredients.map((ing: any) => ing.id || ing.name).filter(Boolean);
      
      // Use user ID from context
      if (!user?.user_id) {
        throw new Error('User not initialized');
      }
      
      // Prepare recommendation request
      const request: RecommendationRequest = {
        user_id: user.user_id,
        ingredient_ids: ingredientIds.length > 0 ? ingredientIds : undefined,
        max_cook_time: user.max_cook_time,
        limit: 10
      };

      // Call recommendation API
      const response = await apiService.getRecommendations(request);
      
      if (response.data) {
        // Convert API response to FoodSuggestion format
        const convertedSuggestions = response.data.results.map((recipe: RecipeRecommendation) => ({
          id: recipe.recipe_id,
          name: recipe.title,
          description: `Delicious ${recipe.cuisine} dish`, // API doesn't provide description
          ingredients: [], // Will be loaded from recipe detail if needed
          cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
          difficulty: 'Medium', // Default difficulty
          cuisine: recipe.cuisine,
          mealType: ['Lunch', 'Dinner'], // Default meal types
          dietaryTags: [], // Will be loaded from recipe detail if needed
          image: recipe.image || 
            (Array.isArray((recipe as any).image_urls) && (recipe as any).image_urls.length > 0
              ? (recipe as any).image_urls[0]
              : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'), // Default image
          matchScore: Math.round(recipe.score * 100) // Convert score to percentage
        }));
        
        setSuggestions(convertedSuggestions);
      } else if (response.error) {
        setError(response.error);
        // Fallback to mock data if API fails
        loadMockSuggestions();
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      // Fallback to mock data
      loadMockSuggestions();
    } finally {
      setLoading(false);
    }
  };

  const loadMockSuggestions = () => {
    const mockSuggestions: FoodSuggestion[] = [
      {
        id: '1',
        name: 'Beef Stew',
        description: 'Traditional beef stew with rich broth and fresh vegetables',
        ingredients: ['Beef', 'Carrots', 'Potatoes', 'Onions', 'Garlic', 'Ginger', 'Cinnamon', 'Star Anise'],
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
        description: 'Fresh tomato salad with olive oil and herbs',
        ingredients: ['Tomatoes', 'Cilantro', 'Onions', 'Olive Oil', 'Vinegar', 'Salt', 'Pepper'],
        cookingTime: '15 minutes',
        difficulty: 'Easy',
        cuisine: 'International',
        mealType: ['Breakfast', 'Lunch', 'Snack'],
        dietaryTags: ['Vegan', 'Gluten Free'],
        image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop'
      },
      {
        id: '3',
        name: 'Stir-fried Bell Peppers',
        description: 'Crispy stir-fried bell peppers with garlic and soy sauce',
        ingredients: ['Bell Peppers', 'Garlic', 'Soy Sauce', 'Cooking Oil', 'Green Onions', 'Black Pepper'],
        cookingTime: '20 minutes',
        difficulty: 'Easy',
        cuisine: 'Asian',
        mealType: ['Lunch', 'Dinner'],
        dietaryTags: ['Vegan', 'Gluten Free'],
        image: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop'
      }
    ];
    
    const scoredSuggestions = mockSuggestions.map(suggestion => ({
      ...suggestion,
      matchScore: Math.floor(Math.random() * 30) + 70
    }));
    
    setSuggestions(scoredSuggestions);
  };

  const handleViewDetails = (foodId: string) => {
    navigate(`/food/${foodId}`);
  };

  const handleRate = (foodId: string) => {
    setRatingModal({ isOpen: true, foodId });
    setUserRating(0);
  };

  const submitRating = async () => {
    if (ratingModal.foodId && userRating > 0) {
      try {
        // Use user ID from context
        if (!user?.user_id) {
          throw new Error('User not initialized');
        }
        
        // Record interaction with API
        await apiService.recordUserInteraction(user.user_id, {
          recipe_id: ratingModal.foodId,
          event_type: 'like',
          rating: userRating
        });
        
        // Also save to localStorage for backward compatibility
        const ratings = JSON.parse(localStorage.getItem('foodRatings') || '{}');
        ratings[ratingModal.foodId] = userRating;
        localStorage.setItem('foodRatings', JSON.stringify(ratings));
        
        setRatingModal({ isOpen: false, foodId: null });
        setUserRating(0);
      } catch (err) {
        console.error('Failed to record rating:', err);
        // Still close modal even if API fails
        setRatingModal({ isOpen: false, foodId: null });
        setUserRating(0);
      }
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

  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'Easy';
      case 'Medium': return 'Medium';
      case 'Hard': return 'Hard';
      default: return difficulty;
    }
  };

  if (loading) {
    return (
      <div className="suggestions-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Finding suitable dishes...</h3>
            <p>AI is analyzing ingredients and suggesting the best dishes for you</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="suggestions-container">
      <div className="container">
        <div className="suggestions-header">
          <h1>Dish Suggestions</h1>
          <p>Based on your ingredients, here are the most suitable dishes</p>
          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
              <button onClick={loadRecommendations} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}
        </div>

        <div className="suggestions-grid">
          {suggestions.map((suggestion) => (
            <div key={suggestion.id} className="suggestion-card">
              <div className="card-image">
                {suggestion.image ? (
                  <img src={suggestion.image} alt={suggestion.name} />
                ) : (
                  <div className="placeholder-image"></div>
                )}
                <div className="match-score">
                  {(suggestion as any).matchScore}% match
                </div>
              </div>
              
              <div className="card-content">
                <div className="card-header">
                  <h3>{suggestion.name}</h3>
                  <div className="cuisine-tag">{suggestion.cuisine}</div>
                </div>
                
                <p className="description">{suggestion.description}</p>
                
                <div className="card-meta">
                  <div className="meta-item">
                    <span className="meta-icon"></span>
                    <span>{suggestion.cookingTime}</span>
                  </div>
                  <div 
                    className="meta-item difficulty"
                    style={{ color: getDifficultyColor(suggestion.difficulty) }}
                  >
                    <span className="meta-icon"></span>
                    <span>{getDifficultyText(suggestion.difficulty)}</span>
                  </div>
                </div>

                <div className="ingredients-preview">
                  <h4>Main ingredients:</h4>
                  <div className="ingredients-list">
                    {suggestion.ingredients.slice(0, 4).map((ingredient, index) => (
                      <span key={index} className="ingredient-tag">
                        {ingredient}
                      </span>
                    ))}
                    {suggestion.ingredients.length > 4 && (
                      <span className="ingredient-tag more">
                        +{suggestion.ingredients.length - 4}
                      </span>
                    )}
                  </div>
                </div>

                <div className="card-footer">
                  <button 
                    className="btn btn-primary"
                    onClick={() => handleViewDetails(suggestion.id)}
                  >
                    View Details
                  </button>
                  <button 
                    className="btn btn-outline"
                    onClick={() => handleRate(suggestion.id)}
                  >
                    Rate
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Rating Modal */}
      {ratingModal.isOpen && (
        <div className="rating-modal-overlay">
          <div className="rating-modal">
            <h3>Rate Dish</h3>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  className={`star ${star <= userRating ? 'filled' : ''}`}
                  onClick={() => setUserRating(star)}
                >
                  ★
                </button>
              ))}
            </div>
            <p>{userRating > 0 ? `${userRating} stars` : 'Select rating'}</p>
            <div className="modal-actions">
              <button 
                className="btn btn-outline"
                onClick={() => setRatingModal({ isOpen: false, foodId: null })}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={submitRating}
                disabled={userRating === 0}
              >
                Submit Rating
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FoodSuggestions;