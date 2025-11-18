import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { RecipeRecommendation, RecommendationRequest } from '../types/api';
import { FoodSuggestion } from '../types';
import './FoodSuggestions.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const FoodSuggestions: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useUser();
  const [suggestions, setSuggestions] = useState<FoodSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasRequestedSuggestions, setHasRequestedSuggestions] = useState(false);
  
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
  
  const [ratingModal, setRatingModal] = useState<{ isOpen: boolean; foodId: string | null }>({
    isOpen: false,
    foodId: null
  });
  const [userRating, setUserRating] = useState(0);

  useEffect(() => {
    loadAvailableIngredients();
  }, []);

  // Load ingredients from localStorage after availableIngredients are loaded
  useEffect(() => {
    if (availableIngredients.length > 0) {
      try {
        const savedIngredients = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
        if (savedIngredients.length > 0) {
          // Restore custom ingredients to availableIngredients state
          const customIngredients = savedIngredients
            .filter((ing: any) => {
              const id = ing.id || ing.name;
              return id.startsWith('custom-') && ing.name;
            })
            .map((ing: any) => ({
              id: ing.id,
              name: ing.name
            }))
            .filter((ing: AvailableIngredient) => {
              // Only add if not already in availableIngredients
              return !availableIngredients.some(avail => avail.id === ing.id);
            });
          
          if (customIngredients.length > 0) {
            setAvailableIngredients(prev => [...prev, ...customIngredients]);
          }
          
          // Only load ingredients that actually exist in availableIngredients or are custom
          const validIngredientIds = savedIngredients
            .map((ing: any) => ing.id || ing.name)
            .filter((id: string) => {
              // Check if ingredient exists in availableIngredients or if it's a custom ingredient
              return availableIngredients.some(ing => ing.id === id) || id.startsWith('custom-');
            });
          setSelectedIngredients(validIngredientIds);
          
          // Clean up localStorage to remove invalid ingredients
          if (validIngredientIds.length !== savedIngredients.length) {
            const validSaved = savedIngredients.filter((ing: any) => {
              const id = ing.id || ing.name;
              return validIngredientIds.includes(id);
            });
            localStorage.setItem('uploadedIngredients', JSON.stringify(validSaved));
          }
        }
      } catch (e) {
        console.error('Failed to load ingredients from localStorage:', e);
      }
    }
  }, [availableIngredients.length]);

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
        setAvailableIngredients(ingredientsRes.data.ingredients);
      }
    } catch (err) {
      console.error('Failed to load ingredients:', err);
    }
  };

  const loadRecommendations = async () => {
    setHasRequestedSuggestions(true);
    setLoading(true);
    setError(null);
    
    try {
      if (!user?.user_id) {
        throw new Error('User not initialized');
      }
      
      const ingredientIds = selectedIngredients.filter(id => !id.startsWith('custom-'));
      
      // Extract ingredient names from custom ingredients
      // First try to find in availableIngredients, then check localStorage
      const ingredientNames = selectedIngredients
        .filter(id => id.startsWith('custom-'))
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

      const request: RecommendationRequest = {
        user_id: user.user_id,
        ingredient_ids: ingredientIds.length > 0 ? ingredientIds : undefined,
        ingredient_names: ingredientNames.length > 0 ? ingredientNames : undefined,
        max_cook_time: user.max_cook_time,
        limit: 10,
        min_match_ratio: 0.3  // Lower threshold to get more results
      };

      console.log('🔍 Recommendation Request:', {
        user_id: request.user_id,
        ingredient_ids: request.ingredient_ids,
        ingredient_names: request.ingredient_names,
        ingredient_ids_count: request.ingredient_ids?.length || 0,
        ingredient_names_count: request.ingredient_names?.length || 0,
        max_cook_time: request.max_cook_time,
        limit: request.limit
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
          setError('Không tìm thấy món nào phù hợp với nguyên liệu hiện tại.');
          loadMockSuggestions();
        } else {
          const convertedSuggestions = response.data.results.map((recipe: RecipeRecommendation) => {
            const rawScore = typeof recipe.score === 'number'
              ? recipe.score
              : (recipe as RecipeRecommendation & { match_percent?: number }).match_percent ?? 0;

            return {
            id: recipe.recipe_id,
            name: recipe.title,
            description: `Delicious ${recipe.cuisine} dish`,
            ingredients: [],
            cookingTime: recipe.cook_time_min ? `${recipe.cook_time_min} minutes` : 'Unknown',
            difficulty: 'Medium' as const,
            cuisine: recipe.cuisine,
            mealType: ['Lunch', 'Dinner'],
            dietaryTags: [],
            image: (typeof recipe.image === 'string' ? recipe.image :
              (Array.isArray((recipe as any).image_urls) && (recipe as any).image_urls.length > 0
                ? (recipe as any).image_urls[0]
                : 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop')) as string,
            matchScore: Math.round(Number(rawScore))
          };
          });
          
          setSuggestions(convertedSuggestions);
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
        image: 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400&h=300&fit=crop'
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
        image: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&h=300&fit=crop'
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
    
    setDetecting(true);
    try {
      const response = await apiService.detectIngredients([selectedImage]);
      
      if (response.data && response.data.ingredients) {
        // Match detected ingredient names with available ingredients
        const detectedNames = response.data.ingredients.map((name: string) => name.toLowerCase().trim());
        const matchedIngredients: string[] = [];
        const addedNames: string[] = [];
        
        // Try to match each detected name with available ingredients
        detectedNames.forEach((detected: string) => {
          // Find exact match first
          let matched = availableIngredients.find(ing => {
            const ingName = ing.name.toLowerCase();
            return ingName === detected || ingName.includes(detected) || detected.includes(ingName);
          });
          
          // If no exact match, try partial match
          if (!matched) {
            matched = availableIngredients.find(ing => {
              const ingName = ing.name.toLowerCase();
              const words = ingName.split(/\s+/);
              return words.some(word => word.startsWith(detected) || detected.startsWith(word));
            });
          }
          
          if (matched && !selectedIngredients.includes(matched.id) && !matchedIngredients.includes(matched.id)) {
            matchedIngredients.push(matched.id);
            addedNames.push(matched.name);
          }
        });
        
        // Add matched ingredients
        if (matchedIngredients.length > 0) {
          const newIngredients = [...selectedIngredients, ...matchedIngredients];
          setSelectedIngredients(newIngredients);
          
          // Save to localStorage
          const saved = JSON.parse(localStorage.getItem('uploadedIngredients') || '[]');
          matchedIngredients.forEach(id => {
            const ingredientData = availableIngredients.find(ing => ing.id === id);
            if (ingredientData && !saved.find((s: any) => s.id === id)) {
              saved.push({ id: ingredientData.id, name: ingredientData.name });
            }
          });
          localStorage.setItem('uploadedIngredients', JSON.stringify(saved));
          setDetectionMessage(null);
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

  const handleViewDetails = (foodId: string) => {
    navigate(`/food/${foodId}`);
  };

  const handleRate = (foodId: string) => {
    setRatingModal({ isOpen: true, foodId });
    setUserRating(0);
  };

  // Helper to check if user is guest (not registered)
  const isGuestUser = (): boolean => {
    const hasToken = !!localStorage.getItem('access_token');
    return !hasToken; // Guest if no access_token
  };

  const submitRating = async () => {
    if (ratingModal.foodId && userRating > 0) {
      // Don't save ratings for guest users
      if (isGuestUser()) {
        alert('Please sign in to rate recipes. Guest ratings are not saved.');
        setRatingModal({ isOpen: false, foodId: null });
        setUserRating(0);
        return;
      }
      
      try {
        if (!user?.user_id) {
          throw new Error('User not initialized');
        }
        
        await apiService.recordUserInteraction(user.user_id, {
          recipe_id: ratingModal.foodId,
          event_type: 'like',
          rating: userRating
        });
        
        const ratings = JSON.parse(localStorage.getItem('foodRatings') || '{}');
        ratings[ratingModal.foodId] = userRating;
        localStorage.setItem('foodRatings', JSON.stringify(ratings));
        
        setRatingModal({ isOpen: false, foodId: null });
        setUserRating(0);
      } catch (err) {
        console.error('Failed to record rating:', err);
        setRatingModal({ isOpen: false, foodId: null });
        setUserRating(0);
      }
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'var(--color-success)';
      case 'Medium': return 'var(--color-warning)';
      case 'Hard': return 'var(--color-error)';
      default: return 'var(--text-secondary)';
    }
  };

  const getDifficultyText = (difficulty: string) => {
    switch (difficulty) {
      case 'Easy': return 'Easy';
      case 'Medium': return 'Medium';
      case 'Hard': return 'Hard';
      default: return difficulty;
    }
  };

  return (
    <div className="suggestions-container">
      <div className="container">
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
                      <div className="ingredient-dropdown-item" style={{ textAlign: 'center', color: '#666' }}>
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
                  const ingredient = availableIngredients.find(ing => ing.id === ingredientId);
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
                  
                  return ingredient ? (
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
                  ) : null;
                })}
              </div>
                <div className="get-suggestions-button-container">
                  <button
                    className="btn btn-primary btn-lg"
                    onClick={() => {
                      console.log('Get Suggestions clicked', { 
                        user_id: user?.user_id, 
                        ingredients: selectedIngredients.length,
                        loading 
                      });
                      loadRecommendations();
                    }}
                    disabled={loading || !user?.user_id || selectedIngredients.length === 0}
                  >
                    {loading ? 'Loading...' : hasRequestedSuggestions ? 'Refresh Suggestions' : 'Get Suggestions'}
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
          <div className="suggestions-grid">
            {suggestions.map((suggestion) => (
              <div key={suggestion.id} className="suggestion-card">
                <div className="card-image">
                  {suggestion.image ? (
                    <img src={suggestion.image} alt={suggestion.name} />
                  ) : (
                    <div className="placeholder-image"></div>
                  )}
                  <div className="match-score">
                    {(suggestion as any).matchScore}% match
                  </div>
                </div>
                
                <div className="card-content">
                  <div className="card-header">
                    <h3>{suggestion.name}</h3>
                    <div className="cuisine-tag">{suggestion.cuisine}</div>
                  </div>
                  
                  <p className="description">{suggestion.description}</p>
                  
                  <div className="card-meta">
                    <div className="meta-item">
                      <span className="meta-icon"></span>
                      <span>{suggestion.cookingTime}</span>
                    </div>
                    <div 
                      className="meta-item difficulty"
                      style={{ color: getDifficultyColor(suggestion.difficulty) }}
                    >
                      <span className="meta-icon"></span>
                      <span>{getDifficultyText(suggestion.difficulty)}</span>
                    </div>
                  </div>

                  <div className="ingredients-preview">
                    <h4>Main ingredients:</h4>
                    <div className="ingredients-list">
                      {suggestion.ingredients.slice(0, 4).map((ingredient, index) => (
                        <span key={index} className="ingredient-tag">
                          {ingredient}
                        </span>
                      ))}
                      {suggestion.ingredients.length > 4 && (
                        <span className="ingredient-tag more">
                          +{suggestion.ingredients.length - 4}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="card-footer">
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleViewDetails(suggestion.id)}
                    >
                      View Details
                    </button>
                    <button 
                      className="btn btn-outline"
                      onClick={() => handleRate(suggestion.id)}
                    >
                      Rate
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
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
                    <img src={imagePreview} alt="Preview" className="image-preview" />
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

      {/* Rating Modal */}
      {ratingModal.isOpen && (
        <div className="rating-modal-overlay">
          <div className="rating-modal">
            <h3>Rate Dish</h3>
            <div className="rating-stars">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  className={`star ${star <= userRating ? 'filled' : ''}`}
                  onClick={() => setUserRating(star)}
                >
                  ★
                </button>
              ))}
            </div>
            <p>{userRating > 0 ? `${userRating} stars` : 'Select rating'}</p>
            <div className="modal-actions">
              <button 
                className="btn btn-outline"
                onClick={() => setRatingModal({ isOpen: false, foodId: null })}
              >
                Cancel
              </button>
              <button 
                className="btn btn-primary"
                onClick={submitRating}
                disabled={userRating === 0}
              >
                Submit Rating
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default FoodSuggestions;
