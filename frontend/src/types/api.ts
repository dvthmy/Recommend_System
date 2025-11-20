// API Types for Recommend Service Integration

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// User Profile Types
export interface UserProfile {
  user_id: string;
  username?: string;
  name?: string;
  age?: number;
  gender?: string;
  locale?: string;
  skill_level?: string;
  max_cook_time?: number;
  dietary_preferences?: string[];
  completed_onboarding?: boolean;  // Track if user completed onboarding
  created_at?: string;
  updated_at?: string;
  access_token?: string;
  token_type?: string;
}

export interface UserProfileUpdate {
  username?: string;
  name?: string;
  age?: number;
  gender?: string;
  locale?: string;
  skill_level?: string;
  max_cook_time?: number;
  dietary_preferences?: string[];
  completed_onboarding?: boolean;  // Track if user completed onboarding
}

// Allergy and Dislike Types
export interface AllergyInfo {
  ingredient_id: string;
  ingredient_name: string;
  category?: string;
  severity?: string;
}

export interface DislikeInfo {
  ingredient_id: string;
  ingredient_name: string;
  category?: string;
  reason?: string;
}

export interface CuisinePreference {
  cuisine_name: string;
  preference_level: number;
  added_at?: string;
}

// Recipe Types
export interface RecipeIngredient {
  ingredient_id: string;
  ingredient_name: string;
  quantity?: string;
  unit?: string;
  is_optional: boolean;
  preparation?: string;
}

export interface RecipeDetail {
  recipe_id: string;
  title: string;
  cuisine?: string;
  cook_time_min?: number;
  prep_time_min?: number;
  total_time_min?: number;
  servings?: number;
  rating_value?: number;
  rating_count?: number;
  review_count?: number;
  description?: string;
  instructions?: string;
  tags?: string[];
  image_urls?: string[];
  popularity_views?: number;
  popularity_saves?: number;
  popularity_cooks?: number;
  popularity_likes?: number;
  allergens?: string[];
  nutrition_calories?: number;
  equipment_needed?: string[];
  alternative_ingredients?: string[];
  ingredients?: RecipeIngredient[];
  created_at?: string;
  updated_at?: string;
}

export interface RecipeSummary {
  recipe_id: string;
  title: string;
  cuisine?: string;
  cook_time_min?: number;
  servings?: number;
  tags?: string[];
  image_urls?: string[];
  popularity_views?: number;
  nutrition_calories?: number;
}

// Recommendation Types
export interface RecipeRecommendation {
  recipe_id: string;
  title: string;
  cuisine: string;
  cook_time_min?: number;
  score: number;
  scores: Record<string, number>;
  image: string[];
}

export interface RecommendationRequest {
  user_id?: string;
  ingredient_ids?: string[];
  ingredient_names?: string[];
  max_cook_time?: number;
  recipe_category?: string;  // Meal type / recipe category
  preferred_cuisines?: string[];  // Preferred cuisines for priority ranking
  limit?: number;
  min_match_ratio?: number;
}

export interface RecommendationResponse {
  results: RecipeRecommendation[];
  total: number;
  request_params: Record<string, any>;
}

// Search Types
export interface RecipeSearchRequest {
  query?: string;
  cuisine?: string;
  max_cook_time?: number;
  min_cook_time?: number;
  tags?: string[];
  ingredients?: string[];
  exclude_ingredients?: string[];
  limit?: number;
  offset?: number;
}

export interface RecipeSearchResponse {
  recipes: RecipeDetail[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// Ingredient Types
export interface IngredientDetail {
  ingredient_id: string;
  canonical_name: string;
  name?: string;
  category?: string;
  allergen?: boolean;
  alternative_names?: string[];
  description?: string;
  nutrition_info?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface IngredientSearchRequest {
  query?: string;
  category?: string;
  allergen?: boolean;
  limit?: number;
  offset?: number;
}

export interface IngredientSearchResponse {
  ingredients: IngredientDetail[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

// User Interaction Types
export interface UserInteraction {
  interaction_id?: string;
  user_id: string;
  recipe_id: string;
  event_type: 'like' | 'rating' | 'view';
  timestamp?: string;
  rating?: number;
  notes?: string;
  duration_minutes?: number;
  success?: boolean;
}

export interface InteractionRecordRequest {
  recipe_id: string;
  event_type: 'like' | 'rating' | 'view';
  rating?: number;
  notes?: string;
  duration_minutes?: number;
  success?: boolean;
}

export interface UserInteractionsResponse {
  user_id: string;
  interactions: UserInteraction[];
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
}

export interface InteractionStats {
  total_interactions: number;
  like_count: number;
  save_count: number;
  view_count: number;
  average_rating?: number;
  most_recent_interaction?: string;
}

export interface UserInteractionStatsResponse {
  user_id: string;
  stats: InteractionStats;
}

// Response Types
export interface UserAllergiesResponse {
  user_id: string;
  allergies: AllergyInfo[];
  total: number;
}

export interface UserDislikesResponse {
  user_id: string;
  dislikes: DislikeInfo[];
  total: number;
}

export interface UserCuisinesResponse {
  user_id: string;
  favorite_cuisines: CuisinePreference[];
  total: number;
}

export interface AllergyUpdateRequest {
  ingredient_ids: string[];
}

export interface DislikeUpdateRequest {
  ingredient_ids: string[];
  reasons?: Record<string, string>;
}

export interface CuisinePreferenceRequest {
  cuisine_name: string;
  preference_level: number;
}

// Recipe Search Types
export interface RecipeSearchRequest {
  query?: string;
  cuisine?: string;
  max_cook_time?: number;
  min_cook_time?: number;
  tags?: string[];
  limit?: number;
  offset?: number;
}

export interface RecipeSearchResponse {
  recipes: RecipeDetail[];
  total: number;
  has_more: boolean;
}

// Ingredient Search Types
export interface IngredientSearchRequest {
  query?: string;
  category?: string;
  limit?: number;
  offset?: number;
}

export interface IngredientSearchResponse {
  ingredients: IngredientDetail[];
  total: number;
  has_more: boolean;
}

// Ingredient Detail Type
export interface IngredientDetail {
  ingredient_id: string;
  canonical_name: string;
  name?: string;
  category?: string;
  allergen?: boolean;
  description?: string;
  alternative_names?: string[];
  nutrition_info?: Record<string, any>;
}

// Basic API Response Types
export interface IngredientsResponse {
  ingredients: Array<{
    id: string;
    name: string;
  }>;
}

export interface CuisinesResponse {
  cuisines: string[];
}

export interface HealthCheckResponse {
  status: string;
  neo4j_connection: string;
  database: string;
}
