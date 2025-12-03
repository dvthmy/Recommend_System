import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import { RecipeDetail } from '../types/api';
import { FoodSuggestion } from '../types';
import { getUserId } from '../utils/auth';
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
  const [showFullNutrition, setShowFullNutrition] = useState<boolean>(false);

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
        
        // Load liked status and user rating
        await loadLikedStatus(recipeId);
        await loadUserRating(recipeId);

        // Only record view for registered users, not guests
        if (recordView && !isGuestUser()) {
          const userId = getUserId();
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
    const userId = getUserId();
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

  const loadUserRating = async (recipeId: string) => {
    const isGuest = isGuestUser();
    
    if (isGuest) {
      setUserRating(0);
      return;
    }

    const userId = getUserId();
    if (!userId) {
      setUserRating(0);
      return;
    }

    try {
      // Fetch user's rating interactions
      const response = await apiService.getUserInteractions(userId, 'rating', 100, 0);
      if (response.data && response.data.interactions) {
        const ratingInteraction = response.data.interactions.find(
          (interaction: any) => interaction.recipe_id === recipeId
        );
        
        if (ratingInteraction && ratingInteraction.rating) {
          setUserRating(ratingInteraction.rating);
        } else {
          setUserRating(0);
        }
      } else {
        setUserRating(0);
      }
    } catch (err) {
      console.error('Failed to load user rating:', err);
      setUserRating(0);
    }
  };

  // Convert API recipe to FoodSuggestion format for display
  const food: FoodSuggestion | null = recipe ? {
    id: recipe.recipe_id,
    name: recipe.title,
    description: recipe.description || `Delicious ${recipe.cuisine} dish`,
    // Use ingredients_list from CSV (full string with quantity/unit)
    ingredients: recipe.ingredients_list || [],
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
      alert('Please sign in to rate recipes. Your rating will not be saved.');
      return;
    }
    
    const userId = getUserId();
    if (userId && recipe) {
      try {
        // Submit rating to backend
        await apiService.recordUserInteraction(userId, {
          recipe_id: recipe.recipe_id,
          event_type: 'rating',
          rating: rating
        });
        
        // Update local state
        setUserRating(rating);
        
        // Reload recipe to get updated average rating and count
        await loadRecipeDetail(id!, false);
      } catch (err) {
        console.error('❌ Failed to rate recipe:', err);
        alert('❌ Failed to submit rating. Please try again.');
      }
    }
  };

  const handleRemoveRating = async () => {
    if (isGuestUser()) return;
    
    const userId = getUserId();
    if (userId && recipe) {
      try {
        // Remove rating via DELETE endpoint
        await apiService.removeUserRating(userId, recipe.recipe_id);
        
        // Update local state
        setUserRating(0);
        
        // Reload recipe to get updated average rating and count
        await loadRecipeDetail(id!, false);
      } catch (err: any) {
        console.error('❌ Failed to remove rating:', err);
        
        // Check for specific error
        if (err?.response?.status === 404) {
          console.warn('⚠️ No rating found, resetting UI state');
          setUserRating(0);
        } else {
          alert('❌ Failed to remove rating. Please try again.');
        }
      }
    }
  };

  const handleStarClick = async (starValue: number) => {
    if (isGuestUser()) {
      alert('Please sign in to rate recipes.');
      return;
    }

    // If clicking the same star twice, remove rating
    if (userRating === starValue) {
      await handleRemoveRating();
    } else {
      // Submit new rating immediately
      await handleRate(starValue);
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
    const userId = getUserId();
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
      // More accurate star filling logic
      const isFilled = i <= displayRating;
      const isHalfFilled = !isFilled && i === Math.ceil(displayRating) && displayRating % 1 >= 0.5;
      
      stars.push(
        <Star
          key={i}
          className={`star ${isFilled || isHalfFilled ? 'filled' : ''}`}
          size={size}
          fill={isFilled ? 'currentColor' : isHalfFilled ? 'url(#half)' : 'none'}
          strokeWidth={1.5}
          onMouseEnter={interactive ? () => setHoveredStar(i) : undefined}
          onMouseLeave={interactive ? () => setHoveredStar(0) : undefined}
          onClick={interactive ? () => handleStarClick(i) : undefined}
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
            onClick={() => navigate('/suggestions')}
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
          onClick={() => navigate('/suggestions')}
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
            
            {/* Description */}
            <p className="food-description">
              {recipe?.description || food.description || `A delicious ${food.cuisine} dish perfect for any occasion.`}
            </p>
            
            {/* Recipe Source URL (small text below description) */}
            {recipe?.url && (
              <div className="recipe-source-url">
                <a 
                  href={recipe.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="recipe-url-link"
                >
                  🔗 {new URL(recipe.url).hostname}
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 10H2V2h4V1H2C1.45 1 1 1.45 1 2v8c0 .55.45 1 1 1h8c.55 0 1-.45 1-1V6h-1v4zM7 1v1h2.59L3.76 7.83l.71.71L10.3 2.71V5h1V1H7z" fill="currentColor"/>
                  </svg>
                </a>
              </div>
            )}

            {/* Metadata: Rating, Time, Servings */}
            <div className="recipe-metadata">
              <div className="rating-metadata">
                <span className="rating-value">{ratingValue.toFixed(1)}</span>
                <span className="rating-text">
                  ({ratingCount} {ratingCount === 1 ? 'rating' : 'ratings'}
                  {recipe?.review_count ? `, ${recipe.review_count} ${recipe.review_count === 1 ? 'review' : 'reviews'}` : ''})
                </span>
                <div className="stars-inline">
                  {renderStars(ratingValue, false, 18)}
                </div>
              </div>
              
              <div className="time-metadata">
                <Clock size={18} />
                <span>
                  {recipe?.prep_time_min && `Prep: ${formatTime(recipe.prep_time_min)}`}
                  {recipe?.prep_time_min && recipe?.cook_time_min && ' | '}
                  {recipe?.cook_time_min && `Cook: ${formatTime(recipe.cook_time_min)}`}
                  {!recipe?.prep_time_min && !recipe?.cook_time_min && formatTime(totalTime)}
                </span>
              </div>
              
              <div className="servings-metadata">
                <Utensils size={18} />
                <span>
                  {servings ? `${servings} ${servings === 1 ? 'Serving' : 'Servings'}` : ''}
                  {recipe?.yield && (!servings || recipe.yield !== servings.toString()) && (servings ? ' | ' : '') + recipe.yield}
                  {!servings && !recipe?.yield && 'Servings unknown'}
                </span>
              </div>
            </div>
            
            {/* User Rating Section - Below metadata */}
            {!isGuestUser() && (
              <div className="user-rating-section-standalone">
                <span className="rate-prompt-inline">
                  {userRating > 0 ? '⭐ Your rating:' : '🌟 Rate this recipe:'}
                </span>
                <div className="interactive-stars-inline">
                  {renderStars(userRating, true, 24)}
                </div>
                {userRating > 0 && (
                  <span className="rating-hint">Click again to remove</span>
                )}
              </div>
            )}

            {/* Ingredients Section */}
            <div className="ingredients-section">
              <h2>Ingredients</h2>
              <div className="ingredients-list">
                {recipe?.ingredients_list && recipe.ingredients_list.length > 0 ? (
                  recipe.ingredients_list.map((ingredient, index) => {
                    const isSelected = selectedIngredients.has(index);
                    // Ensure ingredient is a string and trim whitespace
                    const ingredientText = typeof ingredient === 'string' 
                      ? ingredient.trim() 
                      : String(ingredient).trim();
                    
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
                        <span className="ingredient-name">{ingredientText}</span>
                      </div>
                    );
                  })
                ) : (
                  <p>No ingredient information available</p>
                )}
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
                      <div className="step-label">Step {index + 1}</div>
                      <div className="step-content">{cleanInstruction}</div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Nutrition Section */}
            <div className="nutrition-section">
              <h2>Nutrition Facts <small className="per-serving-text">(per serving)</small></h2>
              {recipe?.nutrition_calories ? (
                <>
                  {/* Summary View - 4 basic nutrients */}
                  {!showFullNutrition && (
                    <div className="nutrition-summary">
                      <div className="nutrition-summary-grid">
                        <div className="nutrition-summary-item">
                          <span className="nutrition-summary-value">{Math.round(recipe.nutrition_calories)}</span>
                          <span className="nutrition-summary-label">Calories</span>
                        </div>
                        {recipe.nutrition_total_fat && (
                          <div className="nutrition-summary-item">
                            <span className="nutrition-summary-value">{recipe.nutrition_total_fat.toFixed(1)}g</span>
                            <span className="nutrition-summary-label">Fat</span>
                          </div>
                        )}
                        {recipe.nutrition_total_carbohydrate && (
                          <div className="nutrition-summary-item">
                            <span className="nutrition-summary-value">{recipe.nutrition_total_carbohydrate.toFixed(1)}g</span>
                            <span className="nutrition-summary-label">Carbs</span>
                          </div>
                        )}
                        {recipe.nutrition_protein && (
                          <div className="nutrition-summary-item">
                            <span className="nutrition-summary-value">{recipe.nutrition_protein.toFixed(1)}g</span>
                            <span className="nutrition-summary-label">Protein</span>
                          </div>
                        )}
                      </div>
                      <button 
                        className="nutrition-toggle-button"
                        onClick={() => setShowFullNutrition(true)}
                      >
                        Show Full Nutrition Label
                      </button>
                    </div>
                  )}
                  
                  {/* Full Nutrition Label - USDA Style */}
                  {showFullNutrition && (
                <div className="nutrition-label-container">
                  {/* Servings Info */}
                  {recipe.servings && (
                    <div className="nutrition-servings-info">
                      Servings Per Recipe: <strong>{recipe.servings}</strong>
                    </div>
                  )}
                  
                  {/* Calories - Highlighted */}
                  <div className="nutrition-row nutrition-calories-row">
                    <span className="nutrition-label-text">Calories</span>
                    <span className="nutrition-value-text">{Math.round(recipe.nutrition_calories)}</span>
                  </div>
                  
                  <div className="nutrition-divider"></div>
                  
                  {/* Nutrients with % Daily Value */}
                  <div className="nutrition-dv-header">
                    <span style={{ textAlign: 'right', width: '100%', fontSize: '12px', fontWeight: 'bold' }}>% Daily Value *</span>
                  </div>
                  
                  {/* Total Fat */}
                  {recipe.nutrition_total_fat && (
                    <>
                      <div className="nutrition-row">
                        <span className="nutrition-label-text"><strong>Total Fat</strong> {recipe.nutrition_total_fat.toFixed(1)}g</span>
                        <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_total_fat / 78) * 100)}%</strong></span>
                      </div>
                      {/* Saturated Fat - Indented */}
                      {recipe.nutrition_saturated_fat && (
                        <div className="nutrition-row nutrition-row-indent">
                          <span className="nutrition-label-text">Saturated Fat {recipe.nutrition_saturated_fat.toFixed(1)}g</span>
                          <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_saturated_fat / 20) * 100)}%</strong></span>
                        </div>
                      )}
                    </>
                  )}
                  
                  {/* Cholesterol */}
                  {recipe.nutrition_cholesterol && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text"><strong>Cholesterol</strong> {Math.round(recipe.nutrition_cholesterol)}mg</span>
                      <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_cholesterol / 300) * 100)}%</strong></span>
                    </div>
                  )}
                  
                  {/* Sodium */}
                  {recipe.nutrition_sodium && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text"><strong>Sodium</strong> {Math.round(recipe.nutrition_sodium)}mg</span>
                      <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_sodium / 2300) * 100)}%</strong></span>
                    </div>
                  )}
                  
                  {/* Total Carbohydrate */}
                  {recipe.nutrition_total_carbohydrate && (
                    <>
                      <div className="nutrition-row">
                        <span className="nutrition-label-text"><strong>Total Carbohydrate</strong> {recipe.nutrition_total_carbohydrate.toFixed(1)}g</span>
                        <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_total_carbohydrate / 275) * 100)}%</strong></span>
                      </div>
                      {/* Dietary Fiber - Indented */}
                      {recipe.nutrition_dietary_fiber && (
                        <div className="nutrition-row nutrition-row-indent">
                          <span className="nutrition-label-text">Dietary Fiber {recipe.nutrition_dietary_fiber.toFixed(1)}g</span>
                          <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_dietary_fiber / 28) * 100)}%</strong></span>
                        </div>
                      )}
                      {/* Total Sugars - Indented */}
                      {recipe.nutrition_total_sugars && (
                        <div className="nutrition-row nutrition-row-indent">
                          <span className="nutrition-label-text">Total Sugars {recipe.nutrition_total_sugars.toFixed(1)}g</span>
                        </div>
                      )}
                    </>
                  )}
                  
                  {/* Protein */}
                  {recipe.nutrition_protein && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text"><strong>Protein</strong> {recipe.nutrition_protein.toFixed(1)}g</span>
                      <span className="nutrition-dv-text"><strong>{Math.round((recipe.nutrition_protein / 50) * 100)}%</strong></span>
                    </div>
                  )}
                  
                  <div className="nutrition-divider"></div>
                  
                  {/* Vitamins and Minerals */}
                  {recipe.nutrition_vitamin_c !== undefined && recipe.nutrition_vitamin_c !== null && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text">Vitamin C {Math.round(recipe.nutrition_vitamin_c)}mg</span>
                      <span className="nutrition-dv-text">{Math.round((recipe.nutrition_vitamin_c / 90) * 100)}%</span>
                    </div>
                  )}
                  
                  {recipe.nutrition_calcium !== undefined && recipe.nutrition_calcium !== null && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text">Calcium {Math.round(recipe.nutrition_calcium)}mg</span>
                      <span className="nutrition-dv-text">{Math.round((recipe.nutrition_calcium / 1300) * 100)}%</span>
                    </div>
                  )}
                  
                  {recipe.nutrition_iron !== undefined && recipe.nutrition_iron !== null && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text">Iron {Math.round(recipe.nutrition_iron)}mg</span>
                      <span className="nutrition-dv-text">{Math.round((recipe.nutrition_iron / 18) * 100)}%</span>
                    </div>
                  )}
                  
                  {recipe.nutrition_potassium !== undefined && recipe.nutrition_potassium !== null && (
                    <div className="nutrition-row">
                      <span className="nutrition-label-text">Potassium {Math.round(recipe.nutrition_potassium)}mg</span>
                      <span className="nutrition-dv-text">{Math.round((recipe.nutrition_potassium / 4700) * 100)}%</span>
                    </div>
                  )}
                  
                  <div className="nutrition-divider"></div>
                  
                  {/* Footnotes */}
                  <div className="nutrition-footnote">
                    <p>* Percent Daily Values are based on a 2,000 calorie diet. Your daily values may be higher or lower depending on your calorie needs.</p>
                    <p style={{ marginTop: '8px' }}>** Nutrient information is not available for all ingredients. Amount is based on available nutrient data.</p>
                    <p style={{ marginTop: '8px' }}>(-) Information is not currently available for this nutrient. If you are following a medically restrictive diet, please consult your doctor or registered dietitian before preparing this recipe for personal consumption.</p>
                  </div>
                  
                  <button 
                    className="nutrition-toggle-button nutrition-toggle-hide"
                    onClick={() => setShowFullNutrition(false)}
                  >
                    Hide Full Label
                  </button>
                </div>
                  )}
                </>
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

