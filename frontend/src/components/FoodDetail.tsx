import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { RecipeDetail } from '../types/api';
import { FoodSuggestion } from '../types';
import { Star, Heart, Clock, Utensils } from 'lucide-react';
import './FoodDetail.css';

const FoodDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [recipe, setRecipe] = useState<RecipeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [userRating, setUserRating] = useState<number>(0);
  const [hoveredStar, setHoveredStar] = useState<number>(0);
  const [isLiked, setIsLiked] = useState<boolean>(false);
  const [selectedIngredients, setSelectedIngredients] = useState<Set<number>>(new Set());

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
    return !hasToken;
  };

  const loadRecipeDetail = async (recipeId: string, recordView: boolean = true) => {
    setLoading(true);
    setError(null);

    try {
      const response = await apiService.getRecipeDetail(recipeId);

      if (response.data) {
        setRecipe(response.data);
        
        // Load liked status
        await loadLikedStatus(recipeId);

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

  const loadLikedStatus = async (recipeId: string) => {
    const isGuest = isGuestUser();
    
    if (isGuest) {
      // For guest users, check localStorage
      try {
        const liked = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        setIsLiked(liked.includes(recipeId));
      } catch (err) {
        console.error('Failed to load liked status from localStorage:', err);
        setIsLiked(false);
      }
      return;
    }

    // For registered users, check backend
    const userId = localStorage.getItem('userId');
    if (!userId) {
      setIsLiked(false);
      return;
    }

    try {
      const response = await apiService.getUserInteractions(userId, 'like', 100, 0);
      if (response.data && response.data.interactions) {
        const liked = response.data.interactions.some((interaction: any) => interaction.recipe_id === recipeId);
        setIsLiked(liked);
      } else {
        setIsLiked(false);
      }
    } catch (err) {
      console.error('Failed to load liked status:', err);
      setIsLiked(false);
    }
  };

  // Convert API recipe to FoodSuggestion format for display
  const food: FoodSuggestion | null = recipe ? {
    id: recipe.recipe_id,
    name: recipe.title,
    description: recipe.description || `Delicious ${recipe.cuisine} dish`,
    ingredients: recipe.ingredients?.map(ing => 
      `${ing.ingredient_name}${ing.quantity ? ` (${ing.quantity}${ing.unit || ''})` : ''}`
    ) || [],
    cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
    difficulty: 'Medium',
    cuisine: recipe.cuisine || 'Unknown',
    mealType: ['Lunch', 'Dinner'],
    dietaryTags: recipe.allergens || [],
    image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&h=600&fit=crop',
    servings: recipe.servings,
    ratingValue: recipe.rating_value,
    ratingCount: recipe.rating_count
  } : null;

  // Get instructions from recipe or use default
  const instructions = recipe?.instructions
    ? recipe.instructions
        .split(/\||\n/)
        .map(step => step.trim())
        .filter(step => step.length > 0)
    : [
        'Prepare ingredients as listed above.',
        'Follow the cooking instructions for your chosen recipe.',
        'Cook according to the specified time and temperature.',
        'Season to taste and serve hot.'
      ];

  const handleRate = async (rating: number) => {
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
          rating: rating
        });
        setUserRating(rating);
        alert('Recipe rated successfully!');
        loadRecipeDetail(id!, false);
      } catch (err) {
        console.error('Failed to rate recipe:', err);
        alert('Failed to rate recipe');
      }
    }
  };

  const handleToggleLike = async () => {
    if (!recipe) return;

    const isGuest = isGuestUser();
    const recipeId = recipe.recipe_id;
    const newLikedState = !isLiked;

    // Optimistic update
    setIsLiked(newLikedState);

    if (isGuest) {
      // For guest users, save to localStorage
      try {
        const liked = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        if (newLikedState) {
          if (!liked.includes(recipeId)) {
            liked.push(recipeId);
          }
        } else {
          const index = liked.indexOf(recipeId);
          if (index > -1) {
            liked.splice(index, 1);
          }
        }
        localStorage.setItem('likedRecipes', JSON.stringify(liked));
      } catch (err) {
        console.error('Failed to save like to localStorage:', err);
        setIsLiked(!newLikedState); // Revert on error
      }
      return;
    }

    // For registered users, save to backend
    const userId = localStorage.getItem('userId');
    if (!userId) {
      setIsLiked(!newLikedState); // Revert
      return;
    }

    try {
      await apiService.recordUserInteraction(userId, {
        recipe_id: recipeId,
        event_type: 'like'
      });
      // Success - state already updated optimistically
    } catch (err) {
      console.error('Failed to toggle like:', err);
      setIsLiked(!newLikedState); // Revert on error
      alert('Failed to update like status');
    }
  };


  const renderStars = (rating: number, interactive: boolean = false, size: number = 20) => {
    const stars = [];
    const displayRating = interactive ? (hoveredStar || userRating) : rating;

    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= Math.floor(displayRating) || (i === Math.ceil(displayRating) && displayRating % 1 >= 0.5);
      stars.push(
        <Star
          key={i}
          className={`star ${isFilled ? 'filled' : ''}`}
          size={size}
          fill={isFilled ? 'currentColor' : 'none'}
          strokeWidth={1.5}
          onMouseEnter={interactive ? () => setHoveredStar(i) : undefined}
          onMouseLeave={interactive ? () => setHoveredStar(0) : undefined}
          onClick={interactive ? () => setUserRating(i) : undefined}
          style={{ cursor: interactive ? 'pointer' : 'default' }}
        />
      );
    }
    return stars;
  };

  const formatTime = (minutes?: number) => {
    if (!minutes) return 'Unknown';
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}h${mins}m` : `${hours}h`;
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

  const ratingValue = recipe?.rating_value || food?.ratingValue || 0;
  const ratingCount = recipe?.rating_count || food?.ratingCount || 0;
  const cookTime = recipe?.cook_time_min || 0;
  const servings = recipe?.servings || food?.servings || 0;
  const totalTime = recipe?.total_time_min || cookTime;

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
          <div className="detail-layout-vertical">
            {/* Image */}
            <div className="food-image">
              <img src={food.image} alt={food.name} />
              <button 
                className={`btn-like-overlay ${isLiked ? 'liked' : ''}`} 
                onClick={handleToggleLike} 
                title={isLiked ? 'Remove from favorites' : 'Add to favorites'}
              >
                <Heart size={24} fill={isLiked ? 'currentColor' : 'none'} />
              </button>
            </div>

            {/* Title */}
            <h1 className="recipe-title">{food.name}</h1>

            {/* Metadata: Rating, Time, Servings */}
            <div className="recipe-metadata">
              <div className="rating-metadata">
                <span className="rating-value">{ratingValue.toFixed(1)}</span>
                <span className="rating-text">({ratingCount} reviews)</span>
                <div className="stars-inline">
                  {renderStars(ratingValue, false, 18)}
                </div>
              </div>
              
              <div className="time-metadata">
                <Clock size={18} />
                <span>{formatTime(totalTime)}</span>
              </div>
              
              <div className="servings-metadata">
                <Utensils size={18} />
                <span>{servings} Servings</span>
              </div>
            </div>

            {/* Description */}
            <p className="food-description">
              {recipe?.description || food.description || `A brief, enticing paragraph about this classic, layered pasta dish. Hearty, cheesy, and packed with flavor, this traditional ${food.cuisine} dish is the ultimate comfort food, perfect for family dinners and special occasions.`}
            </p>

            {/* Ingredients Section */}
            <div className="ingredients-section">
              <h2>Ingredients</h2>
              <div className="ingredients-list">
                {food.ingredients.map((ingredient, index) => {
                  const isSelected = selectedIngredients.has(index);
                  return (
                    <div 
                      key={index} 
                      className={`ingredient-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        const newSelected = new Set(selectedIngredients);
                        if (isSelected) {
                          newSelected.delete(index);
                        } else {
                          newSelected.add(index);
                        }
                        setSelectedIngredients(newSelected);
                      }}
                    >
                      <span className={`ingredient-checkbox ${isSelected ? 'selected' : ''}`}></span>
                      <span className="ingredient-name">{ingredient}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Instructions Section */}
            <div className="instructions-section">
              <h2>Instructions</h2>
              <div className="instructions-list">
                {instructions.map((instruction, index) => {
                  // Remove "[Instructions]" prefix and number prefix like "1) " if present
                  let cleanInstruction = instruction.replace(/^\[Instructions\]\s*/i, '');
                  cleanInstruction = cleanInstruction.replace(/^\d+\)\s*/, '');
                  return (
                    <div key={index} className="instruction-item">
                      <div className="step-number">{index + 1}</div>
                      <div className="step-content">{cleanInstruction}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Nutrition Section */}
            <div className="nutrition-section">
              <h3>Nutrition</h3>
              {recipe?.nutrition_calories ? (
                <div className="nutrition-info">
                  <p>Calories: {recipe.nutrition_calories} per serving</p>
                </div>
              ) : (
                <p className="nutrition-unavailable">Nutrition information is not available for this recipe.</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FoodDetail;

