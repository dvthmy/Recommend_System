import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { UserPreferences } from '../types';
import './Onboarding.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile, loadUserAllergies, loadUserFavoriteCuisines, allergies, favoriteCuisines, error } = useUser();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences>({
    favoriteCuisines: [],
    dietaryRestrictions: [],
    preferredMealTypes: [],
    cookingTimePreference: '',
    favoriteDishes: [],
    completedOnboarding: false
  });
  
  // Allergies state
  const [selectedAllergies, setSelectedAllergies] = useState<string[]>([]);
  const [availableIngredients, setAvailableIngredients] = useState<AvailableIngredient[]>([]);
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [isMealTypeDropdownOpen, setIsMealTypeDropdownOpen] = useState(false);
  const mealTypeDropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadAvailableIngredients();
    const userId = localStorage.getItem('userId');
    if (userId) {
      loadUserAllergies(userId);
      loadUserFavoriteCuisines(userId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (mealTypeDropdownRef.current && !mealTypeDropdownRef.current.contains(event.target as Node)) {
        setIsMealTypeDropdownOpen(false);
      }
    };

    if (isMealTypeDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMealTypeDropdownOpen]);

  const loadAvailableIngredients = async () => {
    try {
      const ingredientsRes = await apiService.getIngredients();
      if (ingredientsRes.data && ingredientsRes.data.ingredients) {
        setAvailableIngredients(ingredientsRes.data.ingredients);
      }
    } catch (err) {
      console.error('Failed to load ingredients:', err);
    }
  };

  // Data constants
  const cuisines = [
    { id: 'vietnamese', name: 'Vietnamese' },
    { id: 'chinese', name: 'Chinese' },
    { id: 'japanese', name: 'Japanese' },
    { id: 'korean', name: 'Korean' },
    { id: 'thai', name: 'Thai' },
    { id: 'indian', name: 'Indian' },
    { id: 'italian', name: 'Italian' },
    { id: 'french', name: 'French' },
    { id: 'mexican', name: 'Mexican' },
    { id: 'american', name: 'American' },
    { id: 'mediterranean', name: 'Mediterranean' },
    { id: 'middle_eastern', name: 'Middle Eastern' }
  ];

  const mealTypes = [
    { id: 'breakfast', name: 'Breakfast' },
    { id: 'lunch', name: 'Lunch' },
    { id: 'dinner', name: 'Dinner' },
    { id: 'appetizer', name: 'Appetizer' },
    { id: 'dessert', name: 'Dessert' },
    { id: 'snack', name: 'Snack' },
    { id: 'brunch', name: 'Brunch' },
    { id: 'tea_time', name: 'Tea Time' }
  ];

  const cookingTimeOptions = [
    { id: 'quick', name: 'Very Fast', time: 'Under 15 minutes', minutes: 15 },
    { id: 'fast', name: 'Fast', time: '15-30 minutes', minutes: 30 },
    { id: 'medium', name: 'Medium', time: '30-60 minutes', minutes: 60 },
    { id: 'slow', name: 'Slow', time: '1-2 hours', minutes: 120 },
    { id: 'very_slow', name: 'Very Slow', time: 'Over 2 hours', minutes: 180 }
  ];

  // Slider values: 0, 15, 30, 45, 60, 75, 90, 105, 120, 135, 150, 165, 180 minutes
  const [cookingTimeMinutes, setCookingTimeMinutes] = useState(0);
  
  const getCookingTimeLabel = (minutes: number) => {
    if (minutes === 0) {
      return '0';
    } else if (minutes < 60) {
      return `${minutes} minutes`;
    } else {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      if (mins === 0) {
        return `${hours} ${hours === 1 ? 'hour' : 'hours'}`;
      }
      return `${hours}h ${mins}m`;
    }
  };

  const handleCookingTimeSliderChange = (minutes: number) => {
    setCookingTimeMinutes(minutes);
    // Map minutes to cooking time preference ID
    let timeId = '';
    if (minutes === 0) timeId = 'quick';
    else if (minutes <= 15) timeId = 'quick';
    else if (minutes <= 30) timeId = 'fast';
    else if (minutes <= 60) timeId = 'medium';
    else if (minutes <= 120) timeId = 'slow';
    else timeId = 'very_slow';
    
    setPreferences(prev => ({
      ...prev,
      cookingTimePreference: timeId
    }));
  };

  const sections = [
    { 
      id: 'cuisines',
      title: 'Favorite Cuisines', 
      description: 'Which country\'s cuisine do you prefer?',
      subtitle: 'Select up to 5 countries'
    },
    { 
      id: 'meals',
      title: 'Meal Types', 
      description: 'Which meal types are you interested in?',
      subtitle: 'Select your preferred meals'
    },
    { 
      id: 'time',
      title: 'Cooking Time', 
      description: 'How much time do you have for cooking?',
      subtitle: 'Choose the appropriate time range'
    }
  ];

  // Handlers
  const handleAddAllergy = (ingredientId: string) => {
    if (!selectedAllergies.includes(ingredientId)) {
      setSelectedAllergies([...selectedAllergies, ingredientId]);
      setIngredientSearch('');
    }
  };

  const handleRemoveAllergy = (ingredientId: string) => {
    setSelectedAllergies(selectedAllergies.filter(id => id !== ingredientId));
  };

  // Show all ingredients that match search, including selected ones
  const filteredIngredients = availableIngredients.filter(ingredient =>
    ingredient.name.toLowerCase().includes(ingredientSearch.toLowerCase())
  );

  // Check if search term matches any existing ingredient
  const exactMatch = availableIngredients.find(
    ing => ing.name.toLowerCase() === ingredientSearch.toLowerCase().trim()
  );

  // Check if we can add a new ingredient (search term doesn't match any existing ingredient)
  const canAddNewIngredient = ingredientSearch.trim() && 
    !exactMatch && 
    !selectedAllergies.some(id => {
      const ing = availableIngredients.find(i => i.id === id);
      return ing && ing.name.toLowerCase() === ingredientSearch.toLowerCase().trim();
    });

  const handleAddNewIngredient = () => {
    if (canAddNewIngredient) {
      // Create a temporary ID for the new ingredient
      const newIngredient: AvailableIngredient = {
        id: `custom-${Date.now()}`,
        name: ingredientSearch.trim()
      };
      // Add to available ingredients list
      setAvailableIngredients([...availableIngredients, newIngredient]);
      // Add to selected allergies
      setSelectedAllergies([...selectedAllergies, newIngredient.id]);
      setIngredientSearch('');
    }
  };

  const handleCuisineToggle = (cuisineId: string) => {
    setPreferences(prev => ({
      ...prev,
      favoriteCuisines: prev.favoriteCuisines.includes(cuisineId)
        ? prev.favoriteCuisines.filter(id => id !== cuisineId)
        : prev.favoriteCuisines.length < 5 ? [...prev.favoriteCuisines, cuisineId] : prev.favoriteCuisines
    }));
  };

  const handleMealTypeSelect = (mealTypeId: string) => {
    setPreferences(prev => ({
      ...prev,
      preferredMealTypes: mealTypeId ? [mealTypeId] : []
    }));
  };



  const finishOnboarding = async () => {
    setIsSubmitting(true);
    
    try {
      if (!user?.user_id) {
        throw new Error('User not initialized');
      }

      const maxCookTime = cookingTimeOptions.find(
        option => option.id === preferences.cookingTimePreference
      )?.minutes;

      const profileUpdate = {
        locale: 'vi-VN',
        skill_level: 'intermediate',
        max_cook_time: maxCookTime,
        dietary_preferences: []
      };

      await updateUserProfile(user.user_id, profileUpdate);

      const hasExistingAllergies = allergies?.allergies && allergies.allergies.length > 0;
      if (selectedAllergies.length > 0 && !hasExistingAllergies) {
        await apiService.addUserAllergies(user.user_id, { ingredient_ids: selectedAllergies });
      }

      const hasExistingCuisines = favoriteCuisines?.favorite_cuisines && favoriteCuisines.favorite_cuisines.length > 0;
      if (preferences.favoriteCuisines.length > 0 && !hasExistingCuisines) {
        for (const cuisineId of preferences.favoriteCuisines) {
          const cuisineName = cuisines.find(c => c.id === cuisineId)?.name;
          if (cuisineName) {
            await apiService.addUserFavoriteCuisine(user.user_id, {
              cuisine_name: cuisineName,
              preference_level: 5
            });
          }
        }
      }
      
      await loadUserAllergies(user.user_id);
      await loadUserFavoriteCuisines(user.user_id);

      const finalPreferences = {
        ...preferences,
        completedOnboarding: true
      };
      localStorage.setItem('userPreferences', JSON.stringify(finalPreferences));
      
      navigate('/suggestions');
    } catch (err) {
      console.error('Failed to save user preferences:', err);
      const finalPreferences = {
        ...preferences,
        completedOnboarding: true
      };
      localStorage.setItem('userPreferences', JSON.stringify(finalPreferences));
      navigate('/upload');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSubmit = () => {
    const hasExistingAllergies = allergies?.allergies && allergies.allergies.length > 0;
    const hasExistingCuisines = favoriteCuisines?.favorite_cuisines && favoriteCuisines.favorite_cuisines.length > 0;
    
    const allergiesValid = hasExistingAllergies || selectedAllergies.length >= 0;
    const cuisinesValid = hasExistingCuisines || preferences.favoriteCuisines.length > 0;
    
    return allergiesValid && 
           cuisinesValid &&
           preferences.preferredMealTypes.length > 0 && 
           preferences.cookingTimePreference !== '';
  };

  return (
    <div className="onboarding-container">
      <div className="container">
        <div className="onboarding-header">
          <h1>Welcome to FoodAI!</h1>
          <p>Help us understand your culinary preferences for perfect dish suggestions</p>
        </div>

        <div className="onboarding-content">
          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
            </div>
          )}

          {/* Ingredient Allergies Section */}
          {(!allergies || !allergies.allergies || allergies.allergies.length === 0) && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>What are your ingredient allergies?</h2>
              </div>
              <div className="allergy-layout-container">
                <div className="allergy-left-content">
                  <p className="section-description">Enter the ingredients you are allergic to</p>
                  <span className="section-subtitle">Optional - skip if none</span>
                </div>
                <div className="allergy-input-container">
                  <div className="allergy-search-wrapper">
                    <input
                      type="text"
                      placeholder="Search or add Ingredient"
                      value={ingredientSearch}
                      onChange={(e) => setIngredientSearch(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && canAddNewIngredient) {
                          handleAddNewIngredient();
                        }
                      }}
                      className="allergy-search-input"
                    />
                  {ingredientSearch && (filteredIngredients.length > 0 || canAddNewIngredient) && (
                    <div className="allergy-dropdown">
                      {filteredIngredients.slice(0, 10).map((ingredient: AvailableIngredient) => {
                        const isSelected = selectedAllergies.includes(ingredient.id);
                        return (
                          <div
                            key={ingredient.id}
                            className={`allergy-dropdown-item ${isSelected ? 'selected' : ''}`}
                            onClick={() => {
                              if (isSelected) {
                                handleRemoveAllergy(ingredient.id);
                              } else {
                                handleAddAllergy(ingredient.id);
                              }
                            }}
                          >
                            {isSelected && (
                              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="allergy-checkmark">
                                <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            )}
                            <span className={isSelected ? 'selected-text' : ''}>{ingredient.name}</span>
                          </div>
                        );
                      })}
                      {canAddNewIngredient && (
                        <div
                          className="allergy-dropdown-item add-new"
                          onClick={handleAddNewIngredient}
                        >
                          <span>Add "{ingredientSearch.trim()}"</span>
                        </div>
                      )}
                    </div>
                  )}
                  </div>
                  {selectedAllergies.length > 0 && (
                    <div className="allergy-tags-container">
                      {selectedAllergies.map(ingredientId => {
                        const ingredient = availableIngredients.find(ing => ing.id === ingredientId);
                        return ingredient ? (
                          <span key={ingredientId} className="allergy-tag">
                            {ingredient.name}
                            <button
                              className="allergy-tag-remove"
                              onClick={() => handleRemoveAllergy(ingredientId)}
                            >
                              ×
                            </button>
                          </span>
                        ) : null;
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Favorite Cuisines Section */}
          {(!favoriteCuisines || !favoriteCuisines.favorite_cuisines || favoriteCuisines.favorite_cuisines.length === 0) && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>{sections[0].title}</h2>
              </div>
              <div className="allergy-left-content">
                <p className="section-description">{sections[0].description}</p>
                <span className="section-subtitle">{sections[0].subtitle}</span>
              </div>
              <div className="options-grid options-grid-centered">
                {cuisines.map(cuisine => (
                  <div
                    key={cuisine.id}
                    className={`option-card ${preferences.favoriteCuisines.includes(cuisine.id) ? 'selected' : ''}`}
                    onClick={() => handleCuisineToggle(cuisine.id)}
                  >
                    <div className="cuisine-flag"></div>
                    <h3>{cuisine.name}</h3>
                    {preferences.favoriteCuisines.includes(cuisine.id) && (
                      <div className="selected-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>
              <p className="selection-counter">
                Selected {preferences.favoriteCuisines.length}/5 countries
              </p>
            </div>
          )}

          {/* Meal Types Section */}
          <div className="onboarding-section">
            <div className="section-header">
              <h2>{sections[1].title}</h2>
            </div>
            <div className="allergy-layout-container">
              <div className="allergy-left-content">
                <p className="section-description">{sections[1].description}</p>
                <span className="section-subtitle">{sections[1].subtitle}</span>
              </div>
              <div className="meal-type-dropdown-wrapper">
                <div className="custom-dropdown" ref={mealTypeDropdownRef}>
                  <div 
                    className="custom-dropdown-select"
                    onClick={() => setIsMealTypeDropdownOpen(!isMealTypeDropdownOpen)}
                  >
                    <span className="custom-dropdown-value">
                      {preferences.preferredMealTypes[0] 
                        ? mealTypes.find(m => m.id === preferences.preferredMealTypes[0])?.name || 'Select a meal type...'
                        : 'Select a meal type...'}
                    </span>
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                      <path d="M6 9L1 4h10z" fill="#9e9e9e"/>
                    </svg>
                  </div>
                  {isMealTypeDropdownOpen && (
                    <div className="custom-dropdown-list">
                      {mealTypes.map(mealType => (
                        <div
                          key={mealType.id}
                          className={`custom-dropdown-item ${preferences.preferredMealTypes[0] === mealType.id ? 'selected' : ''}`}
                          onClick={() => {
                            handleMealTypeSelect(mealType.id);
                            setIsMealTypeDropdownOpen(false);
                          }}
                        >
                          {mealType.name}
                          {preferences.preferredMealTypes[0] === mealType.id && (
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Cooking Time Section */}
          <div className="onboarding-section">
            <div className="section-header">
              <h2>{sections[2].title}</h2>
            </div>
            <div className="allergy-layout-container">
              <div className="allergy-left-content">
                <p className="section-description">{sections[2].description}</p>
                <span className="section-subtitle">{sections[2].subtitle}</span>
              </div>
              <div className="cooking-time-slider-wrapper">
                <div className="cooking-time-slider-container">
                  <div className="cooking-time-display">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="alarm-icon">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67V7z" fill="#2196F3"/>
                    </svg>
                    <span className="cooking-time-value">{getCookingTimeLabel(cookingTimeMinutes)}</span>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="180"
                    step="15"
                    value={cookingTimeMinutes}
                    onChange={(e) => handleCookingTimeSliderChange(parseInt(e.target.value))}
                    className="cooking-time-slider"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="onboarding-footer">
            <button 
              className="btn btn-primary btn-lg" 
              onClick={finishOnboarding}
              disabled={!canSubmit() || isSubmitting}
            >
              {isSubmitting ? 'Saving...' : 'Finish & Continue'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;
