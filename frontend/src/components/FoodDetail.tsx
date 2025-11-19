import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { RecipeDetail } from '../types/api';
import { FoodSuggestion } from '../types';
import './FoodDetail.css';

const FoodDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      const viewedKey = `viewed_${id}`;
      const alreadyViewed = sessionStorage.getItem(viewedKey);

      if (!alreadyViewed) {
        sessionStorage.setItem(viewedKey, "true");
        loadRecipeDetail(id);
      } else {
        loadRecipeDetail(id, false);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);



  // Helper to check if user is guest (not registered)
  const isGuestUser = (): boolean => {
    const hasToken = !!localStorage.getItem('access_token');
    return !hasToken; // Guest if no access_token
  };

  const loadRecipeDetail = async (recipeId: string, recordView: boolean = true) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.getRecipeDetail(recipeId);

      if (response.data) {
        setRecipe(response.data);

        // Only record view for registered users, not guests
        if (recordView && !isGuestUser()) {
          const userId = localStorage.getItem('userId');
          if (userId) {
            try {
              await apiService.recordUserInteraction(userId, {
                recipe_id: recipeId,
                event_type: 'view'
              });
            } catch (err) {
              console.error('Failed to record view interaction:', err);
            }
          }
        }
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      console.error('Failed to load recipe detail:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recipe details');
    } finally {
      setLoading(false);
    }
  };


  // Convert API recipe to FoodSuggestion format for display
  const food: FoodSuggestion | null = recipe ? {
    id: recipe.recipe_id,
    name: recipe.title,
    description: recipe.instructions || `Delicious ${recipe.cuisine} dish`,
    ingredients: recipe.ingredients?.map(ing => 
      `${ing.ingredient_name}${ing.quantity ? ` (${ing.quantity}${ing.unit || ''})` : ''}`
    ) || [],
    cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
    difficulty: 'Medium', // Default difficulty
    cuisine: recipe.cuisine || 'Unknown',
    mealType: ['Lunch', 'Dinner'], // Default meal types
    dietaryTags: recipe.allergens || [],
    image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop',
    servings: recipe.servings,
    ratingValue: recipe.rating_value,
    ratingCount: recipe.rating_count
  } : null;

  // Get instructions from recipe or use default
  const instructions = recipe?.instructions
  ? recipe.instructions
      .split(/\||\n/) // split by | or newline
      .map(step => step.trim())
      .filter(step => step.length > 0)
  : [
      'Prepare ingredients as listed above.',
      'Follow the cooking instructions for your chosen recipe.',
      'Cook according to the specified time and temperature.',
      'Season to taste and serve hot.'
    ];


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

  const handleRate = async () => {
    if (isGuestUser()) {
      alert('Please sign in to rate recipes. Guest ratings are not saved.');
      return;
    }
    
    const userId = localStorage.getItem('userId');
    if (userId && recipe) {
      try {
        await apiService.recordUserInteraction(userId, {
          recipe_id: recipe.recipe_id,
          event_type: 'rating',
          rating: 5 // Default high rating for now
        });
        alert('Recipe rated successfully!');
      } catch (err) {
        console.error('Failed to rate recipe:', err);
        alert('Failed to rate recipe');
      }
    }
  };

  const handleAddToFavorites = async () => {
    if (isGuestUser()) {
      alert('Please sign in to save recipes. Guest favorites are not saved.');
      return;
    }
    
    const userId = localStorage.getItem('userId');
    if (userId && recipe) {
      try {
        // When user rates a recipe, it's considered as 'rated' (rating event)
        await apiService.recordUserInteraction(userId, {
          recipe_id: recipe.recipe_id,
          event_type: 'rating',
          rating: 5 // Default rating when adding to favorites
        });
        alert('Recipe added to favorites!');
      } catch (err) {
        console.error('Failed to add to favorites:', err);
        alert('Failed to add to favorites');
      }
    }
  };

  if (loading) {
    return (
      <div className="food-detail-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading recipe details...</h3>
          </div>
        </div>
      </div>
    );
  }

  if (error || !food) {
    return (
      <div className="food-detail-container">
        <div className="container">
          <button 
            className="back-button"
            onClick={() => navigate(-1)}
          >
            ← Back
          </button>
          <div className="error-state">
            <h3>Failed to load recipe</h3>
            <p>{error || 'Recipe not found'}</p>
            <button onClick={() => loadRecipeDetail(id!)} className="btn btn-primary">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="food-detail-container">
      <div className="container">
        <button 
          className="back-button"
          onClick={() => navigate(-1)}
        >
          ← Back
        </button>

        <div className="food-detail">
          <div className="detail-header">
            <div className="food-image">
              <img src={food.image} alt={food.name} />
            </div>
            <div className="food-info">
              <div className="food-badges">
                <span className="cuisine-badge">{food.cuisine}</span>
                <span 
                  className="difficulty-badge"
                  style={{ color: getDifficultyColor(food.difficulty) }}
                >
                  {getDifficultyText(food.difficulty)}
                </span>
              </div>
              <h1>{food.name}</h1>
              <p className="food-description">{food.description}</p>
              
              <div className="food-meta">
                <div className="meta-item">
                  <span className="meta-icon"></span>
                  <span>{food.cookingTime}</span>
                </div>
                <div className="meta-item">
                  <span className="meta-icon"></span>
                  <span>{food.mealType?.join(', ') || 'Not specified'}</span>
                </div>
              </div>

              <div className="action-buttons">
                <button className="btn btn-primary" onClick={handleRate}>
                  <span></span>
                  Rate this dish
                </button>
                <button className="btn btn-outline" onClick={handleAddToFavorites}>
                  <span></span>
                  Add to favorites
                </button>
              </div>
            </div>
          </div>

          <div className="detail-content">
            <div className="content-grid">
              <div className="ingredients-section">
                <h2>Ingredients needed</h2>
                <div className="ingredients-list">
                  {food.ingredients.map((ingredient, index) => (
                    <div key={index} className="ingredient-item">
                      <span className="ingredient-name">{ingredient}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="instructions-section">
                <h2>Instructions</h2>
                <div className="instructions-list">
                  {instructions.map((instruction, index) => (
                    <div key={index} className="instruction-item">
                      <div className="step-number">{index + 1}</div>
                      <div className="step-content">{instruction}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {food.dietaryTags && food.dietaryTags.length > 0 && (
              <div className="dietary-tags">
                <h3>Suitable for diet:</h3>
                <div className="tags-list">
                  {food.dietaryTags.map((tag, index) => (
                    <span key={index} className="dietary-tag">{tag}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FoodDetail;
