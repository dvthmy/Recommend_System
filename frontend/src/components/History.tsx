import React, { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { UserInteractionStatsResponse } from '../types/api';
import './History.css';

interface RatingHistory {
  id: string;
  foodName: string;
  rating: number;
  date: string;
  ingredients: string[];
}

const History: React.FC = () => {
  const [ratingHistory, setRatingHistory] = useState<RatingHistory[]>([]);
  const [stats, setStats] = useState<UserInteractionStatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterPeriod, setFilterPeriod] = useState('all');

  useEffect(() => {
    loadUserHistory();
  }, []);

  const loadUserHistory = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        setError('User not found');
        setLoading(false);
        return;
      }

      // Load user interactions
            const interactionsResponse = await apiService.getUserInteractions(userId, 'like', 50, 0);
            if (interactionsResponse.data) {
        
        // Convert interactions to rating history format
        const historyData: RatingHistory[] = [];
        
        for (const interaction of interactionsResponse.data.interactions) {
          if (interaction.rating) {
            // Get recipe details to extract name and ingredients
            try {
              const recipeResponse = await apiService.getRecipeDetail(interaction.recipe_id);
              if (recipeResponse.data) {
                historyData.push({
                  id: interaction.interaction_id || interaction.recipe_id,
                  foodName: recipeResponse.data.title,
                  rating: interaction.rating,
                  date: interaction.timestamp ? new Date(interaction.timestamp).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
                  ingredients: recipeResponse.data.ingredients?.map(ing => ing.ingredient_name) || []
                });
              }
            } catch (err) {
              console.error('Failed to load recipe details for interaction:', err);
            }
          }
        }
        
        setRatingHistory(historyData);
      }

      // Load user stats
      const statsResponse = await apiService.getUserInteractionStats(userId);
      if (statsResponse.data) {
        setStats(statsResponse.data);
      }
    } catch (err) {
      console.error('Failed to load user history:', err);
      setError(err instanceof Error ? err.message : 'Failed to load history');
      
      // Fallback to localStorage data
      loadLocalStorageHistory();
    } finally {
      setLoading(false);
    }
  };

  const loadLocalStorageHistory = () => {
    const ratings = JSON.parse(localStorage.getItem('foodRatings') || '{}');
    const mockHistory: RatingHistory[] = Object.entries(ratings).map(([id, rating]) => ({
      id,
      foodName: `Recipe ${id}`,
      rating: rating as number,
      date: new Date().toISOString().split('T')[0],
      ingredients: []
    }));
    setRatingHistory(mockHistory);
  };

  const getFilteredHistory = () => {
    const now = new Date();
    const filtered = ratingHistory.filter(item => {
      const itemDate = new Date(item.date);
      const diffTime = Math.abs(now.getTime() - itemDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

      switch (filterPeriod) {
        case 'week':
          return diffDays <= 7;
        case 'month':
          return diffDays <= 30;
        case 'year':
          return diffDays <= 365;
        default:
          return true;
      }
    });

    return filtered.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
  };

  const getAverageRating = () => {
    if (stats?.stats.average_rating) {
      return stats.stats.average_rating.toFixed(1);
    }
    const filtered = getFilteredHistory();
    if (filtered.length === 0) return 0;
    const sum = filtered.reduce((acc, item) => acc + item.rating, 0);
    return (sum / filtered.length).toFixed(1);
  };

  const getRatingDistribution = () => {
    const filtered = getFilteredHistory();
    const distribution = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
    filtered.forEach(item => {
      distribution[item.rating as keyof typeof distribution]++;
    });
    return distribution;
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={`star ${i < rating ? 'filled' : ''}`}>
        ★
      </span>
    ));
  };

  const filteredHistory = getFilteredHistory();
  const averageRating = getAverageRating();
  const ratingDistribution = getRatingDistribution();

  if (loading) {
    return (
      <div className="history-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading your history...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="container">
        <div className="history-header">
          <h1>Rating History</h1>
          <p>Track dishes you've rated and preference trends</p>
          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
              <button onClick={loadUserHistory} className="btn btn-outline btn-sm">
                Retry
              </button>
            </div>
          )}
        </div>

        <div className="history-stats">
          <div className="stats-card">
            <h3>Total Ratings</h3>
            <div className="stat-value">{stats?.stats.like_count || filteredHistory.length}</div>
          </div>
          <div className="stats-card">
            <h3>Average Rating</h3>
            <div className="stat-value">{averageRating}/5</div>
          </div>
          <div className="stats-card">
            <h3>Favorite Dishes</h3>
            <div className="stat-value">
              {filteredHistory.filter(item => item.rating >= 4).length}
            </div>
          </div>
          {stats && (
            <div className="stats-card">
              <h3>Total Interactions</h3>
              <div className="stat-value">{stats.stats.total_interactions}</div>
            </div>
          )}
        </div>

        <div className="filter-section">
          <label className="form-label">Filter by time:</label>
          <select
            value={filterPeriod}
            onChange={(e) => setFilterPeriod(e.target.value)}
            className="form-input"
          >
            <option value="all">All</option>
            <option value="week">Last 7 days</option>
            <option value="month">Last 30 days</option>
            <option value="year">Last year</option>
          </select>
        </div>

        <div className="history-content">
          <div className="rating-chart">
            <h3>Rating Distribution</h3>
            <div className="chart-bars">
              {[5, 4, 3, 2, 1].map(rating => (
                <div key={rating} className="chart-bar">
                  <div className="bar-label">
                    <span className="stars">{renderStars(rating)}</span>
                    <span className="count">{ratingDistribution[rating as keyof typeof ratingDistribution]}</span>
                  </div>
                  <div className="bar-container">
                    <div 
                      className="bar-fill"
                      style={{ 
                        width: `${filteredHistory.length > 0 ? 
                          (ratingDistribution[rating as keyof typeof ratingDistribution] / filteredHistory.length) * 100 : 0}%` 
                      }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rating-history">
            <h3>Rating History ({filteredHistory.length})</h3>
            {filteredHistory.length === 0 ? (
              <div className="empty-state">
                <div className="empty-icon"></div>
                <h4>No ratings yet</h4>
                <p>Start rating dishes to see history here</p>
              </div>
            ) : (
              <div className="history-list">
                {filteredHistory.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="item-header">
                      <h4>{item.foodName}</h4>
                      <div className="rating-display">
                        {renderStars(item.rating)}
                      </div>
                    </div>
                    <div className="item-meta">
                      <span className="date">{new Date(item.date).toLocaleDateString('en-US')}</span>
                      <div className="ingredients">
                        {item.ingredients.slice(0, 3).map((ingredient, index) => (
                          <span key={index} className="ingredient-tag">
                            {ingredient}
                          </span>
                        ))}
                        {item.ingredients.length > 3 && (
                          <span className="ingredient-tag more">
                            +{item.ingredients.length - 3}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default History;
