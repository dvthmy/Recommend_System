// API Configuration
export const API_CONFIG = {
  BASE_URL: 'http://localhost:8001',
  TIMEOUT: 10000, // 10 seconds
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000, // 1 second
};

// API Endpoints
export const API_ENDPOINTS = {
  // Health
  HEALTH: '/health',
  
  // Recommendations
  RECOMMEND: '/recommend',
  
  // User Management
  USER_PROFILE: (userId: string) => `/users/${userId}/profile`,
  USER_ALLERGIES: (userId: string) => `/users/${userId}/allergies`,
  USER_DISLIKES: (userId: string) => `/users/${userId}/dislikes`,
  USER_FAVORITE_CUISINES: (userId: string) => `/users/${userId}/favorite-cuisines`,
  USER_INTERACTIONS: (userId: string) => `/users/${userId}/interactions`,
  USER_INTERACTION_STATS: (userId: string) => `/users/${userId}/interactions/stats`,
  USER_RECOMPUTE_PROFILE: (userId: string) => `/users/${userId}/recompute-profile`,
  
  // Recipes
  RECIPE_DETAIL: (recipeId: string) => `/recipes/${recipeId}`,
  RECIPE_SEARCH: '/recipes/search',
  RECIPES_BY_CUISINE: (cuisine: string) => `/recipes/by-cuisine/${cuisine}`,
  
  // Ingredients
  INGREDIENTS: '/ingredients',
  INGREDIENT_DETAIL: (ingredientId: string) => `/ingredients/${ingredientId}`,
  INGREDIENT_SEARCH: '/ingredients/search',
  INGREDIENTS_BY_CATEGORY: (category: string) => `/ingredients/by-category/${category}`,
  INGREDIENT_SYNONYMS: (ingredientId: string) => `/ingredients/${ingredientId}/synonyms`,
  
  // Cuisines
  CUISINES: '/cuisines',
};

// Request Headers
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Resource not found.',
  UNAUTHORIZED: 'Unauthorized access.',
  FORBIDDEN: 'Access forbidden.',
  VALIDATION_ERROR: 'Invalid data provided.',
  TIMEOUT: 'Request timeout. Please try again.',
  UNKNOWN: 'An unknown error occurred.',
};

// Success Messages
export const SUCCESS_MESSAGES = {
  PROFILE_UPDATED: 'Profile updated successfully!',
  PREFERENCES_SAVED: 'Preferences saved successfully!',
  RECIPE_RATED: 'Recipe rated successfully!',
  RECIPE_SAVED: 'Recipe added to favorites!',
  INTERACTION_RECORDED: 'Interaction recorded successfully!',
  DATA_LOADED: 'Data loaded successfully!',
};
