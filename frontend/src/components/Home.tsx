import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Star, Users, Heart } from 'lucide-react';
import { apiService } from '../services/api';
import { RecipeSearchRequest } from '../types/api';
import { FoodSuggestion } from '../types';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedDifficulty] = useState('');
  const [allFoods, setAllFoods] = useState<FoodSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cuisines] = useState([
    { id: 'american', name: 'American' },
    { id: 'chinese', name: 'Chinese' },
    { id: 'italian', name: 'Italian' },
    { id: 'mexican', name: 'Mexican' },
    { id: 'french', name: 'French' },
    { id: 'vietnamese', name: 'Vietnamese' },
    { id: 'japanese', name: 'Japanese' },
    { id: 'indian', name: 'Indian' },
    { id: 'mediterranean', name: 'Mediterranean' },
    { id: 'european', name: 'European' },
    { id: 'korean', name: 'Korean' },
    { id: 'british', name: 'British' },
    { id: 'thai', name: 'Thai' },
    { id: 'caribbean', name: 'Caribbean' },
  ]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [likedRecipes, setLikedRecipes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadRecipes();
    loadLikedRecipes();
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
          difficulty: 'Medium' as 'Easy' | 'Medium' | 'Hard', // Default difficulty
          cuisine: recipe.cuisine || 'Unknown',
          mealType: ['Lunch', 'Dinner'], // Default meal types
          dietaryTags: recipe.allergens || [],
          image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
          servings: recipe.servings,
          ratingValue: recipe.rating_value,
          ratingCount: recipe.rating_count
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
        cuisine: selectedCuisine && selectedCuisine !== 'No Preference' ? selectedCuisine : undefined,
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
          difficulty: 'Medium' as 'Easy' | 'Medium' | 'Hard',
          cuisine: recipe.cuisine || 'Unknown',
          mealType: ['Lunch', 'Dinner'],
          dietaryTags: recipe.allergens || [],
          image: recipe.image_urls?.[0] || 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
          servings: recipe.servings,
          ratingValue: recipe.rating_value,
          ratingCount: recipe.rating_count
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
        image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
        servings: 4,
        ratingValue: 4.9,
        ratingCount: 542
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
        image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
        servings: 2,
        ratingValue: 4.6,
        ratingCount: 298
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
        image: 'https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=400&h=300&fit=crop',
        servings: 3,
        ratingValue: 4.8,
        ratingCount: 415
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

  const loadLikedRecipes = async () => {
    // For guest users, load from localStorage
    const isGuest = !localStorage.getItem('access_token');
    if (isGuest) {
      try {
        const liked = JSON.parse(localStorage.getItem('likedRecipes') || '[]');
        setLikedRecipes(new Set(liked));
      } catch (err) {
        console.error('Failed to load liked recipes from localStorage:', err);
      }
      return;
    }

    // For registered users, load from backend
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    try {
      const response = await apiService.getUserInteractions(userId, 'like', 100, 0);
      if (response.data && response.data.interactions) {
        const liked = new Set(response.data.interactions.map((interaction: any) => interaction.recipe_id));
        setLikedRecipes(liked);
      }
    } catch (err) {
      console.error('Failed to load liked recipes:', err);
    }
  };

  const toggleLike = async (recipeId: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent double-click from triggering
    
    const isGuest = !localStorage.getItem('access_token');
    const isLiked = likedRecipes.has(recipeId);

    if (isGuest) {
      // For guest users, save to localStorage
      const newLiked = new Set(likedRecipes);
      if (isLiked) {
        newLiked.delete(recipeId);
      } else {
        newLiked.add(recipeId);
      }
      setLikedRecipes(newLiked);
      localStorage.setItem('likedRecipes', JSON.stringify(Array.from(newLiked)));
      return;
    }

    // For registered users, update backend
    const userId = localStorage.getItem('userId');
    if (!userId) {
      alert('Please sign in to like recipes.');
      return;
    }

    // Optimistic update: update UI immediately
    const newLiked = new Set(likedRecipes);
    if (isLiked) {
      newLiked.delete(recipeId);
    } else {
      newLiked.add(recipeId);
    }
    setLikedRecipes(newLiked);

    try {
      // Backend will toggle like/unlike automatically
      await apiService.recordUserInteraction(userId, {
        recipe_id: recipeId,
        event_type: 'like'
      });
      
      // Reload liked recipes from backend to sync
      await loadLikedRecipes();
      
      // Dispatch event to notify Profile component to reload stats
      window.dispatchEvent(new CustomEvent('interactionUpdated', { 
        detail: { type: 'like', recipeId, isLiked: !isLiked } 
      }));
    } catch (err) {
      console.error('Failed to toggle like:', err);
      // Revert optimistic update on error
      setLikedRecipes(likedRecipes);
      alert('Failed to update like. Please try again.');
    }
  };

  // No need for client-side filtering since we're using API search
  const filteredFoods = allFoods;

  const getServingsText = (servings?: number) => {
    if (!servings) return '1 serving';
    return `${servings} ${servings === 1 ? 'serving' : 'servings'}`;
  };

  const getRatingValueText = (rating?: number) => {
    if (rating === undefined || rating === null) {
      return '4.8';
    }
    return rating.toFixed(1);
  };

  const getRatingCountText = (count?: number) => {
    if (!count) return '0 ratings';
    return `${count.toLocaleString()} ratings`;
  };

  if (loading && allFoods.length === 0) {
    return (
      <div className="home-container">
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
    <div className="home-container">
      <div className="container">
        {/* Hero Section */}
        <div className="home-hero">
          <div className="hero-content">
            <h1 className="hero-title">
              Your Next Favorite Meal, Found.
            </h1>
            <p className="hero-description">
              Tell us what you like and what's in your fridge, and we'll find you the perfect recipe.
            </p>
            <div className="hero-actions">
              <button 
                className="btn btn-primary btn-lg"
                onClick={() => navigate('/onboarding')}
              >
                Get Started
              </button>
            </div>
          </div>
        </div>

        {/* Search and Filter Section */}
        <div className="search-filter-section">
          <div className="hero-search-wrapper">
            <div className="hero-search-input-wrapper">
              <input
                type="text"
                placeholder="Search by dish, ingredient, or keyword..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="hero-search-input"
              />
            </div>
            <div className="hero-cuisine-dropdown">
              <select
                value={selectedCuisine}
                onChange={(e) => setSelectedCuisine(e.target.value)}
                className="cuisine-select"
              >
                <option value="">All Cuisines</option>
                {cuisines.map(cuisine => (
                  <option key={cuisine.id} value={cuisine.name}>
                    {cuisine.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Recipe Section */}
        <div className="recipe-section">

          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
              <button onClick={() => loadRecipes()} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}

          <div className="foods-grid">
            {filteredFoods.map((food) => (
              <div
                key={food.id}
                className="food-card"
                onDoubleClick={() => handleViewDetails(food.id)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleViewDetails(food.id);
                  }
                }}
                aria-label={`View details for ${food.name}`}
              >
                <div className="card-image">
                  <img src={food.image} alt={food.name} />
                  <button
                    className="card-favorite-btn"
                    onClick={(e) => toggleLike(food.id, e)}
                    aria-label={likedRecipes.has(food.id) ? 'Unlike recipe' : 'Like recipe'}
                    title={likedRecipes.has(food.id) ? 'Unlike recipe' : 'Like recipe'}
                  >
                    <Heart 
                      className="favorite-icon" 
                      size={20} 
                      strokeWidth={2}
                      fill={likedRecipes.has(food.id) ? '#FF6B35' : 'transparent'}
                      color={likedRecipes.has(food.id) ? '#FF6B35' : '#666666'}
                    />
                  </button>
                </div>
                
                <div className="card-content">
                  <h3 className="home-recipe-title">{food.name}</h3>
                  
                  <div className="card-meta-rating-group">
                    <div className="card-meta">
                      <div className="meta-item">
                        <Clock className="meta-icon" size={16} strokeWidth={1.5} />
                        <span>{food.cookingTime}</span>
                      </div>
                      <div className="meta-item">
                        <Users className="meta-icon" size={16} strokeWidth={1.5} />
                        <span>{getServingsText(food.servings)}</span>
                      </div>
                    </div>

                    <div className="card-rating">
                      <Star className="rating-icon" size={16} strokeWidth={1.5} />
                      <span className="rating-number">{getRatingValueText(food.ratingValue)}</span>
                      <span className="rating-count">
                        ({getRatingCountText(food.ratingCount)})
                      </span>
                    </div>
                  </div>

                  <div className="card-cuisine-detail">
                    Cuisine: <strong>{food.cuisine || 'World'}</strong>
                  </div>

                  <div className="card-hint">
                    Double-click to view details
                  </div>
                </div>
              </div>
            ))}
          </div>

          {filteredFoods.length === 0 && !loading && (
            <div className="no-results">
              <div className="no-results-icon">🔍</div>
              <h3>No recipes found</h3>
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
    </div>
  );
};

export default Home;
