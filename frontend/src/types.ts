export interface FoodHobby {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface DietaryRestriction {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface CookingSkillLevel {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface MealType {
  id: string;
  name: string;
  description: string;
  icon: string;
}

export interface CookingTimePreference {
  id: string;
  name: string;
  description: string;
  icon: string;
  maxMinutes: number;
}

export interface UserPreferences {
  favoriteCuisines: string[];
  dietaryRestrictions: string[];
  preferredMealTypes: string[];
  cookingTimePreference: string;
  favoriteDishes: string[];
  completedOnboarding: boolean;
}

export interface Ingredient {
  name: string;
  source: 'text' | 'image' | 'api';
  id?: string;
  category?: string;
  allergen?: boolean;
}

export interface FoodSuggestion {
  id: string;
  name: string;
  description: string;
  ingredients: string[];
  cookingTime: string;
  difficulty: 'Easy' | 'Medium' | 'Hard';
  image?: string;
  cuisine?: string;
  mealType?: string[];
  dietaryTags?: string[];
  maxMinutes?: number;
}
