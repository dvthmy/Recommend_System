import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { UserPreferences } from '../types';
import './Onboarding.css';

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const { user, updateUserProfile, isLoading, error } = useUser();
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [preferences, setPreferences] = useState<UserPreferences>({
    favoriteCuisines: [],
    dietaryRestrictions: [],
    preferredMealTypes: [],
    cookingTimePreference: '',
    favoriteDishes: [],
    completedOnboarding: false
  });

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

  const dietaryRestrictions = [
    { id: 'vegetarian', name: 'Vegetarian', description: 'No meat products' },
    { id: 'vegan', name: 'Vegan', description: 'No animal products' },
    { id: 'gluten_free', name: 'Gluten Free', description: 'Avoid wheat, barley' },
    { id: 'lactose_free', name: 'Lactose Free', description: 'Avoid dairy products' },
    { id: 'halal', name: 'Halal', description: 'Islamic dietary standards' },
    { id: 'kosher', name: 'Kosher', description: 'Jewish dietary standards' },
    { id: 'keto', name: 'Keto', description: 'Low carb diet' },
    { id: 'paleo', name: 'Paleo', description: 'Ancient diet' },
    { id: 'low_sodium', name: 'Low Sodium', description: 'Limit sodium intake' },
    { id: 'diabetic_friendly', name: 'Diabetic Friendly', description: 'Low sugar and carbs' }
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

  const popularDishes = [
    { id: 'pho', name: 'Pho Bo', cuisine: 'Vietnamese' },
    { id: 'banh_mi', name: 'Banh Mi', cuisine: 'Vietnamese' },
    { id: 'com_tam', name: 'Com Tam', cuisine: 'Vietnamese' },
    { id: 'bun_cha', name: 'Bun Cha', cuisine: 'Vietnamese' },
    { id: 'sushi', name: 'Sushi', cuisine: 'Japanese' },
    { id: 'ramen', name: 'Ramen', cuisine: 'Japanese' },
    { id: 'kimbap', name: 'Kimbap', cuisine: 'Korean' },
    { id: 'kimchi', name: 'Kimchi', cuisine: 'Korean' },
    { id: 'pad_thai', name: 'Pad Thai', cuisine: 'Thai' },
    { id: 'tom_yum', name: 'Tom Yum', cuisine: 'Thai' },
    { id: 'kung_pao', name: 'Kung Pao Chicken', cuisine: 'Chinese' },
    { id: 'fried_rice', name: 'Fried Rice', cuisine: 'Chinese' },
    { id: 'curry', name: 'Curry', cuisine: 'Indian' },
    { id: 'naan', name: 'Naan Bread', cuisine: 'Indian' },
    { id: 'pizza', name: 'Pizza', cuisine: 'Italian' },
    { id: 'pasta', name: 'Pasta', cuisine: 'Italian' },
    { id: 'croissant', name: 'Croissant', cuisine: 'French' },
    { id: 'ratatouille', name: 'Ratatouille', cuisine: 'French' },
    { id: 'tacos', name: 'Tacos', cuisine: 'Mexican' },
    { id: 'guacamole', name: 'Guacamole', cuisine: 'Mexican' }
  ];

  const steps = [
    { 
      title: 'Favorite Cuisines', 
      description: 'Which country\'s cuisine do you prefer?',
      subtitle: 'Select up to 5 countries'
    },
    { 
      title: 'Dietary Restrictions', 
      description: 'Do you have any dietary restrictions?',
      subtitle: 'Optional - skip if none'
    },
    { 
      title: 'Meal Types', 
      description: 'Which meal types are you interested in?',
      subtitle: 'Select your preferred meals'
    },
    { 
      title: 'Cooking Time', 
      description: 'How much time do you have for cooking?',
      subtitle: 'Choose the appropriate time range'
    },
    { 
      title: 'Favorite Dishes', 
      description: 'Select your top 5 favorite dishes',
      subtitle: 'Choose up to 5 dishes'
    }
  ];

  const handleCuisineToggle = (cuisineId: string) => {
    setPreferences(prev => ({
      ...prev,
      favoriteCuisines: prev.favoriteCuisines.includes(cuisineId)
        ? prev.favoriteCuisines.filter(id => id !== cuisineId)
        : prev.favoriteCuisines.length < 5 ? [...prev.favoriteCuisines, cuisineId] : prev.favoriteCuisines
    }));
  };

  const handleDietaryToggle = (restrictionId: string) => {
    setPreferences(prev => ({
      ...prev,
      dietaryRestrictions: prev.dietaryRestrictions.includes(restrictionId)
        ? prev.dietaryRestrictions.filter(id => id !== restrictionId)
        : [...prev.dietaryRestrictions, restrictionId]
    }));
  };

  const handleMealTypeToggle = (mealTypeId: string) => {
    setPreferences(prev => ({
      ...prev,
      preferredMealTypes: prev.preferredMealTypes.includes(mealTypeId)
        ? prev.preferredMealTypes.filter(id => id !== mealTypeId)
        : [...prev.preferredMealTypes, mealTypeId]
    }));
  };

  const handleCookingTimeSelect = (timeId: string) => {
    setPreferences(prev => ({
      ...prev,
      cookingTimePreference: timeId
    }));
  };

  const handleDishToggle = (dishId: string) => {
    setPreferences(prev => ({
      ...prev,
      favoriteDishes: prev.favoriteDishes.includes(dishId)
        ? prev.favoriteDishes.filter(id => id !== dishId)
        : prev.favoriteDishes.length < 5 ? [...prev.favoriteDishes, dishId] : prev.favoriteDishes
    }));
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const finishOnboarding = async () => {
    setIsSubmitting(true);
    
    try {
      // Use user ID from context
      if (!user?.user_id) {
        throw new Error('User not initialized');
      }

      // Map preferences to API format
      const maxCookTime = cookingTimeOptions.find(
        option => option.id === preferences.cookingTimePreference
      )?.minutes;

      const profileUpdate = {
        locale: 'vi-VN',
        skill_level: 'intermediate', // Default skill level
        max_cook_time: maxCookTime,
        dietary_preferences: preferences.dietaryRestrictions
      };

      // Update user profile
      await updateUserProfile(user.user_id, profileUpdate);

      // Add favorite cuisines
      for (const cuisineId of preferences.favoriteCuisines) {
        const cuisineName = cuisines.find(c => c.id === cuisineId)?.name;
        if (cuisineName) {
          await apiService.addUserFavoriteCuisine(user.user_id, {
            cuisine_name: cuisineName,
            preference_level: 5 // High preference for selected cuisines
          });
        }
      }

      // Save preferences to localStorage for backward compatibility
      const finalPreferences = {
        ...preferences,
        completedOnboarding: true
      };
      localStorage.setItem('userPreferences', JSON.stringify(finalPreferences));
      
      navigate('/upload');
    } catch (err) {
      console.error('Failed to save user preferences:', err);
      // Still navigate to upload page even if API fails
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

  const canProceed = () => {
    switch (currentStep) {
      case 0: return preferences.favoriteCuisines.length > 0;
      case 1: return true; // Optional step
      case 2: return preferences.preferredMealTypes.length > 0;
      case 3: return preferences.cookingTimePreference !== '';
      case 4: return preferences.favoriteDishes.length > 0;
      default: return false;
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
  return (
          <div className="step-content">
            <div className="options-grid">
              {cuisines.map(cuisine => (
                <div
                  key={cuisine.id}
                  className={`option-card ${preferences.favoriteCuisines.includes(cuisine.id) ? 'selected' : ''}`}
                  onClick={() => handleCuisineToggle(cuisine.id)}
                >
                  <div className="cuisine-flag">
                  </div>
                  <h3>{cuisine.name}</h3>
                  {preferences.favoriteCuisines.includes(cuisine.id) && (
                    <div className="selected-indicator">
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
            <p className="selection-counter">
              Selected {preferences.favoriteCuisines.length}/5 countries
            </p>
          </div>
        );

      case 1:
        return (
          <div className="step-content">
            <div className="options-grid">
              {dietaryRestrictions.map(restriction => (
                <div
                  key={restriction.id}
                  className={`option-card ${preferences.dietaryRestrictions.includes(restriction.id) ? 'selected' : ''}`}
                  onClick={() => handleDietaryToggle(restriction.id)}
                >
                  <h3>{restriction.name}</h3>
                  <p>{restriction.description}</p>
                  {preferences.dietaryRestrictions.includes(restriction.id) && (
                    <div className="selected-indicator">
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
            <p className="step-note">This step is optional - you can skip if you have no restrictions</p>
          </div>
        );

      case 2:
        return (
          <div className="step-content">
            <div className="options-grid">
              {mealTypes.map(mealType => (
                <div
                  key={mealType.id}
                  className={`option-card ${preferences.preferredMealTypes.includes(mealType.id) ? 'selected' : ''}`}
                  onClick={() => handleMealTypeToggle(mealType.id)}
                >
                  <div className="meal-icon">
                  </div>
                  <h3>{mealType.name}</h3>
                  {preferences.preferredMealTypes.includes(mealType.id) && (
                    <div className="selected-indicator">
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="step-content">
            <div className="options-grid single-select">
              {cookingTimeOptions.map(time => (
                <div
                  key={time.id}
                  className={`option-card ${preferences.cookingTimePreference === time.id ? 'selected' : ''}`}
                  onClick={() => handleCookingTimeSelect(time.id)}
                >
                  <h3>{time.name}</h3>
                  <p>{time.time}</p>
                  {preferences.cookingTimePreference === time.id && (
                    <div className="selected-indicator">
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="step-content">
            <div className="options-grid">
              {popularDishes.map(dish => (
                <div
                  key={dish.id}
                  className={`option-card ${preferences.favoriteDishes.includes(dish.id) ? 'selected' : ''}`}
                  onClick={() => handleDishToggle(dish.id)}
                >
                  <h3>{dish.name}</h3>
                  <p>{dish.cuisine}</p>
                  {preferences.favoriteDishes.includes(dish.id) && (
                    <div className="selected-indicator">
                      ✓
                    </div>
                  )}
                </div>
              ))}
            </div>
            <p className="selection-counter">
              Selected {preferences.favoriteDishes.length}/5 dishes
            </p>
          </div>
        );

      default:
        return null;
    }
  };

  const currentStepData = steps[currentStep];

  return (
    <div className="onboarding-container">
      <div className="container">
        <div className="onboarding-header">
          <h1>Welcome to FoodAI!</h1>
          <p>Help us understand your culinary preferences for perfect dish suggestions</p>
        </div>

        <div className="onboarding-content">
          <div className="step-indicator">
            <div className="step-progress">
              <div 
                className="progress-bar" 
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
            <div className="step-info">
              <span className="step-counter">Step {currentStep + 1} / {steps.length}</span>
              <div className="step-header">
                <div>
                  <h2>{currentStepData.title}</h2>
                  <p>{currentStepData.description}</p>
                  <span className="step-subtitle">{currentStepData.subtitle}</span>
                </div>
              </div>
            </div>
          </div>

          {renderStepContent()}

          {error && (
            <div className="error-message">
              <p>Error: {error}</p>
            </div>
          )}

          <div className="step-navigation">
            <button 
              className="btn btn-outline" 
              onClick={prevStep}
              disabled={currentStep === 0}
            >
              Back
            </button>
            
            {currentStep === steps.length - 1 ? (
              <button 
                className="btn btn-primary" 
                onClick={finishOnboarding}
                disabled={!canProceed() || isSubmitting}
              >
                {isSubmitting ? 'Saving...' : 'Finish'}
              </button>
            ) : (
              <button 
                className="btn btn-primary" 
                onClick={nextStep}
                disabled={!canProceed()}
              >
                Continue
              </button>
            )}
            </div>
        </div>
      </div>
    </div>
  );
};

export default Onboarding;