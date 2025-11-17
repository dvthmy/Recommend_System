import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '../services/api';
import './History.css';

interface RecipeCard {
  id: string;
  title: string;
  image: string;
  cookTime: string;
  cuisine: string;
  rating?: number;
}

const History: React.FC = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'liked' | 'rated' | 'saved'>('liked');
  const [searchQuery, setSearchQuery] = useState('');
  const [recipes, setRecipes] = useState<RecipeCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRecipes();
  }, [activeTab]);

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
                  cuisine: recipeResponse.data.cuisine || 'Unknown'
                });
              }
            } catch (err) {
              console.error('Failed to load recipe:', err);
            }
          }
        }
      } else if (activeTab === 'rated') {
        // Load rated recipes
        const ratedResponse = await apiService.getUserInteractions(userId, 'like', 50, 0);
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
                    rating: interaction.rating
                  });
                }
              } catch (err) {
                console.error('Failed to load recipe:', err);
              }
            }
          }
        }
      } else if (activeTab === 'saved') {
        // Load saved recipes (using like as saved for now)
        const savedResponse = await apiService.getUserInteractions(userId, 'like', 50, 0);
        if (savedResponse.data?.interactions) {
          for (const interaction of savedResponse.data.interactions) {
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
                  cuisine: recipeResponse.data.cuisine || 'Unknown'
                });
              }
            } catch (err) {
              console.error('Failed to load recipe:', err);
            }
          }
        }
      }

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

  const filteredRecipes = recipes.filter(recipe =>
    recipe.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getSearchPlaceholder = () => {
    switch (activeTab) {
      case 'liked':
        return 'Search in my liked recipes...';
      case 'rated':
        return 'Search in my rated recipes...';
      case 'saved':
        return 'Search in my saved recipes...';
      default:
        return 'Search recipes...';
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
          <button
            className={`tab-button ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            Saved
          </button>
        </div>

        {/* Search Bar */}
        <div className="activity-search">
          <div className="search-input-wrapper">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" className="search-icon">
              <path d="M9 17A8 8 0 1 0 9 1a8 8 0 0 0 0 16z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="m19 19-4.35-4.35" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <input
              type="text"
              placeholder={getSearchPlaceholder()}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
          </div>
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
        {filteredRecipes.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <h4>No recipes found</h4>
            <p>Start {activeTab === 'liked' ? 'liking' : activeTab === 'rated' ? 'rating' : 'saving'} recipes to see them here</p>
          </div>
        ) : (
          <div className="recipe-grid">
            {filteredRecipes.map((recipe) => (
              <div
                key={recipe.id}
                className="recipe-card"
                onClick={() => navigate(`/food/${recipe.id}`)}
              >
                <div className="recipe-image-wrapper">
                  <img src={recipe.image} alt={recipe.title} className="recipe-image" />
                  <div className="heart-icon">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M17.5 5.83333C17.5 3.33333 15.4167 1.25 12.9167 1.25C11.6667 1.25 10.5 1.75 9.58333 2.58333C8.66667 1.75 7.5 1.25 6.25 1.25C3.75 1.25 1.66667 3.33333 1.66667 5.83333C1.66667 6.83333 2 7.75 2.58333 8.5L9.58333 15.5L16.5833 8.5C17.1667 7.75 17.5 6.83333 17.5 5.83333Z" fill="var(--color-primary)" stroke="var(--color-primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  </div>
                </div>
                <div className="recipe-info">
                  <h3 className="recipe-title">{recipe.title}</h3>
                  <p className="recipe-details">{recipe.cookTime} • {recipe.cuisine}</p>
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
