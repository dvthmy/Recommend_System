import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { getUserId } from '../utils/auth';
import './Profile.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const Profile: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, allergies, favoriteCuisines, loadUserProfile, loadUserAllergies, loadUserFavoriteCuisines, isLoading, logout } = useUser();
  const [isEditing, setIsEditing] = useState(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' } | null>(null);
  const [activityStats, setActivityStats] = useState({
    likedRecipes: 0,
    viewedRecipes: 0,
    ratedRecipes: 0
  });
  
  // Edit modal state
  const [editingUsername, setEditingUsername] = useState('');
  const [editingName, setEditingName] = useState('');
  const [editingAge, setEditingAge] = useState<number | ''>('');
  const [editingGender, setEditingGender] = useState('');
  const [editingAllergies, setEditingAllergies] = useState<string[]>([]);
  const [editingCuisines, setEditingCuisines] = useState<{ name: string; level: number }[]>([]);
  // Dietary plan state
  const [editingDietaryPlan, setEditingDietaryPlan] = useState<string>('');
  const [editingWeightKg, setEditingWeightKg] = useState<number | ''>('');
  const [editingHeightCm, setEditingHeightCm] = useState<number | ''>('');
  const [editingActivityLevel, setEditingActivityLevel] = useState<string>('');
  const [availableIngredients, setAvailableIngredients] = useState<AvailableIngredient[]>([]);
  const [ingredientSearch, setIngredientSearch] = useState('');
  const [searchResults, setSearchResults] = useState<AvailableIngredient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hasLoadedRef = useRef(false);
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const genderDropdownRef = useRef<HTMLDivElement>(null);
  const [isDietaryModeDropdownOpen, setIsDietaryModeDropdownOpen] = useState(false);
  const dietaryModeDropdownRef = useRef<HTMLDivElement>(null);
  const [isCuisineDropdownOpen, setIsCuisineDropdownOpen] = useState(false);
  const cuisineDropdownRef = useRef<HTMLDivElement>(null);
  const [isActivityLevelDropdownOpen, setIsActivityLevelDropdownOpen] = useState(false);
  const activityLevelDropdownRef = useRef<HTMLDivElement>(null);
  
  const genderOptions = [
    { id: 'Male', name: 'Male' },
    { id: 'Female', name: 'Female' },
    { id: 'Other', name: 'Other' }
  ];

  const dietaryModeOptions = [
    { id: 'none', name: 'None', description: 'No dietary restrictions' },
    { id: 'low_carb', name: 'Low Carb', description: '≤26% carbs, ≤30g per serving' },
    { id: 'high_protein', name: 'High Protein', description: '≥25% protein, ≥20g per serving' },
    { id: 'low_fat', name: 'Low Fat', description: '≤30% calories from fat' },
    { id: 'keto', name: 'Keto', description: '≤10% carbs, ≥60% fat, ≤15g carbs' },
    { id: 'bmi_based', name: 'BMI-based (Auto)', description: 'Auto-determined from your BMI' }
  ];

  const activityLevelOptions = [
    { id: 'sedentary', name: 'Sedentary (little or no exercise)' },
    { id: 'light', name: 'Light (exercise 1-3 days/week)' },
    { id: 'moderate', name: 'Moderate (exercise 3-5 days/week)' },
    { id: 'active', name: 'Active (exercise 6-7 days/week)' },
    { id: 'very_active', name: 'Very Active (hard exercise daily)' }
  ];

  // Helper function to get cuisine flag
  const getCuisineFlag = (cuisineName: string) => {
    const cuisineId = cuisineName.toLowerCase().replace(/\s+/g, '_');
    const flags: { [key: string]: JSX.Element } = {
      american: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path d="M1.638,5.846H30.362c-.711-1.108-1.947-1.846-3.362-1.846H5c-1.414,0-2.65,.738-3.362,1.846Z" fill="#a62842"></path>
          <path d="M5,4h11v12.923H1V8c0-2.208,1.792-4,4-4Z" fill="#102d5e"></path>
        </svg>
      ),
      chinese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#db362f"></rect>
          <path fill="#ff0" d="M7.958 10.152L7.19 7.786 6.421 10.152 3.934 10.152 5.946 11.614 5.177 13.979 7.19 12.517 9.202 13.979 8.433 11.614 10.446 10.152 7.958 10.152z"></path>
        </svg>
      ),
      italian: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#41914d"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#bf393b"></path>
        </svg>
      ),
      mexican: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#2c6748"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#be2a2c"></path>
        </svg>
      ),
      french: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#092050"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#be2a2c"></path>
        </svg>
      ),
      vietnamese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#c93728"></rect>
          <path fill="#ff5" d="M18.008 16.366L21.257 14.006 17.241 14.006 16 10.186 14.759 14.006 10.743 14.006 13.992 16.366 12.751 20.186 16 17.825 19.249 20.186 18.008 16.366z"></path>
        </svg>
      ),
      japanese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <circle cx="16" cy="16" r="6" fill="#ae232f"></circle>
        </svg>
      ),
      indian: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <path fill="#fff" d="M1 11H31V21H1z"></path>
          <path d="M5,4H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" fill="#e06535"></path>
          <path d="M5,20H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" transform="rotate(180 16 24)" fill="#2c6837"></path>
        </svg>
      ),
      korean: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path d="M12.229,13.486c1.389-2.083,4.203-2.646,6.286-1.257s2.646,4.203,1.257,6.286l-7.543-5.029Z" fill="#be3b3e"></path>
          <path d="M12.229,13.486c-1.389,2.083-.826,4.897,1.257,6.286s4.897,.826,6.286-1.257c.694-1.041,.413-2.449-.629-3.143s-2.449-.413-3.143,.629l-3.771-2.514Z" fill="#1c449c"></path>
        </svg>
      ),
      british: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path fill="#be2a2a" d="M31 14L18 14 18 4 14 4 14 14 1 14 1 18 14 18 14 28 18 28 18 18 31 18 31 14z"></path>
        </svg>
      ),
      thai: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <path fill="#282646" d="M1 11H31V21H1z"></path>
          <path d="M5,4H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" fill="#992532"></path>
          <path d="M5,20H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" transform="rotate(180 16 24)" fill="#992532"></path>
          <path fill="#fff" d="M1 9H31V12H1z"></path>
          <path fill="#fff" d="M1 20H31V23H1z"></path>
        </svg>
      ),
      no_preference: (
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#e0e0e0"></rect>
          <path d="M11,16h10M16,11v10" stroke="#999" strokeWidth="2" strokeLinecap="round"></path>
        </svg>
      )
    };
    return flags[cuisineId] || null;
  };

  // Cuisines list (same as Onboarding)
  const cuisines = [
    { id: 'american', name: 'American' },
    { id: 'chinese', name: 'Chinese' },
    { id: 'italian', name: 'Italian' },
    { id: 'mexican', name: 'Mexican' },
    { id: 'french', name: 'French' },
    { id: 'vietnamese', name: 'Vietnamese' },
    { id: 'japanese', name: 'Japanese' },
    { id: 'indian', name: 'Indian' },
    { id: 'korean', name: 'Korean' },
    { id: 'british', name: 'British' },
    { id: 'thai', name: 'Thai' },
    { id: 'no_preference', name: 'No Preference' }
  ];

  useEffect(() => {
    const userId = getUserId();
    if (userId && !hasLoadedRef.current) {
      hasLoadedRef.current = true;
      loadUserData();
      loadActivityStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (genderDropdownRef.current && !genderDropdownRef.current.contains(event.target as Node)) {
        setIsGenderDropdownOpen(false);
      }
      if (dietaryModeDropdownRef.current && !dietaryModeDropdownRef.current.contains(event.target as Node)) {
        setIsDietaryModeDropdownOpen(false);
      }
      if (cuisineDropdownRef.current && !cuisineDropdownRef.current.contains(event.target as Node)) {
        setIsCuisineDropdownOpen(false);
      }
      if (activityLevelDropdownRef.current && !activityLevelDropdownRef.current.contains(event.target as Node)) {
        setIsActivityLevelDropdownOpen(false);
      }
    };

    if (isGenderDropdownOpen || isDietaryModeDropdownOpen || isCuisineDropdownOpen || isActivityLevelDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isGenderDropdownOpen, isDietaryModeDropdownOpen, isCuisineDropdownOpen, isActivityLevelDropdownOpen]);

  // Reload data when navigating to Profile page (e.g., after Onboarding or returning from History)
  useEffect(() => {
    const userId = getUserId();
    if (userId && location.pathname === '/profile' && hasLoadedRef.current) {
      // Reload data when user navigates to Profile page to get latest data
      loadUserData();
      loadActivityStats();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.pathname]);

  // Listen for interaction updates from other components (e.g., History, Home)
  useEffect(() => {
    const handleInteractionUpdate = () => {
      // Reload activity stats when interaction is updated
      loadActivityStats();
    };

    window.addEventListener('interactionUpdated', handleInteractionUpdate);
    return () => {
      window.removeEventListener('interactionUpdated', handleInteractionUpdate);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
      // Initialize dietary plan fields
      // If auto_dietary_plan is true, set to 'bmi_based', otherwise use dietary_plan
      if (user?.auto_dietary_plan) {
        setEditingDietaryPlan('bmi_based');
      } else {
        setEditingDietaryPlan(user?.dietary_plan || 'none');
      }
      setEditingWeightKg(user?.weight_kg || '');
      setEditingHeightCm(user?.height_cm || '');
      setEditingActivityLevel(user?.activity_level || '');
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
    const userId = getUserId();
    if (userId) {
      await Promise.all([
        loadUserProfile(userId),
        loadUserAllergies(userId),
        loadUserFavoriteCuisines(userId)
      ]);
    }
  };

  const loadActivityStats = async () => {
    const userId = getUserId();
    if (!userId) return;

    try {
      // Try to get stats from stats endpoint first
      const statsRes = await apiService.getUserInteractionStats(userId);
      if (statsRes.data && statsRes.data.stats) {
        // Use rating_count directly from stats endpoint
        setActivityStats({
          likedRecipes: statsRes.data.stats.like_count || 0,
          viewedRecipes: statsRes.data.stats.view_count || 0,
          ratedRecipes: statsRes.data.stats.rating_count || 0
        });
        return;
      }
    } catch (err) {
      // Fallback to calculating from interactions
      try {
        const interactionsRes = await apiService.getUserInteractions(userId, undefined, 1000, 0);
        if (interactionsRes.data) {
          // Response structure when no event_type: { likes: [], views: [], ratings: [] }
          // Response structure when event_type='like': { interactions: [{ recipe_id: ... }] }
          const data = interactionsRes.data as any; // Use type assertion for flexible response structure
          if (data.likes && Array.isArray(data.likes)) {
            // Response without event_type filter
            setActivityStats({
              likedRecipes: data.likes?.length || 0,
              viewedRecipes: data.views?.length || 0,
              ratedRecipes: data.ratings?.length || 0
            });
          } else if (data.interactions && Array.isArray(data.interactions)) {
            // Response with event_type filter (shouldn't happen with undefined event_type, but handle it)
            const interactions = data.interactions || [];
            const liked = interactions.filter((i: any) => i.liked === true).length;
            const viewed = interactions.filter((i: any) => i.view_count && i.view_count > 0).length;
            const rated = interactions.filter((i: any) => i.rating && i.rating > 0).length;
            
            setActivityStats({
              likedRecipes: liked,
              viewedRecipes: viewed,
              ratedRecipes: rated
            });
          }
        }
      } catch (err2) {
        console.error('Failed to load activity stats:', err2);
      }
    }
  };

  const loadAvailableOptions = async () => {
    try {
      const ingredientsRes = await apiService.getIngredients();
      
      if (ingredientsRes.data && ingredientsRes.data.ingredients) {
        setAvailableIngredients(ingredientsRes.data.ingredients);
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
    setEditingUsername('');
    setEditingName('');
    setEditingAge('');
    setEditingGender('');
    setEditingDietaryPlan('none');
    setEditingWeightKg('');
    setEditingHeightCm('');
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
  };

  const handleRemoveCuisine = (cuisineName: string) => {
    setEditingCuisines(editingCuisines.filter(c => c.name !== cuisineName));
  };

  const handleSaveChanges = async () => {
    setIsSaving(true);
    const userId = getUserId();
    if (!userId) {
      setNotification({ message: 'User not found', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
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

      // Add dietary mode information
      if (editingDietaryPlan && editingDietaryPlan !== 'none') {
        if (editingDietaryPlan === 'bmi_based') {
          // BMI-based: calculate BMI and determine dietary_plan automatically
          if (editingHeightCm && editingWeightKg) {
            const heightCm = typeof editingHeightCm === 'number' ? editingHeightCm : parseFloat(String(editingHeightCm));
            const weightKg = typeof editingWeightKg === 'number' ? editingWeightKg : parseFloat(String(editingWeightKg));
            
            if (heightCm > 0 && weightKg > 0) {
              // Calculate BMI: weight (kg) / (height (m))^2
              const heightM = heightCm / 100.0;
              const calculatedBMI = weightKg / (heightM * heightM);
              
              // Determine dietary_plan from BMI (matching recommend_graph.py logic)
              let bmiBasedPlan: string | null = null;
              if (calculatedBMI < 18.5) {
                bmiBasedPlan = 'weight_gain';  // High-protein + High-calorie
              } else if (calculatedBMI > 24.9) {
                bmiBasedPlan = 'weight_loss';  // Low-carb + High-protein + Low-fat
              }
              // BMI 18.5-24.9: balanced diet (no dietary_plan filter)
              
              // Set auto_dietary_plan to true and save BMI data
              profileUpdate.auto_dietary_plan = true;
              profileUpdate.height_cm = heightCm;
              profileUpdate.weight_kg = weightKg;
              profileUpdate.bmi = calculatedBMI;
              
              // Save activity level if provided
              if (editingActivityLevel) {
                profileUpdate.activity_level = editingActivityLevel;
              }
              
              // Only set dietary_plan if BMI is outside normal range
              if (bmiBasedPlan) {
                profileUpdate.dietary_plan = bmiBasedPlan;
                console.log(`✅ BMI-based plan: BMI=${calculatedBMI.toFixed(1)} → ${bmiBasedPlan}`);
              } else {
                profileUpdate.dietary_plan = null; // Clear dietary_plan for balanced BMI
                console.log(`✅ BMI-based plan: BMI=${calculatedBMI.toFixed(1)} → Balanced (no filter)`);
              }
            }
          }
        } else {
          // Other dietary modes: set dietary_plan directly
          // Valid values: "low_carb", "high_protein", "low_fat", "keto"
          profileUpdate.dietary_plan = editingDietaryPlan;
          profileUpdate.auto_dietary_plan = false;
          // Clear BMI-related fields when not using BMI-based
          if (editingDietaryPlan !== 'bmi_based') {
            profileUpdate.height_cm = null;
            profileUpdate.weight_kg = null;
            profileUpdate.bmi = null;
            profileUpdate.activity_level = null;
          }
        }
      } else {
        // No dietary plan selected - clear dietary plan
        console.log('✅ Clearing dietary plan (user selected "none")');
        profileUpdate.dietary_plan = null;
        profileUpdate.auto_dietary_plan = false;
        // Note: Keep BMI fields as they are useful information
      }

      // Log what we're about to send
      console.log('📤 Sending profile update:', profileUpdate);

      if (Object.keys(profileUpdate).length > 0) {
        const response = await apiService.updateUserProfile(userId, profileUpdate);
        console.log('📥 Profile update response:', response);
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

      // Update diets (create Diet nodes and FOLLOWS_DIET relationships automatically)
      // Similar to how Cuisine nodes are created automatically
      if (editingDietaryPlan && editingDietaryPlan !== 'none' && editingDietaryPlan !== 'bmi_based') {
        // For explicit dietary modes (low_carb, high_protein, low_fat, keto), create Diet nodes
        const dietsToCreate: string[] = [editingDietaryPlan];
        
        try {
          await apiService.updateUserDiets(userId, { diets: dietsToCreate });
          console.log(`✅ Created Diet nodes: ${dietsToCreate.join(', ')}`);
        } catch (err) {
          console.error('⚠️ Failed to create Diet nodes (non-blocking):', err);
          // Don't block profile update if diet creation fails
        }
      } else if (editingDietaryPlan === 'none' || (!editingDietaryPlan && user?.dietary_plan)) {
        // If user selects "none" or clears dietary plan, remove all Diet relationships
        try {
          await apiService.updateUserDiets(userId, { diets: [] });
          console.log('✅ Removed all Diet relationships');
        } catch (err) {
          console.error('⚠️ Failed to remove Diet relationships (non-blocking):', err);
        }
      }
      // Note: For BMI-based, don't create Diet nodes (dietary_plan is set in profile instead)

      // Reload data
      await loadUserData();
      setIsEditing(false);
      setIngredientSearch('');
      setNotification({ message: 'Profile updated successfully!', type: 'success' });
      setTimeout(() => setNotification(null), 3000);
    } catch (err) {
      console.error('Failed to save changes:', err);
      setNotification({ message: 'Failed to save changes. Please try again.', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
    } finally {
      setIsSaving(false);
    }
  };

  const handleViewHistory = () => {
    navigate('/history');
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setNotification({ message: 'Please select an image file', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setNotification({ message: 'Image size must be less than 5MB', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
      return;
    }

    setIsUploadingAvatar(true);
    const userId = getUserId();
    if (!userId) {
      setNotification({ message: 'User not found', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
      setIsUploadingAvatar(false);
      return;
    }

    try {
      const response = await apiService.uploadAvatar(userId, file);
      if (response.error) {
        setNotification({ message: `Failed to upload avatar: ${response.error}`, type: 'error' });
        setTimeout(() => setNotification(null), 3000);
      } else {
        // Reload user profile to get updated avatar_url
        await loadUserData();
        setNotification({ message: 'Avatar updated successfully!', type: 'success' });
        setTimeout(() => setNotification(null), 3000);
      }
    } catch (err) {
      console.error('Failed to upload avatar:', err);
      setNotification({ message: 'Failed to upload avatar. Please try again.', type: 'error' });
      setTimeout(() => setNotification(null), 3000);
    } finally {
      setIsUploadingAvatar(false);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
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
              <div 
                className="avatar-circle avatar-container"
                onClick={handleAvatarClick}
                style={{ cursor: 'pointer', position: 'relative', marginLeft: 0 }}
                title="Click to change avatar"
              >
                {user?.avatar_url ? (
                  <img 
                    src={user.avatar_url} 
                    alt="Avatar" 
                    className="avatar-image"
                    style={{
                      width: '100%',
                      height: '100%',
                      borderRadius: '50%',
                      objectFit: 'cover'
                    }}
                  />
                ) : (
                  <span className="avatar-initials">
                    {user?.name ? user.name.charAt(0).toUpperCase() : (user?.username ? user.username.charAt(0).toUpperCase() : 'U')}
                  </span>
                )}
                {isUploadingAvatar && (
                  <div className="avatar-upload-overlay">
                    <div className="loading-spinner" style={{ width: '30px', height: '30px', borderWidth: '3px' }}></div>
                  </div>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                style={{ display: 'none' }}
              />
            </div>
            <div className="user-name" style={{ fontSize: '2.2rem', fontWeight: '600', marginTop: '1rem' }}>
              {user?.name || user?.username || 'Guest User'}
            </div>
            <div className="user-username" style={{ fontSize: '0.95rem', color: '#666', marginTop: '0.5rem', marginBottom: 'var(--spacing-lg)' }}>
              @{user?.username?.toLowerCase().replace(/\s+/g, '_') || 'guest'}
            </div>
             <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-sm)', alignItems: 'flex-start', width: '100%' }}>
               <button 
                 className="edit-profile-btn" 
                 onClick={handleEditProfile}
                 style={{
                   width: '100%',
                   maxWidth: '280px',
                  padding: 'var(--spacing-sm) var(--spacing-md)',
                  backgroundColor: '#f5f5f5',
                  border: '1px solid #666',
                  borderRadius: 'var(--radius-md)',
                  color: '#333',
                  fontSize: 'var(--text-sm)',
                  fontWeight: 'var(--font-medium)',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: 'var(--spacing-xs)',
                  transition: 'all 0.2s ease'
                }}
              >
                <span className="edit-icon">✏️</span>
                Edit Profile
              </button>
              <div
                onClick={() => {
                  logout();
                  navigate('/');
                }}
                 style={{
                   display: 'flex',
                   alignItems: 'center',
                   justifyContent: 'center',
                   gap: 'var(--spacing-xs)',
                   color: '#dc3545',
                   cursor: 'pointer',
                   fontSize: 'var(--text-sm)',
                   marginTop: 'var(--spacing-xs)',
                   textDecoration: 'none',
                   width: '100%',
                   maxWidth: '280px'
                 }}
               >
                 <span>→</span>
                 <span>Logout</span>
               </div>
            </div>
          </div>

          {/* Right Section */}
          <div className="profile-right">
            {/* Food Preferences Section */}
            <h2 className="section-title" style={{ marginBottom: '-50px', fontSize: 'var(--text-3xl)' }}>Food Preferences</h2>
            <div className="preferences-section">
              <div className="preferences-content">
                <div className="preference-group" style={{ marginBottom: 'var(--spacing-md)' }}>
                  <h3 className="preference-label">Favorite Cuisines</h3>
                  <div className="tags-container">
                    {favoriteCuisines?.favorite_cuisines && favoriteCuisines.favorite_cuisines.length > 0 ? (
                      favoriteCuisines.favorite_cuisines.map((cuisine: any, index: number) => (
                        <span key={index} className="tag tag-cuisine" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                          {getCuisineFlag(cuisine.cuisine_name)}
                          {cuisine.cuisine_name}
                        </span>
                      ))
                    ) : (
                      <span className="empty-tag">No cuisines selected</span>
                    )}
                  </div>
                </div>

                <div className="preference-group" style={{ marginBottom: 'var(--spacing-md)' }}>
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
                    </div>
                    
                    <div className="edit-modal-content">
                      <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr', gap: 'var(--spacing-3xl)', alignItems: 'start' }}>
                        {/* Left Column - Avatar */}
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--spacing-md)' }}>
                          <div 
                            className="avatar-circle"
                            style={{ position: 'relative', width: '150px', height: '150px', cursor: 'default' }}
                          >
                            {user?.avatar_url ? (
                              <img 
                                src={user.avatar_url} 
                                alt="Avatar" 
                                className="avatar-image"
                                style={{
                                  width: '100%',
                                  height: '100%',
                                  borderRadius: '50%',
                                  objectFit: 'cover'
                                }}
                              />
                            ) : (
                              <span className="avatar-initials">
                                {user?.name ? user.name.charAt(0).toUpperCase() : (user?.username ? user.username.charAt(0).toUpperCase() : 'U')}
                              </span>
                            )}
                            {isUploadingAvatar && (
                              <div className="avatar-upload-overlay">
                                <div className="loading-spinner" style={{ width: '30px', height: '30px', borderWidth: '3px' }}></div>
                              </div>
                            )}
                          </div>
                          <button
                            onClick={handleAvatarClick}
                            disabled={isUploadingAvatar}
                            style={{
                              padding: 'var(--spacing-sm) var(--spacing-lg)',
                              backgroundColor: '#ff8c42',
                              border: 'none',
                              borderRadius: 'var(--radius-md)',
                              color: 'white',
                              fontSize: 'var(--text-sm)',
                              fontWeight: 'var(--font-medium)',
                              cursor: isUploadingAvatar ? 'not-allowed' : 'pointer',
                              opacity: isUploadingAvatar ? 0.6 : 1,
                              transition: 'all 0.2s ease'
                            }}
                          >
                            {isUploadingAvatar ? 'Uploading...' : 'Change Photo'}
                          </button>
                          <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleAvatarChange}
                            style={{ display: 'none' }}
                          />
                        </div>

                        {/* Right Column - Form Fields */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
                          {/* Personal Information Section */}
                          <div className="edit-section">
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)', alignItems: 'start' }}>
                              <div className="edit-form-field" style={{ width: '100%' }}>
                                <label htmlFor="edit-name">Full Name</label>
                                <input
                                  id="edit-name"
                                  type="text"
                                  placeholder="Enter your name"
                                  value={editingName}
                                  onChange={(e) => setEditingName(e.target.value)}
                                  className="edit-form-input"
                                  style={{ width: '100%' }}
                                />
                              </div>
                              <div className="edit-form-field" style={{ width: '100%' }}>
                                <label htmlFor="edit-username">Username</label>
                                <input
                                  id="edit-username"
                                  type="text"
                                  placeholder="Enter username"
                                  value={editingUsername}
                                  disabled
                                  className="edit-form-input"
                                  style={{ width: '100%', backgroundColor: '#f5f5f5', cursor: 'not-allowed', color: '#666' }}
                                  title="Username cannot be changed"
                                />
                              </div>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-md)', marginTop: 'var(--spacing-md)' }}>
                              <div className="edit-form-field">
                                <label htmlFor="edit-gender">Gender</label>
                                <div className="custom-dropdown" ref={genderDropdownRef}>
                                  <div 
                                    className="custom-dropdown-select"
                                    onClick={() => setIsGenderDropdownOpen(!isGenderDropdownOpen)}
                                  >
                                    <span className={`custom-dropdown-value ${!editingGender ? 'placeholder' : ''}`}>
                                      {editingGender 
                                        ? genderOptions.find(g => g.id === editingGender)?.name || 'Select gender'
                                        : 'Select gender'}
                                    </span>
                                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                                      <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                                    </svg>
                                  </div>
                                  {isGenderDropdownOpen && (
                                    <div className="custom-dropdown-list">
                                      {genderOptions.map(option => (
                                        <div
                                          key={option.id}
                                          className={`custom-dropdown-item ${editingGender === option.id ? 'selected' : ''}`}
                                          onClick={() => {
                                            setEditingGender(option.id);
                                            setIsGenderDropdownOpen(false);
                                          }}
                                        >
                                          {option.name}
                                          {editingGender === option.id && (
                                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                              <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#85DCB0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                            </svg>
                                          )}
                                        </div>
                                      ))}
                                    </div>
                                  )}
                                </div>
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
                            </div>
                          </div>

                      {/* Favorite Cuisines Section */}
                      <div className="edit-section" style={{ marginBottom: '0px', marginTop: '-15px' }}>
                        <h3>Favorite Cuisines</h3>
                        <div className="edit-form-field">
                          <div className="custom-dropdown" ref={cuisineDropdownRef}>
                            <div 
                              className="custom-dropdown-select"
                              onClick={() => setIsCuisineDropdownOpen(!isCuisineDropdownOpen)}
                            >
                              <span className="custom-dropdown-value placeholder">
                                Select cuisine...
                              </span>
                              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                                <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                              </svg>
                            </div>
                            {isCuisineDropdownOpen && (
                              <div className="custom-dropdown-list">
                                {cuisines
                                  .filter(c => !editingCuisines.find(ec => ec.name === c.name))
                                  .map(cuisine => (
                                    <div
                                      key={cuisine.id}
                                      className="custom-dropdown-item"
                                      onClick={() => {
                                        handleAddCuisine(cuisine.name);
                                        setIsCuisineDropdownOpen(false);
                                      }}
                                    >
                                      {cuisine.name}
                                    </div>
                                  ))}
                              </div>
                            )}
                          </div>
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
                      <div className="edit-section" style={{ marginBottom: '0px', marginTop: '-35px'}}>
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
                                        <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#85DCB0" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
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
            <h2 className="section-title" style={{ marginTop: '-20px', marginBottom: '-50px', fontSize: 'var(--text-3xl)' }}>My Activity Summary</h2>
            <div className="activity-section">
              <div className="activity-cards">
                <div className="activity-card">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
                    <div className="activity-icon activity-icon-saved">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#8B4513" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        <circle cx="12" cy="12" r="3" stroke="#8B4513" strokeWidth="1.5" fill="none"/>
                      </svg>
                    </div>
                    <div className="activity-label">Viewed Recipes</div>
                  </div>
                  <div className="activity-count">{activityStats.viewedRecipes}</div>
                </div>
                <div className="activity-card">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
                    <div className="activity-icon activity-icon-liked">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" stroke="#ff6b9d" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    </div>
                    <div className="activity-label">Liked Recipes</div>
                  </div>
                  <div className="activity-count">{activityStats.likedRecipes}</div>
                </div>
                <div className="activity-card">
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-xs)' }}>
                    <div className="activity-icon activity-icon-rated">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="#ffd700" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    </div>
                    <div className="activity-label">Rated Recipes</div>
                  </div>
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

      {/* Notification Toast */}
      {notification && (
        <div className={`notification-toast ${notification.type}`}>
          <div className="notification-content">
            {notification.type === 'success' ? (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17L4 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            ) : (
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2"/>
                <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                <line x1="12" y1="16" x2="12.01" y2="16" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            )}
            <span>{notification.message}</span>
          </div>
          <button className="notification-close" onClick={() => setNotification(null)}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      )}
    </div>
  );
};

export default Profile;
