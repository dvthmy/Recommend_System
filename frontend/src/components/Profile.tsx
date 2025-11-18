import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import './Profile.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, allergies, favoriteCuisines, loadUserProfile, loadUserAllergies, loadUserFavoriteCuisines, isLoading } = useUser();
  const [isEditing, setIsEditing] = useState(false);
  const [activityStats, setActivityStats] = useState({
    likedRecipes: 0,
    savedRecipes: 0,
    ratedRecipes: 0
  });
  
  // Edit modal state
  const [editingUsername, setEditingUsername] = useState('');
  const [editingName, setEditingName] = useState('');
  const [editingAge, setEditingAge] = useState<number | ''>('');
  const [editingGender, setEditingGender] = useState('');
  const [editingAllergies, setEditingAllergies] = useState<string[]>([]);
  const [editingCuisines, setEditingCuisines] = useState<{ name: string; level: number }[]>([]);
  const [availableIngredients, setAvailableIngredients] = useState<AvailableIngredient[]>([]);
  const [availableCuisines, setAvailableCuisines] = useState<string[]>([]);
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [cuisineSearch, setCuisineSearch] = useState('');
  const [searchResults, setSearchResults] = useState<AvailableIngredient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const hasLoadedRef = useRef(false);

  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (userId && !hasLoadedRef.current) {
      hasLoadedRef.current = true;
      loadUserData();
      loadActivityStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  // Reload data when navigating to Profile page (e.g., after Onboarding)
  useEffect(() => {
    const userId = localStorage.getItem('userId');
    if (userId && location.pathname === '/profile' && hasLoadedRef.current) {
      // Reload data when user navigates to Profile page to get latest data
      loadUserData();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  useEffect(() => {
    if (isEditing) {
      loadAvailableOptions();
      // Initialize editing state with current values
      setEditingUsername(user?.username || '');
      setEditingName(user?.name || '');
      setEditingAge(user?.age || '');
      // Normalize gender to match dropdown options (capitalize first letter)
      const normalizeGender = (gender: string | undefined) => {
        if (!gender) return '';
        const lower = gender.toLowerCase();
        if (lower === 'male') return 'Male';
        if (lower === 'female') return 'Female';
        if (lower === 'other') return 'Other';
        // If already capitalized correctly
        if (['Male', 'Female', 'Other'].includes(gender)) return gender;
        // Fallback: capitalize first letter
        return gender.charAt(0).toUpperCase() + gender.slice(1).toLowerCase();
      };
      setEditingGender(normalizeGender(user?.gender));
      if (allergies?.allergies) {
        setEditingAllergies(allergies.allergies.map((a: any) => a.ingredient_id));
      }
      if (favoriteCuisines?.favorite_cuisines) {
        setEditingCuisines(favoriteCuisines.favorite_cuisines.map((c: any) => ({
          name: c.cuisine_name,
          level: c.preference_level || 5
        })));
      }
    }
  }, [isEditing, allergies, favoriteCuisines, user]);

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

  const loadUserData = async () => {
    const userId = localStorage.getItem('userId');
    if (userId) {
      await Promise.all([
        loadUserProfile(userId),
        loadUserAllergies(userId),
        loadUserFavoriteCuisines(userId)
      ]);
    }
  };

  const loadActivityStats = async () => {
    const userId = localStorage.getItem('userId');
    if (!userId) return;

    try {
      // Try to get stats from stats endpoint first
      const statsRes = await apiService.getUserInteractionStats(userId);
      if (statsRes.data && statsRes.data.stats) {
        // Get rated count from interactions
        try {
          const interactionsRes = await apiService.getUserInteractions(userId, undefined, 1000, 0);
          const rated = interactionsRes.data?.interactions?.filter((i: any) => i.rating && i.rating > 0).length || 0;
          
          setActivityStats({
            likedRecipes: statsRes.data.stats.like_count || 0,
            savedRecipes: statsRes.data.stats.save_count || 0,
            ratedRecipes: rated
          });
        } catch (err) {
          setActivityStats({
            likedRecipes: statsRes.data.stats.like_count || 0,
            savedRecipes: statsRes.data.stats.save_count || 0,
            ratedRecipes: 0
          });
        }
        return;
      }
    } catch (err) {
      // Fallback to calculating from interactions
      try {
        const interactionsRes = await apiService.getUserInteractions(userId, undefined, 1000, 0);
        if (interactionsRes.data) {
          const interactions = interactionsRes.data.interactions || [];
          const liked = interactions.filter((i: any) => i.event_type === 'LIKE' || i.liked === true).length;
          const saved = interactions.filter((i: any) => i.event_type === 'SAVE' || i.saved === true).length;
          const rated = interactions.filter((i: any) => i.rating && i.rating > 0).length;
          
          setActivityStats({
            likedRecipes: liked,
            savedRecipes: saved,
            ratedRecipes: rated
          });
        }
      } catch (err2) {
        console.error('Failed to load activity stats:', err2);
      }
    }
  };

  const loadAvailableOptions = async () => {
    try {
      const [ingredientsRes, cuisinesRes] = await Promise.all([
        apiService.getIngredients(),
        apiService.getCuisines()
      ]);
      
      if (ingredientsRes.data && ingredientsRes.data.ingredients) {
        setAvailableIngredients(ingredientsRes.data.ingredients);
      }
      if (cuisinesRes.data && cuisinesRes.data.cuisines) {
        setAvailableCuisines(cuisinesRes.data.cuisines);
      }
    } catch (err) {
      console.error('Failed to load available options:', err);
    }
  };

  const handleEditProfile = () => {
    setIsEditing(true);
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setIngredientSearch('');
    setCuisineSearch('');
    setEditingUsername('');
    setEditingName('');
    setEditingAge('');
    setEditingGender('');
  };

  const handleAddAllergy = (ingredientId: string) => {
    // Use functional update to ensure we have the latest state
    setEditingAllergies(prev => {
      if (prev.includes(ingredientId)) {
        return prev; // Already selected, don't add again
      }
      const newAllergies = [...prev, ingredientId];
      
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
      }
      
      return newAllergies;
    });
    setIngredientSearch('');
  };

  const handleRemoveAllergy = (ingredientId: string) => {
    // Remove from state immediately using functional update
    setEditingAllergies(prev => prev.filter(id => id !== ingredientId));
  };

  const handleAddCuisine = (cuisineName: string) => {
    if (!editingCuisines.find(c => c.name === cuisineName)) {
      setEditingCuisines([...editingCuisines, { name: cuisineName, level: 5 }]);
    }
    setCuisineSearch('');
  };

  const handleRemoveCuisine = (cuisineName: string) => {
    setEditingCuisines(editingCuisines.filter(c => c.name !== cuisineName));
  };

  const handleSaveChanges = async () => {
    setIsSaving(true);
    const userId = localStorage.getItem('userId');
    if (!userId) {
      alert('User not found');
      setIsSaving(false);
      return;
    }

    try {
      // Update user profile (name, age, gender)
      // Note: Username cannot be changed (read-only field)
      const profileUpdate: any = {};
      // Username is read-only, don't include in update
      // if (editingUsername !== (user?.username || '')) {
      //   profileUpdate.username = editingUsername || null;
      // }
      if (editingName !== (user?.name || '')) {
        profileUpdate.name = editingName || null;
      }
      if (editingAge !== (user?.age || '')) {
        profileUpdate.age = editingAge === '' ? null : Number(editingAge);
      }
      // Normalize both genders for comparison (case-insensitive)
      const normalizeForCompare = (g: string | undefined) => g?.toLowerCase() || '';
      if (normalizeForCompare(editingGender) !== normalizeForCompare(user?.gender)) {
        profileUpdate.gender = editingGender || null;
      }

      if (Object.keys(profileUpdate).length > 0) {
        await apiService.updateUserProfile(userId, profileUpdate);
      }

      // Get current allergies and cuisines
      const currentAllergyIds = allergies?.allergies?.map((a: any) => a.ingredient_id) || [];
      const currentCuisineNames = favoriteCuisines?.favorite_cuisines?.map((c: any) => c.cuisine_name) || [];

      // Calculate changes
      const allergiesToAdd = editingAllergies.filter(id => !currentAllergyIds.includes(id));
      const allergiesToRemove = currentAllergyIds.filter((id: string) => !editingAllergies.includes(id));
      const cuisinesToAdd = editingCuisines.filter(c => !currentCuisineNames.includes(c.name));
      const cuisinesToRemove = currentCuisineNames.filter((name: string) => 
        !editingCuisines.find(c => c.name === name)
      );

      // Add new allergies
      if (allergiesToAdd.length > 0) {
        await apiService.addUserAllergies(userId, { ingredient_ids: allergiesToAdd });
      }

      // Remove allergies
      if (allergiesToRemove.length > 0) {
        await apiService.removeUserAllergies(userId, { ingredient_ids: allergiesToRemove });
      }

      // Add new cuisines
      for (const cuisine of cuisinesToAdd) {
        await apiService.addUserFavoriteCuisine(userId, {
          cuisine_name: cuisine.name,
          preference_level: cuisine.level
        });
      }

      // Remove cuisines
      for (const cuisineName of cuisinesToRemove) {
        await apiService.removeUserFavoriteCuisine(userId, cuisineName);
      }

      // Reload data
      await loadUserData();
      setIsEditing(false);
      setIngredientSearch('');
      setCuisineSearch('');
      alert('Profile updated successfully!');
    } catch (err) {
      console.error('Failed to save changes:', err);
      alert('Failed to save changes. Please try again.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleViewHistory = () => {
    navigate('/history');
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
    !editingAllergies.some(id => {
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
      setEditingAllergies([...editingAllergies, newIngredient.id]);
      setIngredientSearch('');
    }
  };

  const filteredCuisines = availableCuisines.filter(cuisine =>
    cuisine.toLowerCase().includes(cuisineSearch.toLowerCase())
  );

  const getAgeRange = (age?: number): string => {
    if (!age) return 'N/A';
    if (age < 18) return 'Under 18';
    if (age < 25) return '18-24';
    if (age < 35) return '25-34';
    if (age < 45) return '35-44';
    if (age < 55) return '45-54';
    return '55+';
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
        <div className="profile-layout">
          {/* Left Section - User Information */}
          <div className="profile-left">
            <div className="profile-avatar">
              <div className="avatar-circle">
                {user?.name ? user.name.charAt(0).toUpperCase() : (user?.username ? user.username.charAt(0).toUpperCase() : 'U')}
              </div>
            </div>
            <div className="user-name" style={{ fontSize: '1.8rem', fontWeight: '600', marginTop: '1rem' }}>
              {user?.name || user?.username || 'Guest User'}
            </div>
            <div className="user-username" style={{ fontSize: '0.95rem', color: '#666', marginTop: '0.5rem' }}>
              @{user?.username?.toLowerCase().replace(/\s+/g, '_') || 'guest'}
            </div>
            {/* Email removed as per user request */}
            <div className="user-info-icons" style={{ marginTop: '1rem' }}>
              <div className="info-icon">
                <span className="icon"></span>
                <span>{user?.gender || 'N/A'}</span>
              </div>
              <div className="info-icon">
                <span className="icon"></span>
                <span>{getAgeRange(user?.age)}</span>
              </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="profile-right">
            {/* Food Preferences Section */}
            <div className="preferences-section">
              <div className="section-header">
                <h2 className="section-title">Food Preferences</h2>
                <button className="edit-profile-btn" onClick={handleEditProfile}>
                  <span className="edit-icon">✏️</span>
                  Edit Profile
                </button>
              </div>

              <div className="preferences-content">
                <div className="preference-group">
                  <h3 className="preference-label">Favorite Cuisines</h3>
                  <div className="tags-container">
                    {favoriteCuisines?.favorite_cuisines && favoriteCuisines.favorite_cuisines.length > 0 ? (
                      favoriteCuisines.favorite_cuisines.map((cuisine: any, index: number) => (
                        <span key={index} className="tag tag-cuisine">
                          {cuisine.cuisine_name}
                        </span>
                      ))
                    ) : (
                      <span className="empty-tag">No cuisines selected</span>
                    )}
                  </div>
                </div>

                <div className="preference-group">
                  <h3 className="preference-label">Ingredient Allergies</h3>
                  <div className="tags-container">
                    {allergies?.allergies && allergies.allergies.length > 0 ? (
                      allergies.allergies.map((allergy: any, index: number) => (
                        <span key={index} className="tag tag-allergy">
                          {allergy.ingredient_name}
                        </span>
                      ))
                    ) : (
                      <span className="empty-tag">No allergies</span>
                    )}
                  </div>
                </div>
              </div>
              
              {/* Edit Modal */}
              {isEditing && (
                <div className="edit-modal-overlay" onClick={handleCancelEdit}>
                  <div className="edit-modal" onClick={(e) => e.stopPropagation()}>
                    <div className="edit-modal-header">
                      <h2>Edit Profile</h2>
                      <button className="close-btn" onClick={handleCancelEdit}>×</button>
                    </div>
                    
                    <div className="edit-modal-content">
                      {/* Personal Information Section */}
                      <div className="edit-section">
                        <h3>Personal Information</h3>
                        <div className="edit-form-fields">
                          <div className="edit-form-field">
                            <label htmlFor="edit-username">Username (Login)</label>
                            <input
                              id="edit-username"
                              type="text"
                              placeholder="Enter username"
                              value={editingUsername}
                              disabled
                              className="edit-form-input"
                              style={{ backgroundColor: '#f5f5f5', cursor: 'not-allowed', color: '#666' }}
                              title="Username cannot be changed"
                            />
                            <small style={{ color: '#666', fontSize: '0.85rem', marginTop: '4px', display: 'block' }}>
                              Username cannot be changed
                            </small>
                          </div>
                          <div className="edit-form-field">
                            <label htmlFor="edit-name">Name (Display Name)</label>
                            <input
                              id="edit-name"
                              type="text"
                              placeholder="Enter your name"
                              value={editingName}
                              onChange={(e) => setEditingName(e.target.value)}
                              className="edit-form-input"
                            />
                          </div>
                          <div className="edit-form-field">
                            <label htmlFor="edit-age">Age</label>
                            <input
                              id="edit-age"
                              type="number"
                              placeholder="Enter age"
                              min="1"
                              max="150"
                              value={editingAge}
                              onChange={(e) => setEditingAge(e.target.value === '' ? '' : Number(e.target.value))}
                              className="edit-form-input"
                            />
                          </div>
                          <div className="edit-form-field">
                            <label htmlFor="edit-gender">Gender</label>
                            <select
                              id="edit-gender"
                              value={editingGender}
                              onChange={(e) => setEditingGender(e.target.value)}
                              className="edit-form-input"
                            >
                              <option value="Male">Male</option>
                              <option value="Female">Female</option>
                              <option value="Other">Other</option>
                            </select>
                          </div>
                        </div>
                      </div>

                      {/* Favorite Cuisines Section */}
                      <div className="edit-section">
                        <h3>Favorite Cuisines</h3>
                        <div className="edit-search-container">
                          <input
                            type="text"
                            placeholder="Search cuisines..."
                            value={cuisineSearch}
                            onChange={(e) => setCuisineSearch(e.target.value)}
                            className="edit-search-input"
                          />
                          {cuisineSearch && filteredCuisines.length > 0 && (
                            <div className="edit-dropdown">
                              {filteredCuisines
                                .filter(c => !editingCuisines.find(ec => ec.name === c))
                                .slice(0, 10)
                                .map(cuisine => (
                                  <div
                                    key={cuisine}
                                    className="edit-dropdown-item"
                                    onClick={() => handleAddCuisine(cuisine)}
                                  >
                                    {cuisine}
                                  </div>
                                ))}
                            </div>
                          )}
                        </div>
                        <div className="edit-tags-container">
                          {editingCuisines.map((cuisine, index) => (
                            <span key={index} className="tag tag-cuisine edit-tag">
                              {cuisine.name}
                              <button
                                className="tag-remove-btn"
                                onClick={() => handleRemoveCuisine(cuisine.name)}
                              >
                                ×
                              </button>
                            </span>
                          ))}
                        </div>
                      </div>

                      {/* Ingredient Allergies Section */}
                      <div className="edit-section">
                        <h3>Ingredient Allergies</h3>
                        <div className="edit-search-container">
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
                            className="edit-search-input"
                          />
                          {ingredientSearch && (filteredIngredients.length > 0 || canAddNewIngredient || isSearching) && (
                            <div className="edit-dropdown">
                              {isSearching && (
                                <div className="edit-dropdown-item" style={{ textAlign: 'center', color: '#666' }}>
                                  Searching...
                                </div>
                              )}
                              {!isSearching && filteredIngredients.slice(0, 10).map((ingredient: AvailableIngredient) => {
                                // Only show checkmark if ingredient is actually in editingAllergies
                                const isSelected = editingAllergies.includes(ingredient.id);
                                return (
                                  <div
                                    key={ingredient.id}
                                    className={`edit-dropdown-item ${isSelected ? 'selected' : ''}`}
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
                                  className="edit-dropdown-item add-new"
                                  onClick={handleAddNewIngredient}
                                >
                                  <span>Add "{ingredientSearch.trim()}"</span>
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                        <div className="edit-tags-container">
                          {editingAllergies.map(ingredientId => {
                            // Try to find in availableIngredients or searchResults first
                            let ingredient = availableIngredients.find(ing => ing.id === ingredientId)
                              || searchResults.find(ing => ing.id === ingredientId);
                            
                            // If not found, fallback to allergies data to get the name
                            if (!ingredient && allergies?.allergies) {
                              const allergyData = allergies.allergies.find((a: any) => a.ingredient_id === ingredientId);
                              if (allergyData) {
                                ingredient = {
                                  id: ingredientId,
                                  name: allergyData.ingredient_name || ingredientId
                                };
                              }
                            }
                            
                            // If still not found, use ingredient_id as fallback
                            if (!ingredient) {
                              ingredient = {
                                id: ingredientId,
                                name: ingredientId
                              };
                            }
                            
                            return (
                              <span key={ingredientId} className="tag tag-allergy edit-tag">
                                {ingredient.name}
                                <button
                                  className="tag-remove-btn"
                                  onClick={() => handleRemoveAllergy(ingredientId)}
                                >
                                  ×
                                </button>
                              </span>
                            );
                          })}
                        </div>
                      </div>
                    </div>

                    <div className="edit-modal-footer">
                      <button className="btn btn-outline" onClick={handleCancelEdit} disabled={isSaving}>
                        Cancel
                      </button>
                      <button className="btn btn-primary" onClick={handleSaveChanges} disabled={isSaving}>
                        {isSaving ? 'Saving...' : 'Save Changes'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Activity Summary Section */}
            <div className="activity-section">
              <h2 className="section-title">My Activity Summary</h2>
              <div className="activity-cards">
                <div className="activity-card">
                  <div className="activity-icon activity-icon-liked">❤️</div>
                  <div className="activity-label">Liked Recipes</div>
                  <div className="activity-count">{activityStats.likedRecipes}</div>
                </div>
                <div className="activity-card">
                  <div className="activity-icon activity-icon-saved">🔖</div>
                  <div className="activity-label">Saved Recipes</div>
                  <div className="activity-count">{activityStats.savedRecipes}</div>
                </div>
                <div className="activity-card">
                  <div className="activity-icon activity-icon-rated">⭐</div>
                  <div className="activity-label">Rated Recipes</div>
                  <div className="activity-count">{activityStats.ratedRecipes}</div>
                </div>
              </div>
              <button className="view-history-btn" onClick={handleViewHistory}>
                View Full History
                <span className="arrow-icon">→</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
