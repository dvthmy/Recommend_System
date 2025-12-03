import { 
  UserProfile, 
  UserProfileUpdate,
  AllergyInfo,
  DislikeInfo,
  CuisinePreference,
  RecipeDetail,
  RecipeSummary,
  RecipeRecommendation,
  RecommendationRequest,
  RecommendationResponse,
  RecipeSearchRequest,
  RecipeSearchResponse,
  IngredientDetail,
  IngredientSearchRequest,
  IngredientSearchResponse,
  UserInteraction,
  InteractionRecordRequest,
  UserInteractionsResponse,
  UserInteractionStatsResponse,
  UserAllergiesResponse,
  UserDislikesResponse,
  UserCuisinesResponse,
  UserDietsResponse,
  AllergyUpdateRequest,
  DislikeUpdateRequest,
  CuisinePreferenceRequest,
  DietRequest,
  DietsUpdate,
  IngredientsResponse,
  CuisinesResponse,
  HealthCheckResponse,
  ApiResponse
} from '../types/api';
import { API_CONFIG, API_ENDPOINTS, DEFAULT_HEADERS, ERROR_MESSAGES } from '../config/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

class ApiService {
  private getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private async request<T>(
    endpoint: string, 
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${API_CONFIG.BASE_URL}${endpoint}`;
    
    const defaultHeaders: Record<string, string> = { ...DEFAULT_HEADERS };
    
    // Add Authorization header if token exists
    const token = this.getAuthToken();
    if (token) {
      defaultHeaders['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new ApiError(
          response.status, 
          errorData.detail || `HTTP error! status: ${response.status}`
        );
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      // Handle network errors (CORS, connection refused, etc.)
      if (error instanceof TypeError && error.message.includes('fetch')) {
        return { 
          error: 'Network error: Could not connect to server. Please check if the backend is running on http://localhost:8000' 
        };
      }
      return { 
        error: error instanceof Error ? error.message : 'Unknown error occurred' 
      };
    }
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<HealthCheckResponse>> {
    return this.request<HealthCheckResponse>(API_ENDPOINTS.HEALTH);
  }

  // User Management
  async getCurrentUser(): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/me');
  }

  async createUser(): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/users', {
      method: 'POST',
    });
  }

  async signUp(data: { username: string; name?: string; password: string; age: number; gender: string }): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async signIn(data: { username: string; password: string }): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>('/auth/signin', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async verifyToken(): Promise<ApiResponse<{ valid: boolean; user_id?: string; message?: string }>> {
    return this.request<{ valid: boolean; user_id?: string; message?: string }>('/auth/verify', {
      method: 'POST',
    });
  }

  async refreshToken(): Promise<ApiResponse<{ access_token: string; token_type: string }>> {
    return this.request<{ access_token: string; token_type: string }>('/auth/refresh', {
      method: 'POST',
    });
  }

  // Recommendations
  async getRecommendations(request: RecommendationRequest): Promise<ApiResponse<RecommendationResponse>> {
    return this.request<RecommendationResponse>('/recommend', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getRecommendationsGet(
    user_id?: string,
    ingredient_ids?: string,
    max_cook_time?: number,
    limit: number = 10
  ): Promise<ApiResponse<RecommendationResponse>> {
    const params = new URLSearchParams();
    if (user_id) params.append('user_id', user_id);
    if (ingredient_ids) params.append('ingredient_ids', ingredient_ids);
    if (max_cook_time) params.append('max_cook_time', max_cook_time.toString());
    params.append('limit', limit.toString());

    return this.request<RecommendationResponse>(`/recommend?${params.toString()}`);
  }

  // Ingredients
  async getIngredients(): Promise<ApiResponse<IngredientsResponse>> {
    // Request maximum ingredients (200 is the backend limit)
    return this.request<IngredientsResponse>('/ingredients?limit=200');
  }

  async getIngredientDetail(ingredient_id: string): Promise<ApiResponse<IngredientDetail>> {
    return this.request<IngredientDetail>(`/ingredients/${ingredient_id}`);
  }

  async searchIngredients(request: IngredientSearchRequest): Promise<ApiResponse<IngredientSearchResponse>> {
    const params = new URLSearchParams();
    if (request.query) params.append('query', request.query);
    if (request.category) params.append('category', request.category);
    if (request.allergen !== undefined) params.append('allergen', request.allergen.toString());
    params.append('limit', (request.limit || 20).toString());
    params.append('offset', (request.offset || 0).toString());

    return this.request<IngredientSearchResponse>(`/ingredients/search?${params.toString()}`);
  }

  async getIngredientsByCategory(category: string, limit: number = 20, offset: number = 0): Promise<ApiResponse<IngredientSearchResponse>> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    return this.request<IngredientSearchResponse>(`/ingredients/by-category/${category}?${params.toString()}`);
  }

  // Cuisines
  async getCuisines(): Promise<ApiResponse<CuisinesResponse>> {
    return this.request<CuisinesResponse>('/cuisines');
  }

  // User Profile
  async getUserProfile(user_id: string): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>(`/users/${user_id}/profile`);
  }

  async updateUserProfile(user_id: string, profile: UserProfileUpdate): Promise<ApiResponse<UserProfile>> {
    return this.request<UserProfile>(`/users/${user_id}/profile`, {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  async uploadAvatar(user_id: string, file: File): Promise<ApiResponse<{ message: string; user_id: string; avatar_url: string }>> {
    const formData = new FormData();
    formData.append('file', file);

    const token = this.getAuthToken();
    const url = `${API_CONFIG.BASE_URL}/users/${user_id}/avatar`;
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // Don't set Content-Type for FormData - browser will set it with boundary

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          error: errorText || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : ERROR_MESSAGES.NETWORK_ERROR,
      };
    }
  }

  // User Allergies
  async getUserAllergies(user_id: string): Promise<ApiResponse<UserAllergiesResponse>> {
    return this.request<UserAllergiesResponse>(`/users/${user_id}/allergies`);
  }

  async addUserAllergies(user_id: string, request: AllergyUpdateRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/allergies`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async removeUserAllergies(user_id: string, request: AllergyUpdateRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/allergies`, {
      method: 'DELETE',
      body: JSON.stringify(request),
    });
  }

  // User Dislikes
  async getUserDislikes(user_id: string): Promise<ApiResponse<UserDislikesResponse>> {
    return this.request<UserDislikesResponse>(`/users/${user_id}/dislikes`);
  }

  async addUserDislikes(user_id: string, request: DislikeUpdateRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/dislikes`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async removeUserDislikes(user_id: string, request: DislikeUpdateRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/dislikes`, {
      method: 'DELETE',
      body: JSON.stringify(request),
    });
  }

  // User Favorite Cuisines
  async getUserFavoriteCuisines(user_id: string): Promise<ApiResponse<UserCuisinesResponse>> {
    return this.request<UserCuisinesResponse>(`/users/${user_id}/favorite-cuisines`);
  }

  async addUserFavoriteCuisine(user_id: string, request: CuisinePreferenceRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/favorite-cuisines`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async removeUserFavoriteCuisine(user_id: string, cuisine_name: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/favorite-cuisines/${cuisine_name}`, {
      method: 'DELETE',
    });
  }

  // User Diets
  async getUserDiets(user_id: string): Promise<ApiResponse<UserDietsResponse>> {
    return this.request<UserDietsResponse>(`/users/${user_id}/diets`);
  }

  async addUserDiet(user_id: string, request: DietRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/diets`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async updateUserDiets(user_id: string, request: DietsUpdate): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/diets`, {
      method: 'PUT',
      body: JSON.stringify(request),
    });
  }

  async removeUserDiet(user_id: string, diet_name: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/diets/${diet_name}`, {
      method: 'DELETE',
    });
  }

  // Recipes
  async getRecipeDetail(recipe_id: string): Promise<ApiResponse<RecipeDetail>> {
    return this.request<RecipeDetail>(`/recipes/${recipe_id}`);
  }

  async searchRecipes(request: RecipeSearchRequest): Promise<ApiResponse<RecipeSearchResponse>> {
    const params = new URLSearchParams();
    if (request.query) params.append('query', request.query);
    if (request.cuisine) params.append('cuisine', request.cuisine);
    if (request.max_cook_time) params.append('max_cook_time', request.max_cook_time.toString());
    if (request.min_cook_time) params.append('min_cook_time', request.min_cook_time.toString());
    if (request.tags) params.append('tags', request.tags.join(','));
    if (request.ingredients) params.append('ingredients', request.ingredients.join(','));
    if (request.exclude_ingredients) params.append('exclude_ingredients', request.exclude_ingredients.join(','));
    params.append('limit', (request.limit || 20).toString());
    params.append('offset', (request.offset || 0).toString());

    return this.request<RecipeSearchResponse>(`/recipes/search?${params.toString()}`);
  }

  async getRecipesByCuisine(cuisine: string, limit: number = 20, offset: number = 0): Promise<ApiResponse<RecipeSearchResponse>> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    return this.request<RecipeSearchResponse>(`/recipes/by-cuisine/${cuisine}?${params.toString()}`);
  }

  // User Interactions
  async recordUserInteraction(user_id: string, request: InteractionRecordRequest): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/interactions`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async removeUserRating(user_id: string, recipe_id: string): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/interactions/${recipe_id}/rating`, {
      method: 'DELETE',
    });
  }

  async getUserInteractions(
    user_id: string, 
    event_type?: string, 
    limit: number = 20, 
    offset: number = 0
  ): Promise<ApiResponse<UserInteractionsResponse>> {
    const params = new URLSearchParams();
    if (event_type) params.append('event_type', event_type);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    return this.request<UserInteractionsResponse>(`/users/${user_id}/interactions?${params.toString()}`);
  }

  async getUserInteractionStats(user_id: string): Promise<ApiResponse<UserInteractionStatsResponse>> {
    return this.request<UserInteractionStatsResponse>(`/users/${user_id}/interactions/stats`);
  }

  async deleteUserInteraction(
    user_id: string,
    recipe_id: string,
    event_type?: string
  ): Promise<ApiResponse<any>> {
    const params = new URLSearchParams();
    if (event_type) params.append('event_type', event_type);
    const queryString = params.toString();
    const url = `/users/${user_id}/interactions/${recipe_id}${queryString ? `?${queryString}` : ''}`;
    
    return this.request<any>(url, {
      method: 'DELETE',
    });
  }

  async recomputeUserProfile(user_id: string, force_recompute: boolean = false): Promise<ApiResponse<any>> {
    return this.request<any>(`/users/${user_id}/recompute-profile`, {
      method: 'POST',
      body: JSON.stringify({ force_recompute }),
    });
  }

  // Detection
  async detectIngredients(files: File[]): Promise<ApiResponse<{ ingredients: string[] }>> {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });

    const token = this.getAuthToken();
    
    // Use fetch directly for FormData to avoid JSON.stringify issues
    const url = `${API_CONFIG.BASE_URL}${API_ENDPOINTS.DETECT}`;
    const headers: HeadersInit = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    // Don't set Content-Type for FormData - browser will set it with boundary

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        return {
          error: errorText || `HTTP ${response.status}: ${response.statusText}`,
        };
      }

      const data = await response.json();
      return { data };
    } catch (error) {
      return {
        error: error instanceof Error ? error.message : ERROR_MESSAGES.NETWORK_ERROR,
      };
    }
  }

  // Admin endpoints
  async triggerComputeFeatures(): Promise<ApiResponse<{ message: string; status: string; note?: string }>> {
    return this.request<{ message: string; status: string; note?: string }>(
      API_ENDPOINTS.ADMIN_COMPUTE_FEATURES,
      {
        method: 'POST',
      }
    );
  }

  async getComputeFeaturesStatus(): Promise<ApiResponse<{ status: string; note?: string }>> {
    return this.request<{ status: string; note?: string }>(
      API_ENDPOINTS.ADMIN_COMPUTE_FEATURES_STATUS,
      {
        method: 'GET',
      }
    );
  }
}

export const apiService = new ApiService();
export { ApiError };
