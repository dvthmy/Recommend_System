import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Clock, Star, Users, Heart } from 'lucide-react';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { RecipeRecommendation, RecommendationRequest } from '../types/api';
import { FoodSuggestion } from '../types';
import { getUserId, setUserId } from '../utils/auth';
import Onboarding from './Onboarding';
import './FoodSuggestions.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const FoodSuggestions: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading, loadUserProfile, loadUserAllergies, loadUserFavoriteCuisines, allergies, favoriteCuisines } = useUser();
  const [suggestions, setSuggestions] = useState<FoodSuggestion[]>([]);
  const [allSuggestions, setAllSuggestions] = useState<FoodSuggestion[]>([]); // Store all loaded suggestions
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRequestedSuggestions, setHasRequestedSuggestions] = useState(false);
  const [hasMore, setHasMore] = useState(false);
  
  // Manual ingredient input state
  const [selectedIngredients, setSelectedIngredients] = useState<string[]>([]);
  const [availableIngredients, setAvailableIngredients] = useState<AvailableIngredient[]>([]);
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [editingIngredientId, setEditingIngredientId] = useState<string | null>(null);
  const [editSearch, setEditSearch] = useState('');
  const [searchResults, setSearchResults] = useState<AvailableIngredient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  
  // Upload image modal state
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [detecting, setDetecting] = useState(false);
  const [detectionMessage, setDetectionMessage] = useState<string | null>(null);
  
  // Liked recipes state
  const [likedRecipes, setLikedRecipes] = useState<Set<string>>(new Set());

  // Track if we need to restore ingredients (set when suggestionsState is restored)
  const [shouldRestoreIngredients, setShouldRestoreIngredients] = useState(false);

  useEffect(() => {
    loadAvailableIngredients();
    loadLikedRecipes();
    
    // Restore suggestions state from sessionStorage if available (when returning from detail page)
     try {
       const savedState = sessionStorage.getItem('suggestionsState');
       if (savedState) {
         const parsedState = JSON.parse(savedState);
        
        // Restore suggestions if available
         if (parsedState.suggestions && parsedState.suggestions.length > 0) {
           // Restore all suggestions
           setAllSuggestions(parsedState.suggestions);
           // Show first 20
           const displayCount = Math.min(20, parsedState.suggestions.length);
           setSuggestions(parsedState.suggestions.slice(0, displayCount));
           setHasRequestedSuggestions(parsedState.hasRequestedSuggestions || false);
           setHasMore(parsedState.suggestions.length > 20);
           if (parsedState.error) {
             setError(parsedState.error);
           }
        }
        
        // Always restore selectedIngredients if available (even if no suggestions)
        // Store to restore after availableIngredients are loaded
        if (parsedState.selectedIngredients && Array.isArray(parsedState.selectedIngredients) && parsedState.selectedIngredients.length > 0) {
             sessionStorage.setItem('restoreIngredientsFromSession', JSON.stringify(parsedState.selectedIngredients));
          setShouldRestoreIngredients(true); // Trigger restoration
          console.log('💾 Stored ingredients to restore:', parsedState.selectedIngredients);
         }
         // Don't clear sessionStorage yet - we need it for restoring ingredients
       }
     } catch (e) {
       console.error('Failed to restore suggestions state:', e);
     }
    
    // Load user profile, allergies, and favorite cuisines if user exists (both authenticated and guest)
    const userId = getUserId();
    if (userId) {
      // Always try to load user profile if not in context or if userId doesn't match
      if (!user || user.user_id !== userId || user.completed_onboarding === undefined) {
        loadUserProfile(userId).then((success) => {
          if (success) {
            // Load allergies and favorite cuisines after profile is loaded
            loadUserAllergies(userId);
            loadUserFavoriteCuisines(userId);
          }
        });
      } else {
        // User already in context, just load allergies and cuisines
        loadUserAllergies(userId);
        loadUserFavoriteCuisines(userId);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Restore ingredients from sessionStorage when returning from detail page
  // This runs when availableIngredients are loaded and there's a restore flag
  useEffect(() => {
    // Only proceed if availableIngredients are loaded and we have a restore flag
        const restoreFromSession = sessionStorage.getItem('restoreIngredientsFromSession');
    if (availableIngredients.length > 0 && restoreFromSession) {
      try {
        let ingredientsToRestore: string[] | null = null;
          try {
            ingredientsToRestore = JSON.parse(restoreFromSession);
          // Remove flag immediately to prevent multiple restorations
            sessionStorage.removeItem('restoreIngredientsFromSession');
          console.log('🔄 Restoring ingredients from session:', ingredientsToRestore);
          } catch (e) {
            console.error('Failed to parse restoreIngredientsFromSession:', e);
          return;
        }
        
        if (ingredientsToRestore && ingredientsToRestore.length > 0) {
          // First, check localStorage for full ingredient data (including custom ingredients)
          let savedIngredients: any[] = [];
            try {
              const localSaved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
            // Map ingredient IDs to their full data
            savedIngredients = ingredientsToRestore.map(id => {
              // First try to find in localStorage (includes custom ingredients)
              const found = localSaved.find((item: any) => (item.id || item.name) === id);
              if (found) return { id: found.id || found.name, name: found.name };
              
              // Then try to find in availableIngredients
              const ing = availableIngredients.find(ing => ing.id === id);
              if (ing) return { id: ing.id, name: ing.name };
            
            // Last resort: assume it's a custom ingredient
            return { id, name: id.replace('custom-', '') };
          });
          } catch (e) {
            console.error('Failed to load from localStorage:', e);
            // Fallback: try to match with availableIngredients
            savedIngredients = ingredientsToRestore.map(id => {
              const ing = availableIngredients.find(ing => ing.id === id);
              if (ing) return { id: ing.id, name: ing.name };
              return { id, name: id.replace('custom-', '') };
            });
        }
        
        if (savedIngredients.length > 0) {
            console.log('📦 Restoring ingredients data:', savedIngredients);
            
            // Add all missing ingredients to availableIngredients (including non-custom ones)
            // This ensures they can be displayed in the UI (both in dropdown checkmark and tags)
            const missingIngredients = savedIngredients
              .map((ing: any) => ({
                id: ing.id || ing.name,
                name: ing.name
              }))
              .filter((ing: AvailableIngredient) => {
                // Only add if not already in availableIngredients
                return !availableIngredients.some(avail => avail.id === ing.id);
              });
          
            // Always add missing ingredients first, then restore selectedIngredients
            if (missingIngredients.length > 0) {
              // First, add missing ingredients to availableIngredients
              setAvailableIngredients(prev => {
                const updated = [...prev, ...missingIngredients];
                // After updating availableIngredients, restore selectedIngredients
                // Use the updated list to ensure all ingredients are available
                const validIngredientIds = savedIngredients.map((ing: any) => ing.id || ing.name);
                console.log('✅ Setting selectedIngredients (added to available):', validIngredientIds);
                // Set selectedIngredients in the next render cycle to ensure availableIngredients is updated
                setTimeout(() => {
                  setSelectedIngredients(validIngredientIds);
                }, 0);
                return updated;
              });
            } else {
              // All ingredients already in availableIngredients, just restore selectedIngredients
              const validIngredientIds = savedIngredients.map((ing: any) => ing.id || ing.name);
              console.log('✅ Setting selectedIngredients (all in available):', validIngredientIds);
              setSelectedIngredients(validIngredientIds);
            }
        
            // Clear sessionStorage suggestionsState after restoring ingredients
            sessionStorage.removeItem('suggestionsState');
            setShouldRestoreIngredients(false); // Reset flag
          }
        }
      } catch (e) {
        console.error('Failed to restore ingredients:', e);
        setShouldRestoreIngredients(false); // Reset flag on error
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [availableIngredients.length, shouldRestoreIngredients]);

  // Search ingredients when user types
  useEffect(() => {
    if (!ingredientSearch.trim()) {
      setSearchResults([]);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsSearching(true);
      try {
        const response = await apiService.searchIngredients({
          query: ingredientSearch.trim(),
          limit: 20,
          offset: 0
        });
        
        if (response.data && response.data.ingredients) {
          const results: AvailableIngredient[] = response.data.ingredients.map(ing => ({
            id: ing.ingredient_id,
            name: ing.canonical_name || ing.name || ''
          }));
          setSearchResults(results);
        } else {
          setSearchResults([]);
        }
      } catch (err) {
        console.error('Failed to search ingredients:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300); // Debounce 300ms

    return () => clearTimeout(timeoutId);
  }, [ingredientSearch]);

  const loadAvailableIngredients = async () => {
    try {
      const ingredientsRes = await apiService.getIngredients();
      if (ingredientsRes.data && ingredientsRes.data.ingredients) {
        // Map to correct format: {id, name}
        const formattedIngredients = ingredientsRes.data.ingredients.map((ing: any) => ({
          id: ing.ingredient_id || ing.id,  // Backend uses ingredient_id
          name: ing.canonical_name || ing.name || ''
        })).filter((ing: any) => ing.id && ing.name); // Only keep valid ingredients
        
        console.log('📦 Loaded ingredients from API:', formattedIngredients.length);
        console.log('📝 Sample ingredients:', formattedIngredients.slice(0, 5));
        setAvailableIngredients(formattedIngredients);
      } else {
        console.warn('⚠️ No ingredients data from API');
      }
    } catch (err) {
      console.error('Failed to load ingredients:', err);
    }
  };

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
    e.stopPropagation(); // Prevent double-click from triggering
    
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
      await loadLikedRecipes();
      
      // Dispatch event to notify Profile component to reload stats
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

  const loadRecommendations = async () => {
    setHasRequestedSuggestions(true);
    setLoading(true);
    setError(null);
    
    try {
      // Get userId from user context or storage (for guest users)
      let userId = user?.user_id || getUserId();
      
      console.log('🔍 loadRecommendations - Initial check:', {
        hasUserInContext: !!user,
        userIdFromContext: user?.user_id,
        userIdFromStorage: getUserId(),
        finalUserId: userId
      });
      
      if (!userId) {
        throw new Error('User not initialized. Please complete onboarding first.');
      }
      
      // Ensure userId is saved (in sessionStorage for guests, localStorage for authenticated)
      if (userId && !getUserId()) {
        const isGuest = !localStorage.getItem('access_token');
        setUserId(userId, isGuest);
      }
      
      // If user is not loaded in context, try to load it
      if (!user?.user_id) {
        console.log('🔄 User not in context, loading profile...');
        const success = await loadUserProfile(userId);
        if (!success) {
          console.error('❌ Failed to load user profile');
          // For guest users, we can still proceed with userId from localStorage
          // The backend will handle the request
        } else {
          console.log('✅ User profile loaded successfully');
        }
        // Wait a bit for state to update
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      // Ensure favorite cuisines are loaded before making recommendation request
      const finalUserId = user?.user_id || userId;
      
      console.log('🔍 loadRecommendations - Final userId:', finalUserId);
      if (!favoriteCuisines) {
        console.log('🔄 Favorite cuisines not loaded yet, loading now...');
        await loadUserFavoriteCuisines(userId);
        // Wait a bit for state to update (React state update is async)
        await new Promise(resolve => setTimeout(resolve, 100));
      }
      
      const ingredientIds = selectedIngredients.filter(id => id && !id.startsWith('custom-'));
      
      // Extract ingredient names from custom ingredients
      // First try to find in availableIngredients, then check localStorage
      const ingredientNames = selectedIngredients
        .filter(id => id && id.startsWith('custom-'))
        .map(id => {
          // Try to find in availableIngredients first
          const ing = availableIngredients.find(ingredient => ingredient.id === id);
          if (ing?.name?.trim()) {
            return ing.name.trim();
          }
          
          // If not found, check localStorage
          try {
            const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
            const savedIng = saved.find((item: any) => item.id === id);
            if (savedIng?.name?.trim()) {
              return savedIng.name.trim();
            }
          } catch (e) {
            console.warn('Failed to parse localStorage for ingredients:', e);
          }
          
          // Last resort: try to extract from ID (but this should rarely happen)
          const extracted = id.replace('custom-', '').trim();
          // Only use if it doesn't look like a timestamp (all digits)
          if (!/^\d+$/.test(extracted)) {
            return extracted;
          }
          
          // If it's a timestamp, return empty string (will be filtered out)
          console.warn(`Could not find name for custom ingredient ID: ${id}`);
          return '';
        })
        .filter(name => name.length > 0);

      // Get meal type from user preferences (stored in meal_preferences)
      // Use user from context if available, otherwise use userId directly (backend will handle it)
      const mealType = user?.meal_preferences && user.meal_preferences.length > 0 
        ? user.meal_preferences[0] 
        : undefined;

      // Get preferred cuisines for sorting (not for filtering)
      const preferredCuisinesList = favoriteCuisines?.favorite_cuisines 
        ? favoriteCuisines.favorite_cuisines.map((c: any) => c.cuisine_name)
        : [];

      // Get allergies (for logging - backend will handle exclusion automatically via user_id)
      const userAllergies = allergies?.allergies 
        ? allergies.allergies.map((a: any) => a.ingredient_name || a.ingredient_id)
        : [];

      // Request more results to have enough for pagination
      // We'll fetch 100 results, then sort and paginate on frontend
      const request: RecommendationRequest = {
        user_id: finalUserId,
        ingredient_ids: ingredientIds.length > 0 ? ingredientIds : undefined,
        ingredient_names: ingredientNames.length > 0 ? ingredientNames : undefined,
        max_cook_time: user?.max_cook_time,
        recipe_category: mealType,  // Use meal type from user preferences
        preferred_cuisines: undefined, // Không giới hạn cuisine - lấy tất cả
        limit: 100, // Fetch more to have enough for pagination
        min_match_ratio: 0.3
      };

      console.log('🔍 Recommendation Request:', {
        user_id: request.user_id,
        ingredient_ids: request.ingredient_ids,
        ingredient_names: request.ingredient_names,
        ingredient_ids_count: request.ingredient_ids?.length || 0,
        ingredient_names_count: request.ingredient_names?.length || 0,
        max_cook_time: request.max_cook_time,
        recipe_category: request.recipe_category,
        preferred_cuisines: request.preferred_cuisines,
        preferred_cuisines_count: request.preferred_cuisines?.length || 0,
        allergies: userAllergies,
        allergies_count: userAllergies.length,
        limit: request.limit,
        min_match_ratio: request.min_match_ratio  // ✅ Added to debug
      });

      const response = await apiService.getRecommendations(request);
      
      console.log('📥 Recommendation Response:', {
        has_data: !!response.data,
        results_count: response.data?.results?.length || 0,
        total: response.data?.total || 0,
        error: response.error
      });
      
      if (response.data) {
        if (response.data.results.length === 0) {
          console.warn('No recommendations returned for request', request);
          setError('No recipes found matching your ingredients. Try different ingredients or adjust your preferences.');
          loadMockSuggestions();
        } else {
          const convertedSuggestions = response.data.results.map((recipe: RecipeRecommendation) => {
            const rawScore = typeof recipe.score === 'number'
              ? recipe.score
              : (recipe as RecipeRecommendation & { match_percent?: number }).match_percent ?? 0;

            // Handle cuisine: backend returns array, frontend expects string
            // Join all cuisines with ", " for display (e.g., "Thai, Vietnamese")
            let cuisineDisplay: string;
            if (Array.isArray(recipe.cuisine)) {
              if (recipe.cuisine.length > 0) {
                // Join all cuisines with ", " (e.g., ["Thai", "Vietnamese"] -> "Thai, Vietnamese")
                cuisineDisplay = recipe.cuisine.join(', ');
              } else {
                cuisineDisplay = 'World';
              }
            } else if (typeof recipe.cuisine === 'string') {
              // Handle case where cuisine might be a concatenated string like "ThaiVietnamese"
              // Try to split common cuisine names if they're concatenated
              const cuisineStr = recipe.cuisine;
              // Check if it looks like concatenated cuisines (e.g., "ThaiVietnamese", "ChineseJapanese")
              // Common cuisine names that might be concatenated (sorted by length desc to match longer names first)
              const commonCuisines = ['Middle Eastern', 'Mediterranean', 'Vietnamese', 'Caribbean', 'European', 'American', 'British', 'Chinese', 'Japanese', 'Korean', 'Indian', 'Italian', 'Spanish', 'French', 'Mexican', 'Greek', 'Asian', 'Thai'];
              
              // Try to split if it matches pattern of concatenated cuisines
              let splitCuisines: string[] = [];
              let remaining = cuisineStr;
              
              // Keep trying to match cuisines until we can't match any more
              while (remaining && remaining.length > 0) {
                let matched = false;
                for (const cuisine of commonCuisines) {
                  // Case-insensitive match
                  if (cuisine && remaining.toLowerCase().startsWith(cuisine.toLowerCase())) {
                    splitCuisines.push(cuisine);
                    remaining = remaining.substring(cuisine.length);
                    matched = true;
                    break;
                  }
                }
                // If no match found, break to avoid infinite loop
                if (!matched) {
                  break;
                }
              }
              
              // If we successfully split into multiple cuisines and consumed entire string, use split version
              // Otherwise, use original string (might be a single cuisine name we don't recognize)
              if (splitCuisines.length > 1 && remaining.length === 0) {
                cuisineDisplay = splitCuisines.join(', ');
              } else {
                cuisineDisplay = cuisineStr;
              }
            } else {
              cuisineDisplay = 'World';
            }

            // Use meal field from backend (normalized to 4 categories: Breakfast, Lunch, Dinner, Snack)
            // Fallback to 'Dinner' if not provided
            const meal = recipe.meal || 'Dinner';
            
            return {
            id: recipe.recipe_id,
            name: recipe.title,
            description: `Delicious ${cuisineDisplay} dish`,
            ingredients: [],
            cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
            difficulty: 'Medium' as const,
            cuisine: cuisineDisplay,
            mealType: [meal],  // Use normalized meal from backend (single value in array for compatibility)
            meal: meal,  // Also store as single value for easier access
            dietaryTags: [],
            image: (typeof recipe.image === 'string' ? recipe.image :
              (Array.isArray((recipe as any).image_urls) && (recipe as any).image_urls.length > 0
                ? (recipe as any).image_urls[0]
                : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop')) as string,
            matchScore: Math.round(Number(rawScore)),
            servings: (recipe as any).servings,
            ratingValue: (recipe as any).avg_rating || (recipe as any).rating_value || 0,
            ratingCount: (recipe as any).rating_count || 0
          };
          });
          
          // Sort suggestions: preferred cuisines first, then others
          const sortedSuggestions = convertedSuggestions.sort((a, b) => {
            const aCuisines = a.cuisine.split(', ').map(c => c.trim());
            const bCuisines = b.cuisine.split(', ').map(c => c.trim());
            
            // Check if suggestion has preferred cuisine
            const aHasPreferred = aCuisines.some(c => 
              preferredCuisinesList.some(pc => 
                c.toLowerCase().includes(pc.toLowerCase()) || 
                pc.toLowerCase().includes(c.toLowerCase())
              )
            );
            const bHasPreferred = bCuisines.some(c => 
              preferredCuisinesList.some(pc => 
                c.toLowerCase().includes(pc.toLowerCase()) || 
                pc.toLowerCase().includes(c.toLowerCase())
              )
            );
            
            // Preferred cuisines first
            if (aHasPreferred && !bHasPreferred) return -1;
            if (!aHasPreferred && bHasPreferred) return 1;
            
            // If both have or both don't have preferred, sort by match score
            return b.matchScore - a.matchScore;
          });
          
          // Store all suggestions
          setAllSuggestions(sortedSuggestions);
          // Show first 20
          const displayCount = Math.min(20, sortedSuggestions.length);
          setSuggestions(sortedSuggestions.slice(0, displayCount));
          setHasMore(sortedSuggestions.length > 20);
        }
      } else if (response.error) {
        setError(response.error);
        loadMockSuggestions();
      }
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setError(err instanceof Error ? err.message : 'Failed to load recommendations');
      loadMockSuggestions();
    } finally {
      setLoading(false);
    }
  };

  const loadMockSuggestions = () => {
    const mockSuggestions: FoodSuggestion[] = [
      {
        id: '1',
        name: 'Beef Stew',
        description: 'Traditional beef stew with rich broth and fresh vegetables',
        ingredients: ['Beef', 'Carrots', 'Potatoes', 'Onions', 'Garlic', 'Ginger', 'Cinnamon', 'Star Anise'],
        cookingTime: '2 hours',
        difficulty: 'Medium',
        cuisine: 'Vietnamese',
        mealType: ['Lunch', 'Dinner'],
        dietaryTags: ['Gluten Free'],
        image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop',
        servings: 4,
        ratingValue: 4.7,
        ratingCount: 128
      },
      {
        id: '2',
        name: 'Tomato Salad',
        description: 'Fresh tomato salad with olive oil and herbs',
        ingredients: ['Tomatoes', 'Cilantro', 'Onions', 'Olive Oil', 'Vinegar', 'Salt', 'Pepper'],
        cookingTime: '15 minutes',
        difficulty: 'Easy',
        cuisine: 'International',
        mealType: ['Breakfast', 'Lunch', 'Snack'],
        dietaryTags: ['Vegan', 'Gluten Free'],
        image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop',
        servings: 2,
        ratingValue: 4.5,
        ratingCount: 89
      }
    ];
    
    const scoredSuggestions = mockSuggestions.map(suggestion => ({
      ...suggestion,
      matchScore: Math.floor(Math.random() * 30) + 70
    }));
    
    setSuggestions(scoredSuggestions);
  };

  // Manual ingredient handlers
  const handleAddIngredient = (ingredientId: string) => {
    // Use functional update to ensure we have the latest state
    setSelectedIngredients(prev => {
      if (prev.includes(ingredientId)) {
        return prev; // Already selected, don't add again
      }
      const newIngredients = [...prev, ingredientId];
      
      // Find ingredient data from search results or available ingredients
      const ingredientData = searchResults.find(ing => ing.id === ingredientId) 
        || availableIngredients.find(ing => ing.id === ingredientId);
      
      if (ingredientData) {
        // Add to availableIngredients if not already there
        setAvailableIngredients(prevAvail => {
          if (!prevAvail.find(ing => ing.id === ingredientId)) {
            return [...prevAvail, ingredientData];
          }
          return prevAvail;
        });
        
        // Save to localStorage
        const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
        if (!saved.find((s: any) => (s.id || s.name) === ingredientId)) {
          saved.push({ id: ingredientData.id, name: ingredientData.name });
          localStorage.setItem('uploadedIngredients', JSON.stringify(saved));
        }
      }
      
      return newIngredients;
    });
    setIngredientSearch('');
  };

  const handleRemoveIngredient = (ingredientId: string) => {
    // Remove from state immediately
    setSelectedIngredients(prev => prev.filter(id => id !== ingredientId));
    
    // Update localStorage
    const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
    const updated = saved.filter((ing: any) => {
      const id = ing.id || ing.name;
      return id !== ingredientId;
    });
    localStorage.setItem('uploadedIngredients', JSON.stringify(updated));
  };

  const handleEditIngredient = (oldIngredientId: string, newIngredientId: string) => {
    if (oldIngredientId === newIngredientId) return;
    
    // Replace old ingredient with new one
    const newIngredients = selectedIngredients.map(id => 
      id === oldIngredientId ? newIngredientId : id
    );
    setSelectedIngredients(newIngredients);
    
    // Update localStorage
    const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
    const oldIngredient = saved.find((ing: any) => ing.id === oldIngredientId);
    if (oldIngredient) {
      const updated = saved.filter((ing: any) => ing.id !== oldIngredientId);
      const newIngredientData = availableIngredients.find(ing => ing.id === newIngredientId);
      if (newIngredientData) {
        updated.push({ id: newIngredientData.id, name: newIngredientData.name });
      }
      localStorage.setItem('uploadedIngredients', JSON.stringify(updated));
    }
  };

  // Use search results if available, otherwise filter from availableIngredients
  const filteredIngredients = ingredientSearch.trim() && searchResults.length > 0
    ? searchResults
    : availableIngredients.filter(ingredient =>
        ingredient.name.toLowerCase().includes(ingredientSearch.toLowerCase())
      );

  // Check if search term matches any existing ingredient (from search results or available)
  const allIngredients = [...searchResults, ...availableIngredients];
  const exactMatch = allIngredients.find(
    ing => ing.name.toLowerCase() === ingredientSearch.toLowerCase().trim()
  );

  // Check if we can add a new ingredient (search term doesn't match any existing ingredient)
  const canAddNewIngredient = ingredientSearch.trim() && 
    !exactMatch && 
    !selectedIngredients.some(id => {
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
      // Add to selected ingredients
      const newIngredients = [...selectedIngredients, newIngredient.id];
      setSelectedIngredients(newIngredients);
      setIngredientSearch('');
      
      // Save to localStorage
      const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
      saved.push({ id: newIngredient.id, name: newIngredient.name });
      localStorage.setItem('uploadedIngredients', JSON.stringify(saved));
    }
  };

  // Upload image handlers
  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };


  const handleDetect = async () => {
    if (!selectedImage) return;
    
    // Ensure ingredients are loaded before detecting
    if (availableIngredients.length === 0) {
      console.log('⏳ Ingredients not loaded yet, loading now...');
      await loadAvailableIngredients();
      // Wait a bit for state to update
      await new Promise(resolve => setTimeout(resolve, 500));
    }
    
    setDetecting(true);
    try {
      const response = await apiService.detectIngredients([selectedImage]);
      
      if (response.data && response.data.ingredients) {
        // Match detected ingredient names with available ingredients
        const detectedNames = response.data.ingredients.map((name: string) => name.toLowerCase().trim());
        const matchedIngredients: string[] = [];
        const unmatchedNames: string[] = [];
        const matchedNames: string[] = [];
        
        console.log('🔍 Detecting:', detectedNames);
        console.log('📦 Available ingredients count:', availableIngredients.length);
        
        // Debug: Check if basic ingredients exist
        const basicChecks = ['chicken', 'garlic', 'carrot', 'potato'];
        basicChecks.forEach(name => {
          const exists = availableIngredients.find(ing => 
            ing.name && ing.name.toLowerCase().trim() === name
          );
          console.log(`🔎 DB has "${name}"?`, exists ? `✅ ${exists.id}` : '❌ Not found');
        });
        
        // STEP-BY-STEP matching: từng ingredient một, rõ ràng
        for (let index = 0; index < detectedNames.length; index++) {
          const detected = detectedNames[index];
          if (!detected || !detected.trim()) continue;
          
          // Convert to lowercase để match dễ hơn
          const detectedLower = detected.toLowerCase().trim();
          console.log(`\n🔍 [${index + 1}/${detectedNames.length}] Matching: "${detectedLower}"`);
          
          let matched: AvailableIngredient | undefined;
          
          // STEP 1: Exact match (ưu tiên cao nhất)
          console.log('  Step 1: Looking for exact match in cache...');
          matched = availableIngredients.find(ing => {
            if (!ing || !ing.name) return false;
            const ingName = ing.name.toLowerCase().trim();
            return ingName === detectedLower;
          });
          
          // STEP 1.5: If not in cache, search in DB directly
          if (!matched) {
            console.log('  Step 1.5: Not in cache, searching DB...');
            try {
              const searchRes = await apiService.searchIngredients({
                query: detectedLower,
                limit: 5,
                offset: 0
              });
              
              if (searchRes.data && searchRes.data.ingredients && searchRes.data.ingredients.length > 0) {
                // Find exact match from search results
                const exactMatch = searchRes.data.ingredients.find((ing: any) => {
                  const ingName = (ing.canonical_name || ing.name || '').toLowerCase().trim();
                  return ingName === detectedLower;
                });
                
                if (exactMatch) {
                  const ingredientId: string | undefined = exactMatch.ingredient_id;
                  const ingredientName: string | undefined = exactMatch.canonical_name || exactMatch.name;

                  // Guard against incomplete data from backend
                  if (ingredientId && ingredientName) {
                    matched = {
                      id: ingredientId,
                      name: ingredientName,
                    };
                    // Add to cache for future use
                    availableIngredients.push(matched);
                    console.log(`  ✅ Found exact match in DB: "${matched.name}" (${matched.id})`);
                  } else {
                    console.warn(
                      '  ⚠️ Skipping exactMatch from DB due to missing id or name',
                      exactMatch,
                    );
                  }
                }
              }
            } catch (err) {
              console.error('  ❌ DB search failed:', err);
            }
          } else {
            console.log(`  ✅ Found exact match in cache: "${matched.name}" (${matched.id})`);
          }
          
          if (!matched) {
            console.log('  ❌ No exact match');
            
            // STEP 2: Tìm ingredients có chứa detected word (nhưng lấy shortest)
            console.log('  Step 2: Looking for ingredients containing this word...');
            const containsMatches = availableIngredients.filter(ing => {
              if (!ing || !ing.name) return false;
              const ingName = ing.name.toLowerCase().trim();
              // Check if detectedLower is a complete word in ingName
              const words = ingName.split(/\s+/);
              return words.includes(detectedLower);
            });
            
            if (containsMatches.length > 0) {
              console.log(`  Found ${containsMatches.length} matches:`, containsMatches.map(m => m.name));
              // Sort by length, pick shortest (most specific)
              containsMatches.sort((a, b) => a.name.length - b.name.length);
              matched = containsMatches[0];
              console.log(`  ✅ Picked shortest: "${matched.name}" (${matched.id})`);
            } else {
              console.log('  ❌ No word matches');
              
              // STEP 3: Starts with (cho partial matches)
              console.log('  Step 3: Looking for ingredients starting with this...');
              const startsWithMatches = availableIngredients.filter(ing => {
                if (!ing || !ing.name) return false;
                const ingName = ing.name.toLowerCase().trim();
                return ingName.startsWith(detectedLower);
              });
              
              if (startsWithMatches.length > 0) {
                console.log(`  Found ${startsWithMatches.length} matches:`, startsWithMatches.map(m => m.name));
                startsWithMatches.sort((a, b) => a.name.length - b.name.length);
                matched = startsWithMatches[0];
                console.log(`  ✅ Picked shortest: "${matched.name}" (${matched.id})`);
              } else {
                console.log('  ❌ No starts-with matches');
              }
            }
          }
          
          // Add to results
          if (matched && !selectedIngredients.includes(matched.id) && !matchedIngredients.includes(matched.id)) {
            console.log(`✅ FINAL: "${detectedLower}" → "${matched.name}" (ID: ${matched.id})\n`);
            matchedIngredients.push(matched.id);
            matchedNames.push(matched.name);
          } else if (!matched) {
            console.log(`❌ FINAL: No match for "${detectedLower}" - will create custom ingredient\n`);
            unmatchedNames.push(detectedLower);
          }
        }
        
        console.log('✅ Total matched:', matchedIngredients.length);
        console.log('❌ Total unmatched:', unmatchedNames.length);
        
        const newIngredientIds = [...selectedIngredients];
        const newCustomIngredients: AvailableIngredient[] = [];
        const customIds: string[] = [];
        
        // Handle matched ingredients
        if (matchedIngredients.length > 0) {
          matchedIngredients.forEach(id => {
            if (!newIngredientIds.includes(id)) {
              newIngredientIds.push(id);
            }
          });
        }
        
        // Create custom ingredients for unmatched names
        unmatchedNames.forEach((name, index) => {
          const cleanName = name.replace(/\s+/g, ' ').trim().toLowerCase();
          if (!cleanName) return;
          
          // Check if already exists (maybe previously added custom)
          const existing = availableIngredients.find(ing => 
            ing.name && ing.name.toLowerCase().trim() === cleanName
          );
          if (existing) {
            if (!newIngredientIds.includes(existing.id)) {
              newIngredientIds.push(existing.id);
            }
            return;
          }
          
          const customId = `custom-${Date.now()}-${index}`;
          // Keep original name (lowercase) - DO NOT capitalize
          // This ensures consistency with database ingredient names
          
          const newIngredient: AvailableIngredient = {
            id: customId,
            name: cleanName  // Use lowercase name directly
          };
          newCustomIngredients.push(newIngredient);
          customIds.push(customId);
          newIngredientIds.push(customId);
        });
        
        if (newCustomIngredients.length > 0) {
          setAvailableIngredients(prev => [...prev, ...newCustomIngredients]);
        }
        
        if (matchedIngredients.length > 0 || customIds.length > 0) {
          setSelectedIngredients(newIngredientIds);
          
          // Save to localStorage
          const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
          const existingIds = new Set(saved.map((s: any) => s.id || s.name));
          
          matchedIngredients.forEach(id => {
            const ingredientData = availableIngredients.find(ing => ing.id === id);
            if (ingredientData && !existingIds.has(id)) {
              saved.push({ id: ingredientData.id, name: ingredientData.name });
              existingIds.add(id);
            }
          });
          
          newCustomIngredients.forEach(ingredient => {
            if (!existingIds.has(ingredient.id)) {
              saved.push({ id: ingredient.id, name: ingredient.name });
              existingIds.add(ingredient.id);
            }
          });
          
          localStorage.setItem('uploadedIngredients', JSON.stringify(saved));
          
          const totalAdded = matchedIngredients.length + newCustomIngredients.length;
          if (totalAdded > 0) {
            setDetectionMessage(`Added ${totalAdded} ingredient${totalAdded > 1 ? 's' : ''} from image.`);
          } else {
            setDetectionMessage(null);
          }
        } else {
          // No ingredients detected
          setDetectionMessage('No matching ingredients found. Please add them manually.');
        }
        
        // Close modal
        setUploadModalOpen(false);
        setSelectedImage(null);
        setImagePreview(null);
      } else {
        // API error
        setDetectionMessage('Failed to detect ingredients. Please try again or add them manually.');
        setUploadModalOpen(false);
        setSelectedImage(null);
        setImagePreview(null);
      }
    } catch (err) {
      console.error('Failed to detect ingredients:', err);
      setDetectionMessage('Error detecting ingredients. Please try again or add them manually.');
      setUploadModalOpen(false);
      setSelectedImage(null);
      setImagePreview(null);
    } finally {
      setDetecting(false);
    }
  };

  const handleCancelUpload = () => {
    setUploadModalOpen(false);
    setSelectedImage(null);
    setImagePreview(null);
    setDetectionMessage(null);
  };

  const handleLoadMore = () => {
    if (allSuggestions.length > suggestions.length) {
      // Load from already fetched suggestions
      const nextDisplayCount = Math.min(suggestions.length + 40, allSuggestions.length);
      setSuggestions(allSuggestions.slice(0, nextDisplayCount));
      setHasMore(nextDisplayCount < allSuggestions.length);
    }
  };

  const handleViewDetails = (foodId: string) => {
    // Save current state to sessionStorage before navigating
    const stateToSave = {
      suggestions: allSuggestions, // Save all suggestions, not just displayed ones
      hasRequestedSuggestions,
      selectedIngredients,
      error
    };
    sessionStorage.setItem('suggestionsState', JSON.stringify(stateToSave));
    navigate(`/food/${foodId}`);
  };

  const getServingsText = (servings?: number) => {
    if (!servings) return '1 serving';
    return `${servings} ${servings === 1 ? 'serving' : 'servings'}`;
  };

  const getRatingValueText = (rating?: number) => {
    if (rating === undefined || rating === null) {
      return '4.8';
    }
    return rating.toFixed(1);
  };

  const getRatingCountText = (count?: number) => {
    if (!count) return '0 ratings';
    return `${count.toLocaleString()} ratings`;
  };

  // Check if user is guest
  const hasAccessToken = !!localStorage.getItem('access_token');
  const hasUsername = !!user?.username;
  const isGuest = !hasAccessToken || (user && !hasUsername);

  // Check if user has completed onboarding (from database or user object)
  // For both guest and registered users, check completed_onboarding from user object
  const hasCompletedOnboarding = user?.completed_onboarding === true;

  // Show loading state while user is being loaded (only for registered users)
  if (!isGuest && isLoading && !user) {
    return (
      <div className="suggestions-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Loading...</h3>
          </div>
        </div>
      </div>
    );
  }

  // If a registered user hasn't completed onboarding, show Onboarding component.
  // Guest users are allowed to access suggestions directly after finishing the onboarding flow.
  if (!isGuest && !hasCompletedOnboarding) {
    return <Onboarding />;
  }

  return (
    <div className="suggestions-container">
      <div className="container">
        {/* Back to Onboarding Button */}
        <div className="back-to-onboarding-container">
          <button
            className="btn btn-outline btn-sm"
            onClick={() => navigate('/onboarding')}
          >
            ← Back to Onboarding
          </button>
        </div>

        {/* Ingredients Input Section */}
        <div className="ingredients-input-section">
          <div className="section-header">
            <h2>Add Ingredients</h2>
          </div>
          <p className="section-description">Add ingredients manually or upload an image to detect them</p>
          
          <div className="ingredients-input-container">
            {/* Manual Input and Upload in same row */}
            <div className="input-upload-row">
              <div className="ingredient-search-wrapper">
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
                  className="ingredient-search-input"
                />
                {ingredientSearch && (filteredIngredients.length > 0 || canAddNewIngredient || isSearching) && (
                  <div className="ingredient-dropdown">
                    {isSearching && (
                      <div key="searching" className="ingredient-dropdown-item" style={{ textAlign: 'center', color: '#666' }}>
                        Searching...
                      </div>
                    )}
                    {!isSearching && filteredIngredients.slice(0, 10).map((ingredient) => {
                      // Only show checkmark if ingredient is actually in selectedIngredients
                      const isSelected = selectedIngredients.includes(ingredient.id);
                      return (
                        <div
                          key={ingredient.id}
                          className={`ingredient-dropdown-item ${isSelected ? 'selected' : ''}`}
                          onClick={() => {
                            if (isSelected) {
                              handleRemoveIngredient(ingredient.id);
                            } else {
                              handleAddIngredient(ingredient.id);
                            }
                          }}
                        >
                          {isSelected && (
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="ingredient-checkmark">
                              <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          )}
                          <span className={isSelected ? 'selected-text' : ''}>{ingredient.name}</span>
                        </div>
                      );
                    })}
                    {canAddNewIngredient && (
                      <div
                        key="add-new-ingredient"
                        className="ingredient-dropdown-item add-new"
                        onClick={handleAddNewIngredient}
                      >
                        <span>Add "{ingredientSearch.trim()}"</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              <div className="or-divider">
                <span>OR</span>
              </div>
              
              <button
                className="btn btn-primary btn-lg upload-btn-inline"
                onClick={() => setUploadModalOpen(true)}
              >
                📷 Upload Image
              </button>
            </div>
            
            {detectionMessage && (
              <div className="detection-message">
                {detectionMessage}
              </div>
            )}
            
            {selectedIngredients.length > 0 && (
              <>
                <div className="selected-ingredients-tags">
                {selectedIngredients.map(ingredientId => {
                  // Step 1: Try to find ingredient in availableIngredients first
                  let ingredient = availableIngredients.find(ing => ing.id === ingredientId);
                  
                  // Step 2: If not found, try to get from localStorage (for restored ingredients)
                  if (!ingredient) {
                    try {
                      const localSaved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
                      const found = localSaved.find((item: any) => (item.id || item.name) === ingredientId);
                      if (found) {
                        const foundIngredient = { id: found.id || found.name, name: found.name };
                        ingredient = foundIngredient;
                        // Add to availableIngredients if not already there (for next render)
                        // Use useEffect would be better, but this ensures it's added for dropdown checkmark
                        if (!availableIngredients.some(ing => ing.id === foundIngredient.id)) {
                          // Use setTimeout to avoid setting state during render
                          setTimeout(() => {
                            setAvailableIngredients(prev => {
                              if (!prev.some(ing => ing.id === foundIngredient.id)) {
                                return [...prev, foundIngredient];
                              }
                              return prev;
                            });
                          }, 0);
                        }
                      }
                    } catch (e) {
                      console.error('Failed to load from localStorage:', e);
                    }
                  }
                  
                  // Step 3: If still not found, create a temporary ingredient object for display
                  // This ensures the tag always displays, even if ingredient data is missing
                  if (!ingredient) {
                    ingredient = {
                      id: ingredientId,
                      name: ingredientId.replace('custom-', '').replace(/^ing_/, '')
                    };
                  }
                  
                  const isEditing = editingIngredientId === ingredientId;
                  
                  if (isEditing) {
                    const editFiltered = availableIngredients.filter(ing =>
                      ing.name.toLowerCase().includes(editSearch.toLowerCase()) &&
                      ing.id !== ingredientId
                    );
                    
                    return (
                      <div key={ingredientId} className="ingredient-tag-editing">
                        <div className="edit-search-wrapper">
                          <input
                            type="text"
                            placeholder="Search to replace..."
                            value={editSearch}
                            onChange={(e) => setEditSearch(e.target.value)}
                            className="edit-search-input"
                            autoFocus
                          />
                          {editSearch && editFiltered.length > 0 && (
                            <div className="edit-dropdown">
                              {editFiltered.slice(0, 10).map((ing) => (
                                <div
                                  key={ing.id}
                                  className="edit-dropdown-item"
                                  onClick={() => {
                                    handleEditIngredient(ingredientId, ing.id);
                                    setEditingIngredientId(null);
                                    setEditSearch('');
                                  }}
                                >
                                  {ing.name}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                        <button
                          className="tag-remove-btn"
                          onClick={() => {
                            setEditingIngredientId(null);
                            setEditSearch('');
                          }}
                          title="Cancel edit"
                        >
                          ×
                        </button>
                      </div>
                    );
                  }
                  
                  return (
                    <span 
                      key={ingredientId} 
                      className="ingredient-tag"
                      onDoubleClick={() => {
                        setEditingIngredientId(ingredientId);
                        setEditSearch('');
                      }}
                      title="Double click to edit"
                    >
                      {ingredient.name}
                      <button
                        className="tag-remove-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleRemoveIngredient(ingredientId);
                        }}
                        title="Remove"
                      >
                        ×
                      </button>
                    </span>
                  );
                })}
              </div>
                <div className="get-suggestions-button-container">
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={() => {
                      console.log('Get Suggestions clicked', { 
                        user_id: user?.user_id || getUserId(), 
                        ingredients: selectedIngredients.length,
                        loading 
                      });
                      loadRecommendations();
                    }}
                    disabled={loading || (!user?.user_id && !getUserId()) || selectedIngredients.length === 0}
                  >
                    {loading ? 'Loading...' : 'Suggestions'}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Suggestions Header - Only show after requesting suggestions */}
        {hasRequestedSuggestions && (
          <div className="suggestions-header">
            <h1>Dish Suggestions</h1>
            <p>Based on your ingredients, here are the most suitable dishes</p>
            {error && (
              <div className="error-message">
                <p>Error: {error}</p>
                <button onClick={loadRecommendations} className="btn btn-outline btn-sm">
                  Retry
                </button>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {hasRequestedSuggestions && loading && (
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Finding suitable dishes...</h3>
            <p>AI is analyzing ingredients and suggesting the best dishes for you</p>
          </div>
        )}

        {/* Suggestions Grid */}
        {hasRequestedSuggestions && !loading && suggestions.length > 0 && (
          <>
            <div className="foods-grid">
              {suggestions.map((suggestion) => (
                <div 
                  key={suggestion.id} 
                  className="food-card"
                  onDoubleClick={() => handleViewDetails(suggestion.id)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleViewDetails(suggestion.id);
                    }
                  }}
                  aria-label={`View details for ${suggestion.name}`}
                  tabIndex={0}
                >
                  <div className="card-image">
                    {suggestion.image ? (
                      <img src={suggestion.image} alt={suggestion.name} />
                    ) : (
                      <div className="placeholder-image"></div>
                    )}
                    <button
                      className="card-favorite-btn"
                      onClick={(e) => toggleLike(suggestion.id, e)}
                      aria-label={likedRecipes.has(suggestion.id) ? 'Unlike recipe' : 'Like recipe'}
                      title={likedRecipes.has(suggestion.id) ? 'Unlike recipe' : 'Like recipe'}
                    >
                      <Heart 
                        className="favorite-icon" 
                        size={20} 
                        strokeWidth={2}
                        fill={likedRecipes.has(suggestion.id) ? '#FF6B35' : 'transparent'}
                        color={likedRecipes.has(suggestion.id) ? '#FF6B35' : '#666666'}
                      />
                    </button>
                  </div>
                  
                  <div className="card-content">
                    <h3 className="home-recipe-title">{suggestion.name}</h3>
                    
                    <div className="card-meta-rating-group">
                      <div className="card-meta">
                        <div className="meta-item">
                          <Clock className="meta-icon" size={16} strokeWidth={1.5} />
                          <span>{suggestion.cookingTime}</span>
                        </div>
                        <div className="meta-item">
                          <Users className="meta-icon" size={16} strokeWidth={1.5} />
                          <span>{getServingsText(suggestion.servings)}</span>
                        </div>
                      </div>

                      <div className="card-rating">
                        <Star className="rating-icon" size={16} strokeWidth={1.5} />
                        <span className="rating-number">{getRatingValueText(suggestion.ratingValue)}</span>
                        <span className="rating-count">
                          ({getRatingCountText(suggestion.ratingCount)})
                        </span>
                      </div>
                    </div>

                    <div className="card-cuisine-detail">
                      Cuisine: <strong>{suggestion.cuisine || 'World'}</strong>
                    </div>

                    <div className="card-hint">
                      Double-click to view details
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {/* Load More Button */}
            {hasMore && (
              <div className="load-more-container" style={{ textAlign: 'center', marginTop: '2rem', marginBottom: '2rem' }}>
                <button
                  className="btn btn-primary btn-lg"
                  onClick={handleLoadMore}
                >
                  Load More
                </button>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!loading && suggestions.length === 0 && selectedIngredients.length === 0 && (
          <div className="empty-state">
            <p>Add ingredients to get dish suggestions</p>
          </div>
        )}
      </div>

      {/* Upload Image Modal */}
      {uploadModalOpen && (
        <div className="upload-modal-overlay" onClick={handleCancelUpload}>
          <div className="upload-modal" onClick={(e) => e.stopPropagation()}>
            <div className="upload-modal-header">
              <h2>Upload Image</h2>
              <button className="close-btn" onClick={handleCancelUpload}>×</button>
            </div>
            
            <div className="upload-modal-content">
              <div className="image-upload-area">
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleImageSelect}
                  className="file-input"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="upload-label">
                  {imagePreview ? (
                    <img src={imagePreview || undefined} alt="Preview" className="image-preview" />
                  ) : (
                    <div className="upload-placeholder">
                      <span>📷</span>
                      <p>Click to select an image</p>
                    </div>
                  )}
                </label>
              </div>
            </div>

            <div className="upload-modal-footer">
              <button 
                className="btn btn-outline" 
                onClick={handleCancelUpload}
                disabled={detecting}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary" 
                onClick={handleDetect}
                disabled={!selectedImage || detecting}
              >
                {detecting ? 'Detecting...' : 'Detect'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default FoodSuggestions;

