import React, { useState, useEffect } from 'react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { UserProfile, UserAllergiesResponse, UserDislikesResponse, UserCuisinesResponse } from '../types/api';
import { UserPreferences } from '../types';
import './Profile.css';

const Profile: React.FC = () => {
  const { user, allergies, dislikes, favoriteCuisines, loadUserProfile, loadUserAllergies, loadUserDislikes, loadUserFavoriteCuisines, isLoading, error } = useUser();
  const [preferences, setPreferences] = useState<UserPreferences>({
    favoriteCuisines: [],
    dietaryRestrictions: [],
    preferredMealTypes: [],
    cookingTimePreference: '',
    favoriteDishes: [],
    completedOnboarding: false
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    loadUserData();
    // Also load from localStorage for backward compatibility
    const storedPreferences = localStorage.getItem('userPreferences');
    if (storedPreferences) {
      setPreferences(JSON.parse(storedPreferences));
    }
  }, []);

  const loadUserData = async () => {
    const userId = localStorage.getItem('userId');
    if (userId) {
      await Promise.all([
        loadUserProfile(userId),
        loadUserAllergies(userId),
        loadUserDislikes(userId),
        loadUserFavoriteCuisines(userId)
      ]);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    
    try {
      const userId = localStorage.getItem('userId');
      if (!userId) {
        alert('User not found');
        return;
      }

      // Update user profile
      const profileUpdate = {
        locale: 'vi-VN',
        skill_level: 'intermediate',
        max_cook_time: getMaxCookTimeFromPreference(preferences.cookingTimePreference),
        dietary_preferences: preferences.dietaryRestrictions
      };

      await apiService.updateUserProfile(userId, profileUpdate);

      // Update favorite cuisines
      if (favoriteCuisines) {
        // Remove existing cuisines
        for (const cuisine of favoriteCuisines.favorite_cuisines) {
          await apiService.removeUserFavoriteCuisine(userId, cuisine.cuisine_name);
        }
      }

      // Add new favorite cuisines
      for (const cuisineId of preferences.favoriteCuisines) {
        const cuisineName = cuisineOptions.find(c => c.id === cuisineId)?.name;
        if (cuisineName) {
          await apiService.addUserFavoriteCuisine(userId, {
            cuisine_name: cuisineName,
            preference_level: 5
          });
        }
      }

      // Save to localStorage for backward compatibility
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      setIsEditing(false);
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to save profile:', err);
      alert('Failed to save profile. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const getMaxCookTimeFromPreference = (timePreference: string): number | undefined => {
    switch (timePreference) {
      case 'quick': return 15;
      case 'fast': return 30;
      case 'medium': return 60;
      case 'slow': return 120;
      case 'very_slow': return 180;
      default: return undefined;
    }
  };

  const handleCancel = () => {
    // Reload from localStorage
    const storedPreferences = localStorage.getItem('userPreferences');
    if (storedPreferences) {
      setPreferences(JSON.parse(storedPreferences));
    }
    setIsEditing(false);
  };

  const resetPreferences = async () => {
    if (window.confirm('Are you sure you want to reset all preferences?')) {
      try {
        const userId = localStorage.getItem('userId');
        if (userId) {
          // Reset profile
          await apiService.updateUserProfile(userId, {
            locale: 'vi-VN',
            skill_level: 'intermediate',
            max_cook_time: undefined,
            dietary_preferences: []
          });

          // Remove all favorite cuisines
          if (favoriteCuisines) {
            for (const cuisine of favoriteCuisines.favorite_cuisines) {
              await apiService.removeUserFavoriteCuisine(userId, cuisine.cuisine_name);
            }
          }
        }

        const defaultPreferences: UserPreferences = {
          favoriteCuisines: [],
          dietaryRestrictions: [],
          preferredMealTypes: [],
          cookingTimePreference: '',
          favoriteDishes: [],
          completedOnboarding: false
        };
        setPreferences(defaultPreferences);
        localStorage.setItem('userPreferences', JSON.stringify(defaultPreferences));
        alert('Preferences reset successfully!');
      } catch (err) {
        console.error('Failed to reset preferences:', err);
        alert('Failed to reset preferences. Please try again.');
      }
    }
  };

  const getTimePreferenceText = (time: string) => {
    switch (time) {
      case 'quick': return 'Very Fast (under 15 minutes)';
      case 'fast': return 'Fast (15-30 minutes)';
      case 'medium': return 'Medium (30-60 minutes)';
      case 'slow': return 'Slow (1-2 hours)';
      case 'very_slow': return 'Very Slow (over 2 hours)';
      default: return 'Not set';
    }
  };

  const cuisineOptions = [
    { id: 'vietnamese', name: 'Vietnamese' },
    { id: 'chinese', name: 'Chinese' },
    { id: 'japanese', name: 'Japanese' },
    { id: 'korean', name: 'Korean' },
    { id: 'thai', name: 'Thai' },
    { id: 'indian', name: 'Indian' },
    { id: 'italian', name: 'Italian' },
    { id: 'french', name: 'French' },
    { id: 'mexican', name: 'Mexican' },
    { id: 'american', name: 'American' }
  ];

  const dietaryOptions = [
    { id: 'vegetarian', name: 'Vegetarian', description: 'No meat products' },
    { id: 'vegan', name: 'Vegan', description: 'No animal products' },
    { id: 'gluten_free', name: 'Gluten Free', description: 'Avoid wheat, barley' },
    { id: 'lactose_free', name: 'Lactose Free', description: 'Avoid dairy products' },
    { id: 'halal', name: 'Halal', description: 'Islamic dietary standards' },
    { id: 'keto', name: 'Keto', description: 'Low carb diet' }
  ];

  const mealTypeOptions = [
    { id: 'breakfast', name: 'Breakfast' },
    { id: 'lunch', name: 'Lunch' },
    { id: 'dinner', name: 'Dinner' },
    { id: 'appetizer', name: 'Appetizer' },
    { id: 'dessert', name: 'Dessert' },
    { id: 'snack', name: 'Snack' }
  ];

  const timePreferenceOptions = [
    { id: 'quick', name: 'Very Fast', description: 'Under 15 minutes' },
    { id: 'fast', name: 'Fast', description: '15-30 minutes' },
    { id: 'medium', name: 'Medium', description: '30-60 minutes' },
    { id: 'slow', name: 'Slow', description: '1-2 hours' },
    { id: 'very_slow', name: 'Very Slow', description: 'Over 2 hours' }
  ];

  const popularDishes = [
    { id: 'pho', name: 'Pho Bo', cuisine: 'Vietnamese' },
    { id: 'banh_mi', name: 'Banh Mi', cuisine: 'Vietnamese' },
    { id: 'sushi', name: 'Sushi', cuisine: 'Japanese' },
    { id: 'pizza', name: 'Pizza', cuisine: 'Italian' },
    { id: 'curry', name: 'Curry', cuisine: 'Indian' },
    { id: 'tacos', name: 'Tacos', cuisine: 'Mexican' }
  ];

  const toggleCuisine = (cuisineId: string) => {
    setPreferences(prev => ({
      ...prev,
      favoriteCuisines: prev.favoriteCuisines.includes(cuisineId)
        ? prev.favoriteCuisines.filter(id => id !== cuisineId)
        : [...prev.favoriteCuisines, cuisineId]
    }));
  };

  const toggleDietaryRestriction = (restrictionId: string) => {
    setPreferences(prev => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restrictionId)
        ? prev.dietaryRestrictions.filter(id => id !== restrictionId)
        : [...prev.dietaryRestrictions, restrictionId]
    }));
  };

  const toggleMealType = (mealTypeId: string) => {
    setPreferences(prev => ({
      ...prev,
      preferredMealTypes: prev.preferredMealTypes.includes(mealTypeId)
        ? prev.preferredMealTypes.filter(id => id !== mealTypeId)
        : [...prev.preferredMealTypes, mealTypeId]
    }));
  };

  const toggleDish = (dishId: string) => {
    setPreferences(prev => ({
      ...prev,
      favoriteDishes: prev.favoriteDishes.includes(dishId)
        ? prev.favoriteDishes.filter(id => id !== dishId)
        : [...prev.favoriteDishes, dishId]
    }));
  };

  if (isLoading) {
    return (
      <div className="profile-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading profile...</h3>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="profile-container">
      <div className="container">
        <div className="profile-header">
          <div className="user-info">
            <div className="avatar">
            </div>
            <div className="user-details">
              <h1>User Profile</h1>
              <p>Manage your preferences and personal settings</p>
              {error && (
                <div className="error-message">
                  <p>Error: {error}</p>
                  <button onClick={loadUserData} className="btn btn-outline btn-sm">
                    Retry
                  </button>
                </div>
              )}
            </div>
          </div>
          <div className="profile-actions">
            {isEditing ? (
              <>
                <button className="btn btn-outline" onClick={handleCancel} disabled={isSaving}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={handleSave} disabled={isSaving}>
                  {isSaving ? 'Saving...' : 'Save Changes'}
                </button>
              </>
            ) : (
              <>
                <button className="btn btn-outline" onClick={resetPreferences}>
                  Reset
                </button>
                <button className="btn btn-primary" onClick={handleEdit}>
                  Edit
                </button>
              </>
            )}
          </div>
        </div>

        <div className="profile-content">
          <div className="preferences-grid">
            <div className="preference-section">
              <h3>Favorite Cuisines</h3>
              {isEditing ? (
                <div className="options-grid">
                  {cuisineOptions.map(cuisine => (
                    <div
                      key={cuisine.id}
                      className={`option-card ${preferences.favoriteCuisines.includes(cuisine.id) ? 'selected' : ''}`}
                      onClick={() => toggleCuisine(cuisine.id)}
                    >
                      <span className="cuisine-flag"></span>
                      <span>{cuisine.name}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="selected-items">
                  {preferences.favoriteCuisines.length === 0 ? (
                    <p className="empty-text">No cuisines selected</p>
                  ) : (
                    preferences.favoriteCuisines.map(cuisineId => {
                      const cuisine = cuisineOptions.find(c => c.id === cuisineId);
                      return cuisine ? (
                        <span key={cuisineId} className="selected-item">
                          <span></span>
                          <span>{cuisine.name}</span>
                        </span>
                      ) : null;
                    })
                  )}
                </div>
              )}
            </div>

            <div className="preference-section">
              <h3>Dietary Restrictions</h3>
              {isEditing ? (
                <div className="options-grid">
                  {dietaryOptions.map(restriction => (
                    <div
                      key={restriction.id}
                      className={`option-card ${preferences.dietaryRestrictions.includes(restriction.id) ? 'selected' : ''}`}
                      onClick={() => toggleDietaryRestriction(restriction.id)}
                    >
                      <span>{restriction.name}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="selected-items">
                  {preferences.dietaryRestrictions.length === 0 ? (
                    <p className="empty-text">No restrictions</p>
                  ) : (
                    preferences.dietaryRestrictions.map(restrictionId => {
                      const restriction = dietaryOptions.find(r => r.id === restrictionId);
                      return restriction ? (
                        <span key={restrictionId} className="selected-item">
                          <span>{restriction.name}</span>
                        </span>
                      ) : null;
                    })
                  )}
                </div>
              )}
            </div>

            <div className="preference-section">
              <h3>Favorite Meal Types</h3>
              {isEditing ? (
                <div className="options-grid">
                  {mealTypeOptions.map(mealType => (
                    <div
                      key={mealType.id}
                      className={`option-card ${preferences.preferredMealTypes.includes(mealType.id) ? 'selected' : ''}`}
                      onClick={() => toggleMealType(mealType.id)}
                    >
                      <span className="meal-icon"></span>
                      <span>{mealType.name}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="selected-items">
                  {preferences.preferredMealTypes.length === 0 ? (
                    <p className="empty-text">No meal types selected</p>
                  ) : (
                    preferences.preferredMealTypes.map(mealTypeId => {
                      const mealType = mealTypeOptions.find(m => m.id === mealTypeId);
                      return mealType ? (
                        <span key={mealTypeId} className="selected-item">
                          <span></span>
                          <span>{mealType.name}</span>
                        </span>
                      ) : null;
                    })
                  )}
                </div>
              )}
            </div>

            <div className="preference-section">
              <h3>Cooking Time</h3>
              {isEditing ? (
                <div className="radio-options">
                  {timePreferenceOptions.map(time => (
                    <label key={time.id} className="radio-option">
                      <input
                        type="radio"
                        name="timePreference"
                        value={time.id}
                        checked={preferences.cookingTimePreference === time.id}
                        onChange={(e) => setPreferences(prev => ({ ...prev, cookingTimePreference: e.target.value }))}
                      />
                      <div className="radio-content">
                        <div className="radio-title">{time.name}</div>
                        <div className="radio-description">{time.description}</div>
                      </div>
                    </label>
                  ))}
                </div>
              ) : (
                <p className="current-value">{getTimePreferenceText(preferences.cookingTimePreference)}</p>
              )}
            </div>

            <div className="preference-section">
              <h3>Favorite Dishes</h3>
              {isEditing ? (
                <div className="options-grid">
                  {popularDishes.map(dish => (
                    <div
                      key={dish.id}
                      className={`option-card ${preferences.favoriteDishes.includes(dish.id) ? 'selected' : ''}`}
                      onClick={() => toggleDish(dish.id)}
                    >
                      <span>{dish.name}</span>
                      <span className="dish-cuisine">{dish.cuisine}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="selected-items">
                  {preferences.favoriteDishes.length === 0 ? (
                    <p className="empty-text">No dishes selected</p>
                  ) : (
                    preferences.favoriteDishes.map(dishId => {
                      const dish = popularDishes.find(d => d.id === dishId);
                      return dish ? (
                        <span key={dishId} className="selected-item">
                          <span>{dish.name}</span>
                        </span>
                      ) : null;
                    })
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;