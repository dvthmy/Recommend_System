import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Heart } from 'lucide-react';
import { apiService } from '../services/api';
import './History.css';

interface RecipeCard {
  id: string;
  title: string;
  image: string;
  cookTime: string;
  cuisine: string;
  rating?: number;
  lastView?: string;
  likeTime?: string;
  ratingTime?: string;
}

const History: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'liked' | 'rated' | 'viewed'>('viewed');
  const [recipes, setRecipes] = useState<RecipeCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [likedRecipes, setLikedRecipes] = useState<Set<string>>(new Set());

  useEffect(() => {
    loadLikedRecipes();
    loadRecipes();
  }, [activeTab]);

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
    e.stopPropagation(); // Prevent navigation
    
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
      
      // If in liked tab, remove from list
      if (activeTab === 'liked' && isLiked) {
        setRecipes(prev => prev.filter(r => r.id !== recipeId));
      }
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
      // Note: Unlike only sets liked=false in database, does NOT delete the recipe
      await loadLikedRecipes();
      
      // If unliked, remove from current display list if in liked tab
      // This only removes from UI, recipe still exists in database
      if (isLiked && activeTab === 'liked') {
        setRecipes(prev => prev.filter(r => r.id !== recipeId));
      } else if (!isLiked && activeTab === 'liked') {
        // If liked, reload recipes to show the new liked recipe in History
        await loadRecipes();
      }
      
      // Dispatch event to notify Profile component to reload stats
      // This updates the like count in Profile, but does NOT delete the recipe
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

  const loadRecipes = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        setError('User not found');
        setLoading(false);
        return;
      }

      let allRecipes: RecipeCard[] = [];

      if (activeTab === 'liked') {
        // Load liked recipes
        const likedResponse = await apiService.getUserInteractions(userId, 'like', 50, 0);
        if (likedResponse.data?.interactions) {
          for (const interaction of likedResponse.data.interactions) {
            try {
              const recipeResponse = await apiService.getRecipeDetail(interaction.recipe_id);
              if (recipeResponse.data) {
                allRecipes.push({
                  id: interaction.recipe_id,
                  title: recipeResponse.data.title,
                  image: (recipeResponse.data.image_urls && recipeResponse.data.image_urls.length > 0)
                    ? recipeResponse.data.image_urls[0]
                    : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
                  cookTime: recipeResponse.data.cook_time_min 
                    ? `${recipeResponse.data.cook_time_min} min` 
                    : 'Unknown',
                  cuisine: recipeResponse.data.cuisine || 'Unknown',
                  likeTime: (interaction as any).like_time || (interaction as any).timestamp
                });
              }
            } catch (err) {
              console.error('Failed to load recipe:', err);
            }
          }
        }
      } else if (activeTab === 'rated') {
        // Load rated recipes
        const ratedResponse = await apiService.getUserInteractions(userId, 'rating', 50, 0);
        if (ratedResponse.data?.interactions) {
          for (const interaction of ratedResponse.data.interactions) {
            if (interaction.rating) {
              try {
                const recipeResponse = await apiService.getRecipeDetail(interaction.recipe_id);
                if (recipeResponse.data) {
                  allRecipes.push({
                    id: interaction.recipe_id,
                    title: recipeResponse.data.title,
                    image: (recipeResponse.data.image_urls && recipeResponse.data.image_urls.length > 0)
                      ? recipeResponse.data.image_urls[0]
                      : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
                    cookTime: recipeResponse.data.cook_time_min 
                      ? `${recipeResponse.data.cook_time_min} min` 
                      : 'Unknown',
                    cuisine: recipeResponse.data.cuisine || 'Unknown',
                    rating: interaction.rating,
                    ratingTime: (interaction as any).rating_time || (interaction as any).timestamp
                  });
                }
              } catch (err) {
                console.error('Failed to load recipe:', err);
              }
            }
          }
        }
      } else if (activeTab === 'viewed') {
        // Load viewed recipes
        const viewedResponse = await apiService.getUserInteractions(userId, 'view', 50, 0);
        if (viewedResponse.data?.interactions) {
          for (const interaction of viewedResponse.data.interactions) {
            try {
              const recipeResponse = await apiService.getRecipeDetail(interaction.recipe_id);
              if (recipeResponse.data) {
                allRecipes.push({
                  id: interaction.recipe_id,
                  title: recipeResponse.data.title,
                  image: (recipeResponse.data.image_urls && recipeResponse.data.image_urls.length > 0)
                    ? recipeResponse.data.image_urls[0]
                    : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
                  cookTime: recipeResponse.data.cook_time_min 
                    ? `${recipeResponse.data.cook_time_min} min` 
                    : 'Unknown',
                  cuisine: recipeResponse.data.cuisine || 'Unknown',
                  lastView: (interaction as any).last_view || (interaction as any).timestamp
                });
              }
            } catch (err) {
              console.error('Failed to load recipe:', err);
            }
          }
        }
      }

      // Sort recipes by timestamp (most recent first)
      allRecipes.sort((a, b) => {
        const getTimestamp = (recipe: RecipeCard): number => {
          let timestampStr: string | undefined;
          if (activeTab === 'viewed') {
            timestampStr = recipe.lastView;
          } else if (activeTab === 'liked') {
            timestampStr = recipe.likeTime;
          } else if (activeTab === 'rated') {
            timestampStr = recipe.ratingTime;
          }
          
          if (!timestampStr) return 0;
          
          try {
            const date = new Date(timestampStr);
            return date.getTime();
          } catch {
            return 0;
          }
        };
        
        const timeA = getTimestamp(a);
        const timeB = getTimestamp(b);
        
        // Sort descending (most recent first)
        return timeB - timeA;
      });

      setRecipes(allRecipes);
    } catch (err) {
      console.error('Failed to load recipes:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recipes');
      // Fallback to mock data
      setRecipes(getMockRecipes());
    } finally {
      setLoading(false);
    }
  };

  const getMockRecipes = (): RecipeCard[] => {
    return [
      { id: '1', title: 'Spicy Thai Green Curry', image: 'https://images.unsplash.com/photo-1559314809-0d155014e29e?w=400&h=300&fit=crop', cookTime: '35 min', cuisine: 'Thai' },
      { id: '2', title: 'Classic Lasagna', image: 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=400&h=300&fit=crop', cookTime: '90 min', cuisine: 'Italian' },
      { id: '3', title: 'Lemon Herb Roast Chicken', image: 'https://images.unsplash.com/photo-1604503468506-a8da13d82791?w=400&h=300&fit=crop', cookTime: '75 min', cuisine: 'American' },
      { id: '4', title: 'Vegan Chocolate Avocado Mousse', image: 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=400&h=300&fit=crop', cookTime: '15 min', cuisine: 'Dessert' },
      { id: '5', title: 'Garlic Butter Shrimp Scampi', image: 'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=400&h=300&fit=crop', cookTime: '20 min', cuisine: 'Italian' },
      { id: '6', title: 'Quinoa Salad with Roasted Vegetables', image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop', cookTime: '40 min', cuisine: 'Healthy' },
      { id: '7', title: 'Homemade Margherita Pizza', image: 'https://images.unsplash.com/photo-1574071318508-1cdbab80d002?w=400&h=300&fit=crop', cookTime: '30 min', cuisine: 'Italian' },
      { id: '8', title: 'Hearty Beef Stew', image: 'https://images.unsplash.com/photo-1604909052743-94e838986d24?w=400&h=300&fit=crop', cookTime: '180 min', cuisine: 'Comfort Food' }
    ];
  };


  const formatTimeAgo = (dateString?: string | any): string => {
    if (!dateString) return '';
    
    try {
      let date: Date;
      
      // Handle Neo4j datetime format or ISO string
      if (typeof dateString === 'string') {
        // If it's already an ISO string, use it directly
        date = new Date(dateString);
      } else if (dateString && typeof dateString === 'object') {
        // Handle Neo4j datetime object (has epochSeconds or epochMillis)
        if (dateString.epochSeconds) {
          date = new Date(dateString.epochSeconds * 1000);
        } else if (dateString.epochMillis) {
          date = new Date(dateString.epochMillis);
        } else if (dateString.toString) {
          // Try to convert to string first
          date = new Date(dateString.toString());
        } else {
          return '';
        }
      } else {
        return '';
      }
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        console.error('Invalid date:', dateString);
        return '';
      }
      
      const now = new Date();
      const diffInMs = now.getTime() - date.getTime();
      
      // Check if diff is valid
      if (isNaN(diffInMs) || diffInMs < 0) {
        return 'Just now';
      }
      
      const diffInSeconds = Math.floor(diffInMs / 1000);
      const diffInMinutes = Math.floor(diffInSeconds / 60);
      const diffInHours = Math.floor(diffInMinutes / 60);
      const diffInDays = Math.floor(diffInHours / 24);
      const diffInWeeks = Math.floor(diffInDays / 7);
      const diffInMonths = Math.floor(diffInDays / 30);
      const diffInYears = Math.floor(diffInDays / 365);

      if (diffInSeconds < 60) {
        return 'Just now';
      } else if (diffInMinutes < 60) {
        return `${diffInMinutes} ${diffInMinutes === 1 ? 'minute' : 'minutes'} ago`;
      } else if (diffInHours < 24) {
        return `${diffInHours} ${diffInHours === 1 ? 'hour' : 'hours'} ago`;
      } else if (diffInDays < 7) {
        return `${diffInDays} ${diffInDays === 1 ? 'day' : 'days'} ago`;
      } else if (diffInWeeks < 4) {
        return `${diffInWeeks} ${diffInWeeks === 1 ? 'week' : 'weeks'} ago`;
      } else if (diffInMonths < 12) {
        return `${diffInMonths} ${diffInMonths === 1 ? 'month' : 'months'} ago`;
      } else {
        return `${diffInYears} ${diffInYears === 1 ? 'year' : 'years'} ago`;
      }
    } catch (err) {
      console.error('Failed to format date:', err, dateString);
      return '';
    }
  };

  if (loading) {
    return (
      <div className="activity-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading your activity...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="activity-container">
      <div className="container">
        {/* Header */}
        <div className="activity-header">
          <h1>My Activity</h1>
        </div>

        {/* Navigation Tabs */}
        <div className="activity-tabs">
          <button
            className={`tab-button ${activeTab === 'viewed' ? 'active' : ''}`}
            onClick={() => setActiveTab('viewed')}
          >
            Viewed
          </button>
          <button
            className={`tab-button ${activeTab === 'liked' ? 'active' : ''}`}
            onClick={() => setActiveTab('liked')}
          >
            Liked
          </button>
          <button
            className={`tab-button ${activeTab === 'rated' ? 'active' : ''}`}
            onClick={() => setActiveTab('rated')}
          >
            Rated
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <p>Error: {error}</p>
            <button onClick={loadRecipes} className="btn btn-outline btn-sm">
              Retry
            </button>
          </div>
        )}

        {/* Recipe Grid */}
        {recipes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h4>No recipes found</h4>
            <p>Start {activeTab === 'liked' ? 'liking' : activeTab === 'rated' ? 'rating' : 'viewing'} recipes to see them here</p>
          </div>
        ) : (
          <div className="recipe-grid">
            {recipes.map((recipe) => (
              <div
                key={recipe.id}
                className="recipe-card"
                onClick={() => navigate(`/food/${recipe.id}`)}
              >
                <div className="recipe-image-wrapper">
                  <img src={recipe.image} alt={recipe.title} className="recipe-image" />
                  <button
                    className={`history-heart-btn ${likedRecipes.has(recipe.id) ? 'liked' : ''}`}
                    onClick={(e) => toggleLike(recipe.id, e)}
                    aria-label={likedRecipes.has(recipe.id) ? 'Unlike recipe' : 'Like recipe'}
                    title={likedRecipes.has(recipe.id) ? 'Unlike recipe' : 'Like recipe'}
                  >
                    <Heart 
                      className="favorite-icon" 
                      size={20} 
                      strokeWidth={2}
                      fill={likedRecipes.has(recipe.id) ? '#FF6B35' : 'transparent'}
                      color={likedRecipes.has(recipe.id) ? '#FF6B35' : '#666666'}
                    />
                  </button>
                </div>
                <div className="recipe-info">
                  <h3 className="recipe-title">{recipe.title}</h3>
                  {activeTab === 'viewed' && recipe.lastView ? (
                    <div className="recipe-meta">
                      <div className="recipe-status">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="view-icon">
                          <path d="M8 2C4.5 2 1.73 4.61 1 8c.73 3.39 3.5 6 7 6s6.27-2.61 7-6c-.73-3.39-3.5-6-7-6zM8 12.5c-2.48 0-4.5-2.02-4.5-4.5S5.52 3.5 8 3.5s4.5 2.02 4.5 4.5-2.02 4.5-4.5 4.5z" fill="currentColor"/>
                          <path d="M8 6.5c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" fill="currentColor"/>
                        </svg>
                        <span className="viewed-badge">Viewed</span>
                        <span className="meta-separator">•</span>
                        <span className="time-ago">{formatTimeAgo(recipe.lastView)}</span>
                      </div>
                    </div>
                  ) : activeTab === 'liked' && recipe.likeTime ? (
                    <div className="recipe-meta">
                      <div className="recipe-status">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="heart-icon-small">
                          <path d="M13.3334 4C13.3334 2.15905 11.8413 0.666672 10.0001 0.666672C9.00008 0.666672 8.06675 1.07467 7.40008 1.73334C6.73341 1.07467 5.80008 0.666672 4.80008 0.666672C2.95875 0.666672 1.46675 2.15905 1.46675 4C1.46675 4.73334 1.73341 5.40001 2.16675 5.93334L7.40008 11.1667L12.6334 5.93334C13.0667 5.40001 13.3334 4.73334 13.3334 4Z" fill="currentColor"/>
                        </svg>
                        <span className="liked-badge">Liked</span>
                        <span className="meta-separator">•</span>
                        <span className="time-ago">{formatTimeAgo(recipe.likeTime)}</span>
                      </div>
                    </div>
                  ) : activeTab === 'rated' && recipe.ratingTime ? (
                    <div className="recipe-meta">
                      <div className="recipe-status">
                        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="star-icon-small">
                          <path d="M8 1L10.163 5.808L15 6.587L11.5 9.692L12.326 14.5L8 12.192L3.674 14.5L4.5 9.692L1 6.587L5.837 5.808L8 1Z" fill="currentColor"/>
                        </svg>
                        <span className="rated-badge">Rated {recipe.rating}⭐</span>
                        <span className="meta-separator">•</span>
                        <span className="time-ago">{formatTimeAgo(recipe.ratingTime)}</span>
                      </div>
                    </div>
                  ) : (
                    <p className="recipe-details">{recipe.cookTime} • {recipe.cuisine}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default History;
