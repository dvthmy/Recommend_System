import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { UserPreferences } from '../types';
import { getUserId, setUserId } from '../utils/auth';
import './Onboarding.css';

interface AvailableIngredient {
  id: string;
  name: string;
}

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const { user, setUser, updateUserProfile, loadUserProfile, loadUserAllergies, loadUserFavoriteCuisines, allergies, favoriteCuisines, error } = useUser();
  
  // Determine if user has completed onboarding before
  // If completed_onboarding is true, user has done onboarding before → show only 2 questions (Meal Types, Cooking Time)
  // If completed_onboarding is false/undefined, user is new (guest or first-time login) → show 4 questions (Allergies, Favorite Cuisines, Meal Types, Cooking Time)
  
  // Check if user is guest
  const hasAccessToken = !!localStorage.getItem('access_token');
  const hasUsername = !!user?.username;
  const isGuest = !hasAccessToken || (user && !hasUsername);
  
  // User has completed onboarding if:
  // 1. Registered user: user.completed_onboarding === true
  // 2. Guest user: user.completed_onboarding === true (if created in DB) or check from user object
  const hasCompletedOnboardingBefore = user?.completed_onboarding === true;
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
  const [searchResults, setSearchResults] = useState<AvailableIngredient[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isMealTypeDropdownOpen, setIsMealTypeDropdownOpen] = useState(false);
  const mealTypeDropdownRef = useRef<HTMLDivElement>(null);
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const genderDropdownRef = useRef<HTMLDivElement>(null);
  const [isAgeGroupDropdownOpen, setIsAgeGroupDropdownOpen] = useState(false);
  const ageGroupDropdownRef = useRef<HTMLDivElement>(null);
  const [isDietaryModeDropdownOpen, setIsDietaryModeDropdownOpen] = useState(false);
  const dietaryModeDropdownRef = useRef<HTMLDivElement>(null);
  const [isActivityLevelDropdownOpen, setIsActivityLevelDropdownOpen] = useState(false);
  const activityLevelDropdownRef = useRef<HTMLDivElement>(null);
  const hasLoadedDataRef = useRef(false);
  
  // Age and Gender state (for guest users only)
  const [ageGroup, setAgeGroup] = useState<string>('');
  const [gender, setGender] = useState<string>('');
  
  // Dietary mode state
  const [dietaryMode, setDietaryMode] = useState<string>('');
  const [bmiHeight, setBmiHeight] = useState<string>('');
  const [bmiWeight, setBmiWeight] = useState<string>('');
  const [bmiActivityLevel, setBmiActivityLevel] = useState<string>('');
  
  // Age group options matching database values
  const ageGroupOptions = [
    { id: '<18', name: 'Under 18', minAge: 1, maxAge: 17, avgAge: 15 },
    { id: '18-30', name: '18 - 30', minAge: 18, maxAge: 30, avgAge: 24 },
    { id: '30-34', name: '31 - 34', minAge: 31, maxAge: 34, avgAge: 32.5 },
    { id: '35-44', name: '35 - 44', minAge: 35, maxAge: 44, avgAge: 39.5 },
    { id: '45-54', name: '45 - 54', minAge: 45, maxAge: 54, avgAge: 49.5 },
    { id: '55+', name: '55 and above', minAge: 55, maxAge: 100, avgAge: 65 }
  ];

  useEffect(() => {
    // Prevent multiple API calls if component re-renders
    if (hasLoadedDataRef.current) {
      return;
    }
    
    hasLoadedDataRef.current = true;
    loadAvailableIngredients();
    const userId = getUserId();
    if (userId) {
      // Load full user profile to get completed_onboarding status
      // For registered users: completed_onboarding will be loaded from DB
      // For guest users: completed_onboarding might be undefined, but we check localStorage flag
      loadUserProfile(userId);
      loadUserAllergies(userId);
      loadUserFavoriteCuisines(userId);
    } else {
      // If no userId, ensure favoriteCuisines is null so the section shows
      // This is already the default state, but we make it explicit
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (mealTypeDropdownRef.current && !mealTypeDropdownRef.current.contains(event.target as Node)) {
        setIsMealTypeDropdownOpen(false);
      }
      if (genderDropdownRef.current && !genderDropdownRef.current.contains(event.target as Node)) {
        setIsGenderDropdownOpen(false);
      }
      if (ageGroupDropdownRef.current && !ageGroupDropdownRef.current.contains(event.target as Node)) {
        setIsAgeGroupDropdownOpen(false);
      }
      if (dietaryModeDropdownRef.current && !dietaryModeDropdownRef.current.contains(event.target as Node)) {
        setIsDietaryModeDropdownOpen(false);
      }
      if (activityLevelDropdownRef.current && !activityLevelDropdownRef.current.contains(event.target as Node)) {
        setIsActivityLevelDropdownOpen(false);
      }
    };

    if (isMealTypeDropdownOpen || isGenderDropdownOpen || isAgeGroupDropdownOpen || isDietaryModeDropdownOpen || isActivityLevelDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMealTypeDropdownOpen, isGenderDropdownOpen, isAgeGroupDropdownOpen, isDietaryModeDropdownOpen, isActivityLevelDropdownOpen]);

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

  // Flag SVGs for each cuisine
  const getCuisineFlag = (cuisineId: string) => {
    const flags: { [key: string]: JSX.Element } = {
      american: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path d="M1.638,5.846H30.362c-.711-1.108-1.947-1.846-3.362-1.846H5c-1.414,0-2.65,.738-3.362,1.846Z" fill="#a62842"></path>
          <path d="M2.03,7.692c-.008,.103-.03,.202-.03,.308v1.539H31v-1.539c0-.105-.022-.204-.03-.308H2.03Z" fill="#a62842"></path>
          <path fill="#a62842" d="M2 11.385H31V13.231H2z"></path>
          <path fill="#a62842" d="M2 15.077H31V16.923000000000002H2z"></path>
          <path fill="#a62842" d="M1 18.769H31V20.615H1z"></path>
          <path d="M1,24c0,.105,.023,.204,.031,.308H30.969c.008-.103,.031-.202,.031-.308v-1.539H1v1.539Z" fill="#a62842"></path>
          <path d="M30.362,26.154H1.638c.711,1.108,1.947,1.846,3.362,1.846H27c1.414,0,2.65-.738,3.362-1.846Z" fill="#a62842"></path>
          <path d="M5,4h11v12.923H1V8c0-2.208,1.792-4,4-4Z" fill="#102d5e"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
          <path fill="#fff" d="M4.601 7.463L5.193 7.033 4.462 7.033 4.236 6.338 4.01 7.033 3.279 7.033 3.87 7.463 3.644 8.158 4.236 7.729 4.827 8.158 4.601 7.463z"></path>
          <path fill="#fff" d="M7.58 7.463L8.172 7.033 7.441 7.033 7.215 6.338 6.989 7.033 6.258 7.033 6.849 7.463 6.623 8.158 7.215 7.729 7.806 8.158 7.58 7.463z"></path>
          <path fill="#fff" d="M10.56 7.463L11.151 7.033 10.42 7.033 10.194 6.338 9.968 7.033 9.237 7.033 9.828 7.463 9.603 8.158 10.194 7.729 10.785 8.158 10.56 7.463z"></path>
          <path fill="#fff" d="M6.066 9.283L6.658 8.854 5.927 8.854 5.701 8.158 5.475 8.854 4.744 8.854 5.335 9.283 5.109 9.979 5.701 9.549 6.292 9.979 6.066 9.283z"></path>
          <path fill="#fff" d="M9.046 9.283L9.637 8.854 8.906 8.854 8.68 8.158 8.454 8.854 7.723 8.854 8.314 9.283 8.089 9.979 8.68 9.549 9.271 9.979 9.046 9.283z"></path>
          <path fill="#fff" d="M12.025 9.283L12.616 8.854 11.885 8.854 11.659 8.158 11.433 8.854 10.702 8.854 11.294 9.283 11.068 9.979 11.659 9.549 12.251 9.979 12.025 9.283z"></path>
          <path fill="#fff" d="M6.066 12.924L6.658 12.494 5.927 12.494 5.701 11.799 5.475 12.494 4.744 12.494 5.335 12.924 5.109 13.619 5.701 13.19 6.292 13.619 6.066 12.924z"></path>
          <path fill="#fff" d="M9.046 12.924L9.637 12.494 8.906 12.494 8.68 11.799 8.454 12.494 7.723 12.494 8.314 12.924 8.089 13.619 8.68 13.19 9.271 13.619 9.046 12.924z"></path>
          <path fill="#fff" d="M12.025 12.924L12.616 12.494 11.885 12.494 11.659 11.799 11.433 12.494 10.702 12.494 11.294 12.924 11.068 13.619 11.659 13.19 12.251 13.619 12.025 12.924z"></path>
          <path fill="#fff" d="M13.539 7.463L14.13 7.033 13.399 7.033 13.173 6.338 12.947 7.033 12.216 7.033 12.808 7.463 12.582 8.158 13.173 7.729 13.765 8.158 13.539 7.463z"></path>
          <path fill="#fff" d="M4.601 11.104L5.193 10.674 4.462 10.674 4.236 9.979 4.01 10.674 3.279 10.674 3.87 11.104 3.644 11.799 4.236 11.369 4.827 11.799 4.601 11.104z"></path>
          <path fill="#fff" d="M7.58 11.104L8.172 10.674 7.441 10.674 7.215 9.979 6.989 10.674 6.258 10.674 6.849 11.104 6.623 11.799 7.215 11.369 7.806 11.799 7.58 11.104z"></path>
          <path fill="#fff" d="M10.56 11.104L11.151 10.674 10.42 10.674 10.194 9.979 9.968 10.674 9.237 10.674 9.828 11.104 9.603 11.799 10.194 11.369 10.785 11.799 10.56 11.104z"></path>
          <path fill="#fff" d="M13.539 11.104L14.13 10.674 13.399 10.674 13.173 9.979 12.947 10.674 12.216 10.674 12.808 11.104 12.582 11.799 13.173 11.369 13.765 11.799 13.539 11.104z"></path>
          <path fill="#fff" d="M4.601 14.744L5.193 14.315 4.462 14.315 4.236 13.619 4.01 14.315 3.279 14.315 3.87 14.744 3.644 15.44 4.236 15.01 4.827 15.44 4.601 14.744z"></path>
          <path fill="#fff" d="M7.58 14.744L8.172 14.315 7.441 14.315 7.215 13.619 6.989 14.315 6.258 14.315 6.849 14.744 6.623 15.44 7.215 15.01 7.806 15.44 7.58 14.744z"></path>
          <path fill="#fff" d="M10.56 14.744L11.151 14.315 10.42 14.315 10.194 13.619 9.968 14.315 9.237 14.315 9.828 14.744 9.603 15.44 10.194 15.01 10.785 15.44 10.56 14.744z"></path>
          <path fill="#fff" d="M13.539 14.744L14.13 14.315 13.399 14.315 13.173 13.619 12.947 14.315 12.216 14.315 12.808 14.744 12.582 15.44 13.173 15.01 13.765 15.44 13.539 14.744z"></path>
        </svg>
      ),
      chinese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#db362f"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path fill="#ff0" d="M7.958 10.152L7.19 7.786 6.421 10.152 3.934 10.152 5.946 11.614 5.177 13.979 7.19 12.517 9.202 13.979 8.433 11.614 10.446 10.152 7.958 10.152z"></path>
          <path fill="#ff0" d="M12.725 8.187L13.152 8.898 13.224 8.072 14.032 7.886 13.269 7.562 13.342 6.736 12.798 7.361 12.035 7.037 12.461 7.748 11.917 8.373 12.725 8.187z"></path>
          <path fill="#ff0" d="M14.865 10.372L14.982 11.193 15.37 10.46 16.187 10.602 15.61 10.007 15.997 9.274 15.253 9.639 14.675 9.044 14.793 9.865 14.048 10.23 14.865 10.372z"></path>
          <path fill="#ff0" d="M15.597 13.612L16.25 13.101 15.421 13.13 15.137 12.352 14.909 13.149 14.081 13.179 14.769 13.642 14.541 14.439 15.194 13.928 15.881 14.391 15.597 13.612z"></path>
          <path fill="#ff0" d="M13.26 15.535L13.298 14.707 12.78 15.354 12.005 15.062 12.46 15.754 11.942 16.402 12.742 16.182 13.198 16.875 13.236 16.047 14.036 15.827 13.26 15.535z"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      italian: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#41914d"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#bf393b"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      mexican: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#2c6748"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#be2a2c"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
          <path fill="#bb3433" d="M17.875 19.221L17.874 19.221 17.875 19.221 17.875 19.221z"></path>
          <path fill="#bb3433" d="M19.08 17.788L19.08 17.788 19.08 17.788 19.08 17.788z"></path>
          <path fill="#bb3433" d="M15.938 18.943L15.938 18.944 15.938 18.944 15.938 18.943z"></path>
          <path fill="#bb3433" d="M16.305 19.76L16.305 19.76 16.305 19.76 16.305 19.76z"></path>
          <path fill="#854a29" d="M16.196 16.434L16.196 16.434 16.196 16.434 16.196 16.434z"></path>
          <path d="M14.757,12.878h0s0,0,0,0Z" fill="#854a29"></path>
          <path fill="#854a29" d="M15.137 12.715L15.137 12.715 15.137 12.715 15.137 12.715z"></path>
          <path d="M18.701,18.611c-.462-.69-.74,.319-1.215,.252,.125-.81-.778-.5-1.196-.312l.165-.241c-.625,.291-1.368-.712-1.816,.028-.095-.205-.882-.689-1.201-.328,.025-1.017-1.723-.957-.807,.081,.63,.179,.975,.964,1.915,.554,.129,.53,1.025,.583,1.413,.297-.052,.161-.027,.622-.041,.715,.479,.384,.485-.223,.822-.414,.489-.25,2.275,.502,1.96-.631Z" fill="#3b8288"></path>
          <path d="M14.624,17.264s.004,.003,.012,.007c-.007-.004-.011-.007-.012-.007h0Z" fill="#a27037"></path>
          <path d="M18.215,13.019c.002-.497-3.62-1.554-2.526,.068-.258,.037-.691-.15-.712-.352,0,0,0,0,0,0,0,0,0,0,0,0,.015,.04-.11,.248-.151,.267-.006-.1-.03-.192-.03-.192v.004c-.125-.31-.028,.433-.249,.37,.076-.029,.006-.364-.052-.32,.037,.024-.047,.41-.121,.427,.045-.065-.042-.324-.062-.272,0,0,0,0,0,0,.063,.263-.45,.571-.376,.701-.336,.119-.481,.946,.12,.757-.256-.134-.135-.469,.172-.434-.014-.003,.043,.021,.027,.032,.079,.371,.485-.072,.645-.128-.169,.942-.602,1.836,.288,2.773-.295-.311-.349,.054-.016,.163-.201,.01-.431,.205-.085,.313-.071,.072-.345-.137-.195,.009-.003-.001-.006-.003-.009-.004,0,0,.002,.002,.006,.005-.572-.025-.025,.2,.214,.222-.194,.305,.482,.023,.548,.016,0,0,0,0,0,0,.133,.335,.238,.032,.208-.217,.095,.109,.19,.217,.287,.324h0s0,0,0,0h0c.152,.041,.318,.718,.432,.365,.004-.014,.006-.028,.008-.042,.226,.254,.334,.35,.235-.053,.123,.202,.233,.26,.201-.004,.186,.195,.137-.07,.118-.206,.179,.711,1.985,.561,1.799,.083-.312-.304-2.294-1.415-1.782-2.109,.194,.099,1.156,1.304,.738,.599-.371-.965,.316,0,.418,.358,.23,.415-.128-.724-.204-.764,.635,.793,.576,1.491,.375,.027,.025,.048,.066,.086,.116,.105-.037-.074-.08-.103-.104-.114,.039,.009,.087,.068,.107,.115-.001,0-.002,0-.003-.001,.339,1.803,.462,1.494,.249-.132,.512,2.02,.44,2.008,.384-.037,.367,.526,.103,1.624,.26,2.125,.274-.584,.176-2.301,.355-2.761-.337-.32-1.113-2.012-1.631-2.085Zm-2.889,4.239s0-.001,0-.002h.002s-.001,.001-.002,.002Z" fill="#a27037"></path>
          <path d="M14.715,16.587c.079-.641-.499-.553-.914-.554-.811-.68,1.523-1.254,.432-1.993h.004s-.008-.002-.007-.002l.007,.002s-.023-.023-.022-.023c-.094,.015-.235,.019-.282,.136,0,0,.003,.002,.006,.005l-.126,.148c0,.006,.21,.147,.201,.157,.008-.002,.019,.009,.025,.013,.11,.347-.585,.486-.724,.802-.445,.914,.373,1.211,1.023,1.217-.875,.946-.794,.138-1.382-.416,.083-.354,.237-.801-.251-.948,.003-.079-.13-.161-.165-.041,.033-.034-.086-.136-.135-.069-.19-.243-.413,.369-.078,.307,.008,.075,.133,.04,.152,.023-.003,.095,.142,.085,.161,.025,.33,.191-.146,.548,.001,.847,.195,.36,.548,.505,.559,.978,.29,.474,1.476-.153,1.506-.487,.005-.039,.007-.081,.01-.123h0Zm-.254-1.951s.004,.004,.005,.005h0s-.004-.003-.006-.005h0Zm-.572,.62s0,0,0,0c0,0,0,0,0,0h0Z" fill="#a9ac78"></path>
          <path d="M13.746,13.936c.005,.021-.459,.125-.392-.081,.088,.028,.498-.271,.332-.237-.458,.313-.307-.073-.156-.339,.045,.015,.052,.236,.028,.25,.133-.089,.077-.573-.109-.321-.182-.073-.67,.401-.397,.595-.096,.419,.233,.596,.585,.507l.002-.006h.031c-.052-.007,.077-.344,.076-.367Z" fill="#a9ac78"></path>
        </svg>
      ),
      french: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <path fill="#fff" d="M10 4H22V28H10z"></path>
          <path d="M5,4h6V28H5c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" fill="#092050"></path>
          <path d="M25,4h6V28h-6c-2.208,0-4-1.792-4-4V8c0-2.208,1.792-4,4-4Z" transform="rotate(180 26 16)" fill="#be2a2c"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      vietnamese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#c93728"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
          <path fill="#ff5" d="M18.008 16.366L21.257 14.006 17.241 14.006 16 10.186 14.759 14.006 10.743 14.006 13.992 16.366 12.751 20.186 16 17.825 19.249 20.186 18.008 16.366z"></path>
        </svg>
      ),
      japanese: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <circle cx="16" cy="16" r="6" fill="#ae232f"></circle>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      indian: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <path fill="#fff" d="M1 11H31V21H1z"></path>
          <path d="M5,4H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" fill="#e06535"></path>
          <path d="M5,20H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" transform="rotate(180 16 24)" fill="#2c6837"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M16,12.292c-2.048,0-3.708,1.66-3.708,3.708s1.66,3.708,3.708,3.708,3.708-1.66,3.708-3.708-1.66-3.708-3.708-3.708Zm3.041,4.109c-.01,.076,.042,.145,.117,.157-.033,.186-.08,.367-.143,.54-.071-.028-.152,.006-.181,.077-.029,.071,.004,.151,.073,.182-.04,.085-.083,.167-.13,.248l-1.611-1.069-.592-.249c.013-.026,.024-.053,.034-.081l.595,.242,1.895,.383-1.833-.616-.636-.087c.006-.028,.009-.057,.011-.087l.638,.08,1.93-.12-1.93-.12-.638,.08c-.002-.03-.005-.059-.011-.087l.636-.087,1.833-.616-1.895,.383-.595,.242c-.009-.028-.021-.055-.034-.081l.592-.249,1.611-1.069c.047,.081,.09,.163,.13,.248-.07,.031-.103,.111-.073,.182,.029,.071,.11,.105,.181,.077,.063,.173,.111,.354,.143,.54-.075,.012-.127,.081-.117,.157,.01,.076,.078,.129,.154,.121,.008,.092,.013,.185,.013,.279s-.005,.187-.013,.279c-.075-.008-.144,.045-.154,.121Zm-.584-2.462c-.059,.048-.07,.134-.023,.194,.046,.06,.132,.072,.194,.028,.053,.076,.104,.155,.15,.236l-1.731,.861-.512,.388c-.016-.024-.034-.047-.054-.069l.508-.394,1.28-1.45-1.45,1.28-.394,.508c-.022-.019-.045-.038-.069-.054l.388-.512,.861-1.731c.081,.047,.16,.097,.236,.15-.045,.061-.033,.147,.028,.194,.061,.046,.147,.036,.194-.023,.071,.06,.141,.123,.207,.189,.066,.066,.129,.135,.189,.207Zm-2.177-1.133c-.008,.075,.045,.144,.121,.154,.076,.01,.145-.042,.157-.117,.186,.033,.367,.08,.54,.143-.028,.071,.006,.152,.077,.181,.071,.029,.151-.004,.182-.073,.085,.04,.167,.083,.248,.13l-1.069,1.611-.249,.592c-.026-.013-.053-.024-.081-.034l.242-.595,.383-1.895-.616,1.833-.087,.636c-.028-.006-.057-.009-.087-.011l.08-.638-.12-1.93-.12,1.93,.08,.638c-.03,.002-.059,.005-.087,.011l-.087-.636-.616-1.833,.383,1.895,.242,.595c-.028,.009-.055,.021-.081,.034l-.249-.592-1.069-1.611c.081-.047,.163-.09,.248-.13,.031,.07,.111,.103,.182,.073,.071-.029,.105-.11,.077-.181,.173-.063,.354-.111,.54-.143,.012,.075,.081,.127,.157,.117,.076-.01,.129-.078,.121-.154,.092-.008,.185-.013,.279-.013s.187,.005,.279,.013Zm-3.113,4.368c-.029-.071-.11-.105-.181-.077-.063-.173-.111-.354-.143-.54,.075-.012,.127-.081,.117-.157-.01-.076-.078-.129-.154-.121-.008-.092-.013-.185-.013-.279s.005-.187,.013-.279c.075,.008,.144-.045,.154-.121,.01-.076-.042-.145-.117-.157,.033-.186,.08-.367,.143-.54,.071,.028,.152-.006,.181-.077,.029-.071-.004-.151-.073-.182,.04-.085,.083-.167,.13-.248l1.611,1.069,.592,.249c-.013,.026-.024,.053-.034,.081l-.595-.242-1.895-.383,1.833,.616,.636,.087c-.006,.028-.009,.057-.011,.087l-.638-.08-1.93,.12,1.93,.12,.638-.08c.002,.03,.005,.059,.011,.087l-.636,.087-1.833,.616,1.895-.383,.595-.242c.009,.028,.021,.055,.034,.081l-.592,.249-1.611,1.069c-.047-.081-.09-.163-.13-.248,.07-.031,.103-.111,.073-.182Zm.772-3.63c.048,.059,.134,.07,.194,.023,.06-.046,.072-.132,.028-.194,.076-.053,.155-.104,.236-.15l.861,1.731,.388,.512c-.024,.016-.047,.034-.069,.054l-.394-.508-1.45-1.28,1.28,1.45,.508,.394c-.019,.022-.038,.045-.054,.069l-.512-.388-1.731-.861c.047-.081,.097-.16,.15-.236,.061,.045,.147,.033,.194-.028,.046-.061,.036-.147-.023-.194,.06-.071,.123-.141,.189-.207s.135-.129,.207-.189Zm-.395,4.518c.059-.048,.07-.134,.023-.194-.046-.06-.132-.072-.194-.028-.053-.076-.104-.155-.15-.236l1.731-.861,.512-.388c.016,.024,.034,.047,.054,.069l-.508,.394-1.28,1.45,1.45-1.28,.394-.508c.022,.019,.045,.038,.069,.054l-.388,.512-.861,1.731c-.081-.047-.16-.097-.236-.15,.045-.061,.033-.147-.028-.194-.061-.046-.147-.036-.194,.023-.071-.06-.141-.123-.207-.189-.066-.066-.129-.135-.189-.207Zm2.177,1.133c.008-.075-.045-.144-.121-.154-.076-.01-.145,.042-.157,.117-.186-.033-.367-.08-.54-.143,.028-.071-.006-.152-.077-.181-.071-.029-.151,.004-.182,.073-.085-.04-.167-.083-.248-.13l1.069-1.611,.249-.592c.026,.013,.053,.024,.081,.034l-.242,.595-.383,1.895,.616-1.833,.087-.636c.028,.006,.057,.009,.087,.011l-.08,.638,.12,1.93,.12-1.93-.08-.638c.03-.002,.059-.005,.087-.011l.087,.636,.616,1.833-.383-1.895-.242-.595c.028-.009,.055-.021,.081-.034l.249,.592,1.069,1.611c-.081,.047-.163,.09-.248,.13-.031-.07-.111-.103-.182-.073-.071,.029-.105,.11-.077,.181-.173,.063-.354,.111-.54,.143-.012-.075-.081-.127-.157-.117-.076,.01-.129,.078-.121,.154-.092,.008-.185,.013-.279,.013s-.187-.005-.279-.013Zm2.341-.738c-.048-.059-.134-.07-.194-.023-.06,.046-.072,.132-.028,.194-.076,.053-.155,.104-.236,.15l-.861-1.731-.388-.512c.024-.016,.047-.034,.069-.054l.394,.508,1.45,1.28-1.28-1.45-.508-.394c.019-.022,.038-.045,.054-.069l.512,.388,1.731,.861c-.047,.081-.097,.16-.15,.236-.061-.045-.147-.033-.194,.028-.046,.061-.036,.147,.023,.194-.06,.071-.123,.141-.189,.207s-.135,.129-.207,.189Z" fill="#2c2c6b"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      mediterranean: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#0066cc"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M16,10c-3.314,0-6,2.686-6,6s2.686,6,6,6,6-2.686,6-6-2.686-6-6-6Zm0,10c-2.209,0-4-1.791-4-4s1.791-4,4-4,4,1.791,4,4-1.791,4-4,4Z" fill="#fff"></path>
        </svg>
      ),
      european: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#003399"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <circle cx="16" cy="16" r="5" fill="#ffcc00"></circle>
        </svg>
      ),
      korean: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path transform="rotate(-56.31 8.143 10.762)" d="M5.877 10.384H10.41V11.139000000000001H5.877z"></path>
          <path transform="rotate(-56.31 9.086 11.39)" d="M6.819 11.013H11.352V11.768H6.819z"></path>
          <path transform="rotate(-56.31 10.028 12.02)" d="M7.762 11.641H12.295V12.396H7.762z"></path>
          <path transform="rotate(-56.31 24.538 20.216)" d="M23.499 19.839H25.576V20.593999999999998H23.499z"></path>
          <path transform="rotate(-56.31 23.176 22.26)" d="M22.137 21.882H24.215V22.637H22.137z"></path>
          <path transform="rotate(-56.31 23.595 19.588)" d="M22.556 19.21H24.633000000000003V19.965H22.556z"></path>
          <path transform="rotate(-56.31 22.234 21.632)" d="M21.195 21.253H23.272V22.008H21.195z"></path>
          <path transform="rotate(-56.31 22.653 18.96)" d="M21.614 18.582H23.691000000000003V19.337H21.614z"></path>
          <path transform="rotate(-56.31 21.29 21.002)" d="M20.252 20.625H22.329V21.38H20.252z"></path>
          <path d="M12.229,13.486c1.389-2.083,4.203-2.646,6.286-1.257s2.646,4.203,1.257,6.286l-7.543-5.029Z" fill="#be3b3e"></path>
          <path d="M12.229,13.486c-1.389,2.083-.826,4.897,1.257,6.286s4.897,.826,6.286-1.257c.694-1.041,.413-2.449-.629-3.143s-2.449-.413-3.143,.629l-3.771-2.514Z" fill="#1c449c"></path>
          <circle cx="14.114" cy="14.743" r="2.266" fill="#be3b3e"></circle>
          <path transform="rotate(-33.69 8.143 21.238)" d="M7.765 18.972H8.52V23.505000000000003H7.765z"></path>
          <path transform="rotate(-33.69 10.03 19.98)" d="M9.651 17.715H10.406V22.248H9.651z"></path>
          <path transform="rotate(-33.69 22.915 11.39)" d="M22.537 9.124H23.291999999999998V13.657H22.537z"></path>
          <path transform="rotate(-33.69 8.405 19.588)" d="M8.027 18.549H8.782V20.625999999999998H8.027z"></path>
          <path transform="rotate(-33.691 9.767 21.632)" d="M9.389 20.592H10.144V22.668999999999997H9.389z"></path>
          <path transform="rotate(-33.69 21.29 10.998)" d="M20.913 9.959H21.668V12.036H20.913z"></path>
          <path transform="rotate(-33.69 22.652 13.04)" d="M22.275 12.002H23.029999999999998V14.079H22.275z"></path>
          <path transform="rotate(-33.69 23.176 9.741)" d="M22.798 8.702H23.552999999999997V10.779H22.798z"></path>
          <path transform="rotate(-33.691 24.539 11.783)" d="M24.16 10.745H24.915V12.822H24.16z"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      british: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#fff"></rect>
          <path fill="#be2a2a" d="M31 14L18 14 18 4 14 4 14 14 1 14 1 18 14 18 14 28 18 28 18 18 31 18 31 14z"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      thai: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <path fill="#282646" d="M1 11H31V21H1z"></path>
          <path d="M5,4H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" fill="#992532"></path>
          <path d="M5,20H27c2.208,0,4,1.792,4,4v4H1v-4c0-2.208,1.792-4,4-4Z" transform="rotate(180 16 24)" fill="#992532"></path>
          <path fill="#fff" d="M1 9H31V12H1z"></path>
          <path fill="#fff" d="M1 20H31V23H1z"></path>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M27,5H5c-1.657,0-3,1.343-3,3v1c0-1.657,1.343-3,3-3H27c1.657,0,3,1.343,3,3v-1c0-1.657-1.343-3-3-3Z" fill="#fff" opacity=".2"></path>
        </svg>
      ),
      caribbean: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#0066cc"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M16,10c-3.314,0-6,2.686-6,6s2.686,6,6,6,6-2.686,6-6-2.686-6-6-6Zm0,10c-2.209,0-4-1.791-4-4s1.791-4,4-4,4,1.791,4,4-1.791,4-4,4Z" fill="#ffcc00"></path>
        </svg>
      ),
      no_preference: (
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
          <rect x="1" y="4" width="30" height="24" rx="4" ry="4" fill="#e0e0e0"></rect>
          <path d="M27,4H5c-2.209,0-4,1.791-4,4V24c0,2.209,1.791,4,4,4H27c2.209,0,4-1.791,4-4V8c0-2.209-1.791-4-4-4Zm3,20c0,1.654-1.346,3-3,3H5c-1.654,0-3-1.346-3-3V8c0-1.654,1.346-3,3-3H27c1.654,0,3,1.346,3,3V24Z" opacity=".15"></path>
          <path d="M11,16h10M16,11v10" stroke="#999" strokeWidth="2" strokeLinecap="round"></path>
        </svg>
      )
    };
    return flags[cuisineId] || flags.no_preference;
  };

  // Data constants
  const cuisines = [
    { id: 'american', name: 'American' },
    { id: 'chinese', name: 'Chinese' },
    { id: 'italian', name: 'Italian' },
    { id: 'mexican', name: 'Mexican' },
    { id: 'french', name: 'French' },
    { id: 'vietnamese', name: 'Vietnamese' },
    { id: 'japanese', name: 'Japanese' },
    { id: 'indian', name: 'Indian' },
    // { id: 'mediterranean', name: 'Mediterranean' }, khu vực
    // { id: 'european', name: 'European' },
    { id: 'korean', name: 'Korean' },
    { id: 'british', name: 'British' },
    { id: 'thai', name: 'Thai' },
    // { id: 'caribbean', name: 'Caribbean' },
    { id: 'no_preference', name: 'No Preference' }
  ];

  const mealTypes = [
    { id: 'main_dishes', name: '🍽️ Main Dishes', description: 'Entrees, main courses ' },
    { id: 'appetizers', name: '🍤 Appetizers', description: 'Starters, finger foods ' },
    { id: 'desserts', name: '🎂 Desserts', description: 'Cakes, sweets, pastries ' },
    { id: 'beverages', name: '🍹 Beverages', description: 'Drinks, smoothies, cocktails' },
    { id: 'side_dishes', name: '🥗 Side Dishes', description: 'Sides, salads' },
    { id: 'breakfast', name: '☕ Breakfast', description: 'Breakfast items ' },
    { id: 'snacks', name: '🍪 Snacks', description: 'Light snacks' }
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
      id: 'age',
      title: 'Age', 
      description: 'How old are you?',
      subtitle: 'This helps us personalize recommendations'
    },
    { 
      id: 'gender',
      title: 'Gender', 
      description: 'What is your gender?',
      subtitle: 'This helps us personalize recommendations'
    },
    { 
      id: 'dietary_mode',
      title: 'Dietary Mode', 
      description: 'What is your dietary preference?',
      subtitle: 'Optional - select your diet type or BMI-based plan'
    },
    { 
      id: 'cuisines',
      title: 'Favorite Cuisines', 
      description: 'Which country\'s cuisine do you prefer?',
      subtitle: 'Select up to 3 countries'
    },
    { 
      id: 'meals',
      title: 'Meal Types', 
      description: 'What type of dish would you like?',
      subtitle: 'Select the category that fits your needs'
    },
    { 
      id: 'time',
      title: 'Cooking Time', 
      description: 'How much time do you have for cooking?',
      subtitle: 'Choose the appropriate time range'
    }
  ];

  const genderOptions = [
    { id: 'male', name: 'Male' },
    { id: 'female', name: 'Female' },
    { id: 'other', name: 'Other' },
    { id: 'prefer_not_to_say', name: 'Prefer not to say' }
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

  // Handlers
  const handleAddAllergy = (ingredientId: string) => {
    // Use functional update to ensure we have the latest state
    setSelectedAllergies(prev => {
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
    setSelectedAllergies(prev => prev.filter(id => id !== ingredientId));
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
    setPreferences(prev => {
      // If "No Preference" is selected
      if (cuisineId === 'no_preference') {
        // If already selected, deselect it
        if (prev.favoriteCuisines.includes('no_preference')) {
          return {
            ...prev,
            favoriteCuisines: []
          };
        }
        // Otherwise, select only "No Preference" and clear others
        return {
          ...prev,
          favoriteCuisines: ['no_preference']
        };
      }
      
      // If "No Preference" is already selected, remove it and select the clicked cuisine
      if (prev.favoriteCuisines.includes('no_preference')) {
        return {
          ...prev,
          favoriteCuisines: [cuisineId]
        };
      }
      
      // Toggle the selected cuisine
      if (prev.favoriteCuisines.includes(cuisineId)) {
        return {
          ...prev,
          favoriteCuisines: prev.favoriteCuisines.filter(id => id !== cuisineId)
        };
      } else {
        // Add cuisine if under limit (3)
        return {
          ...prev,
          favoriteCuisines: prev.favoriteCuisines.length < 3 ? [...prev.favoriteCuisines, cuisineId] : prev.favoriteCuisines
        };
      }
    });
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
      // Get userId from context or storage (for guest users who might not have user object in context yet)
      let currentUserId = user?.user_id || getUserId();
      
      // If still no userId, try to create a guest user
      if (!currentUserId) {
        console.log('🔄 No userId found, creating guest user...');
        try {
          const createResponse = await apiService.createUser();
          if (createResponse.data) {
            currentUserId = createResponse.data.user_id;
            const isGuest = !localStorage.getItem('access_token');
            setUserId(currentUserId, isGuest);
            setUser(createResponse.data);
            console.log('✅ Created new guest user:', currentUserId);
          } else {
            throw new Error(createResponse.error || 'Failed to create guest user');
          }
        } catch (err) {
          console.error('❌ Failed to create guest user:', err);
          throw new Error('Failed to initialize user. Please try again.');
        }
      }

      // Ensure user object is in context (load if needed)
      if (!user?.user_id || user.user_id !== currentUserId) {
        console.log('🔄 Loading user profile into context...');
        const success = await loadUserProfile(currentUserId);
        if (!success) {
          // For guest users, create a minimal user object if load fails
          const hasAccessToken = !!localStorage.getItem('access_token');
          if (!hasAccessToken) {
            const tempUser = {
              user_id: currentUserId,
              username: undefined,
              name: undefined,
              age: undefined,
              age_group: undefined,
              gender: undefined,
              locale: 'vi-VN',
              skill_level: 'beginner',
              max_cook_time: 60,
              meal_preferences: [],
              completed_onboarding: false,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString()
            } as any;
            setUser(tempUser);
            console.log('✅ Created temporary user object for guest');
          } else {
            throw new Error('Failed to load user profile');
          }
        }
      }

      const maxCookTime = cookingTimeOptions.find(
        option => option.id === preferences.cookingTimePreference
      )?.minutes;

      // Get meal type name from preferences
      const selectedMealType = preferences.preferredMealTypes[0];
      // Map meal type ID to backend meal type value
      const mealTypeMapping: { [key: string]: string } = {
        'main_dishes': 'Main Dishes',
        'appetizers': 'Appetizers',
        'desserts': 'Desserts',
        'beverages': 'Beverages',
        'side_dishes': 'Side Dishes',
        'breakfast': 'Breakfast',
        'snacks': 'Snacks'
      };
      const mealTypeName = mealTypeMapping[selectedMealType] || selectedMealType;
      
      // Check if user is guest
      const hasAccessToken = !!localStorage.getItem('access_token');
      const hasUsername = user?.username;
      const isGuest = !hasAccessToken || !hasUsername;
      
      // Check if this is a temporary guest user (not in database yet)
      const isTemporaryGuest = isGuest && currentUserId?.startsWith('guest_');
      
      // If temporary guest, create user in database first
      if (isTemporaryGuest) {
        try {
          console.log('🔄 Creating guest user in database...');
          const createResponse = await apiService.createUser();
          if (createResponse.data) {
            // Update userId in storage and context
            currentUserId = createResponse.data.user_id;
            const isGuest = !localStorage.getItem('access_token');
            setUserId(currentUserId, isGuest);
            setUser(createResponse.data);
            console.log('✅ Guest user created in database:', currentUserId);
          } else {
            throw new Error(createResponse.error || 'Failed to create guest user in database');
          }
        } catch (err) {
          console.error('❌ Failed to create guest user in database:', err);
          throw new Error('Failed to create guest account. Please try again.');
        }
      }
      
      const profileUpdate: any = {
        locale: 'vi-VN',
        skill_level: 'intermediate',
        max_cook_time: maxCookTime,
        meal_preferences: mealTypeName ? [mealTypeName] : [],  // Store meal type in meal_preferences
        completed_onboarding: true  // Mark onboarding as completed in database
      };
      
      // Add age, age_group and gender for guest users
      if (isGuest && ageGroup) {
        // Find age group option to get average age
        const selectedAgeGroup = ageGroupOptions.find(ag => ag.id === ageGroup);
        if (selectedAgeGroup) {
          // Use average age for the age_group range
          profileUpdate.age = Math.round(selectedAgeGroup.avgAge);
          // age_group will be auto-calculated by backend from age, but we can also set it explicitly
          // Note: Backend will calculate age_group from age, so we don't need to set it separately
        }
      }
      if (isGuest && gender) {
        profileUpdate.gender = gender;
      }

      // Add dietary mode information
      if (dietaryMode && dietaryMode !== 'none') {
        if (dietaryMode === 'bmi_based') {
          // BMI-based: calculate BMI and determine dietary_plan automatically
          if (bmiHeight && bmiWeight) {
            const heightCm = parseFloat(bmiHeight);
            const weightKg = parseFloat(bmiWeight);
            
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
              if (bmiActivityLevel) {
                profileUpdate.activity_level = bmiActivityLevel;
              }
              
              // Only set dietary_plan if BMI is outside normal range
              if (bmiBasedPlan) {
                profileUpdate.dietary_plan = bmiBasedPlan;
                console.log(`✅ BMI-based plan: BMI=${calculatedBMI.toFixed(1)} → ${bmiBasedPlan}`);
              } else {
                console.log(`✅ BMI-based plan: BMI=${calculatedBMI.toFixed(1)} → Balanced (no filter)`);
              }
            }
          }
        } else {
          // Other dietary modes: set dietary_plan directly
          // Valid values: "low_carb", "high_protein", "low_fat", "keto"
          profileUpdate.dietary_plan = dietaryMode;
          profileUpdate.auto_dietary_plan = false;
        }
      }

      await updateUserProfile(currentUserId, profileUpdate);

      const hasExistingAllergies = allergies?.allergies && allergies.allergies.length > 0;
      if (selectedAllergies.length > 0 && !hasExistingAllergies) {
        await apiService.addUserAllergies(currentUserId, { ingredient_ids: selectedAllergies });
      }

      const hasExistingCuisines = favoriteCuisines?.favorite_cuisines && favoriteCuisines.favorite_cuisines.length > 0;
      // Only add cuisines if "No Preference" is not selected
      if (preferences.favoriteCuisines.length > 0 && 
          !preferences.favoriteCuisines.includes('no_preference') && 
          !hasExistingCuisines) {
        for (const cuisineId of preferences.favoriteCuisines) {
          const cuisineName = cuisines.find(c => c.id === cuisineId)?.name;
          if (cuisineName) {
            await apiService.addUserFavoriteCuisine(currentUserId, {
              cuisine_name: cuisineName,
              preference_level: 5
            });
          }
        }
      }
      // If "No Preference" is selected, we don't add any cuisines (returns None/null)
      
      await loadUserAllergies(currentUserId);
      await loadUserFavoriteCuisines(currentUserId);
      
      // Reload user profile to get updated completed_onboarding status (for both registered and guest users)
      await loadUserProfile(currentUserId);

      // Ensure userId is saved (important for guest users)
      if (currentUserId) {
        const isGuest = !localStorage.getItem('access_token');
        setUserId(currentUserId, isGuest);
        console.log('✅ Saved userId:', currentUserId, isGuest ? '(sessionStorage)' : '(localStorage)');
      }
      
      // Set guestCompletedOnboarding flag for guest users (to prevent redirect back to onboarding)
      if (isGuest) {
        localStorage.setItem('guestCompletedOnboarding', 'true');
      }

      // Save completion status (for registered users only)
      if (!isGuest) {
        // Registered users: save to userPreferences
        const finalPreferences = {
          ...preferences,
          completedOnboarding: true
        };
        localStorage.setItem('userPreferences', JSON.stringify(finalPreferences));
      }
      // Guest users: completed_onboarding is already saved in database via updateUserProfile
      
      navigate('/suggestions');
    } catch (err) {
      console.error('Failed to save user preferences:', err);
      
      // Get userId from context or storage (for guest users who might not have user object in context yet)
      let currentUserId = user?.user_id || getUserId();
      
      // Check if user is guest
      // Guest = no access token OR (has user object but no username)
      const hasAccessToken = !!localStorage.getItem('access_token');
      const hasUsername = !!user?.username;
      const isGuest = !hasAccessToken || !hasUsername;
      
      // Ensure userId is saved (important for guest users)
      if (currentUserId) {
        const isGuestUser = currentUserId.startsWith('guest_') || isGuest;
        setUserId(currentUserId, isGuestUser);
        console.log('✅ Saved userId (catch block):', currentUserId, isGuestUser ? '(sessionStorage)' : '(localStorage)');
        
        // Set guestCompletedOnboarding flag for guest users (to prevent redirect back to onboarding)
        if (isGuestUser) {
          localStorage.setItem('guestCompletedOnboarding', 'true');
        }
      }
      
      // Save completion status (for registered users only)
      if (!isGuest && currentUserId) {
        // Registered users: save to userPreferences
        const finalPreferences = {
          ...preferences,
          completedOnboarding: true
        };
        localStorage.setItem('userPreferences', JSON.stringify(finalPreferences));
      }
      // Guest users: completed_onboarding is already saved in database via updateUserProfile
      
      navigate('/suggestions');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSubmit = () => {
    // Check if user is guest
    const hasAccessToken = !!localStorage.getItem('access_token');
    const hasUsername = !!user?.username;
    const isGuest = !hasAccessToken || (user && !hasUsername);
    
    // Validate BMI form if BMI-based is selected
    if (dietaryMode === 'bmi_based') {
      const height = parseFloat(bmiHeight);
      const weight = parseFloat(bmiWeight);
      if (!bmiHeight || !bmiWeight || height <= 0 || weight <= 0 || height < 50 || height > 300 || weight < 1 || weight > 500) {
        return false;
      }
    }
    
    // For guest users: require age group, gender, meal type, and cooking time
    if (isGuest && !hasCompletedOnboardingBefore) {
      return ageGroup !== '' &&
             gender !== '' &&
             preferences.preferredMealTypes.length > 0 && 
             preferences.cookingTimePreference !== '';
    }
    
    // For registered users or returning guests: only check meal type and cooking time
    return preferences.preferredMealTypes.length > 0 && 
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

          {/* Age Section - Only for guest users */}
          {!hasCompletedOnboardingBefore && isGuest && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>{sections[0].title}</h2>
              </div>
              <div className="allergy-layout-container">
                <div className="allergy-left-content">
                  <p className="section-description">{sections[0].description}</p>
                  <span className="section-subtitle">{sections[0].subtitle}</span>
                </div>
                <div className="meal-type-dropdown-wrapper">
                  <div className="custom-dropdown" ref={ageGroupDropdownRef}>
                    <div 
                      className="custom-dropdown-select"
                      onClick={() => setIsAgeGroupDropdownOpen(!isAgeGroupDropdownOpen)}
                    >
                      <span className={`custom-dropdown-value ${!ageGroup ? 'placeholder' : ''}`}>
                        {ageGroup 
                          ? ageGroupOptions.find(a => a.id === ageGroup)?.name || 'Select age group...'
                          : 'Select age group...'}
                      </span>
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                        <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    </div>
                    {isAgeGroupDropdownOpen && (
                      <div className="custom-dropdown-list">
                        {ageGroupOptions.map(option => (
                          <div
                            key={option.id}
                            className={`custom-dropdown-item ${ageGroup === option.id ? 'selected' : ''}`}
                            onClick={() => {
                              setAgeGroup(option.id);
                              setIsAgeGroupDropdownOpen(false);
                            }}
                          >
                            {option.name}
                            {ageGroup === option.id && (
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
          )}

          {/* Gender Section - Only for guest users */}
          {!hasCompletedOnboardingBefore && isGuest && (
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
                  <div className="custom-dropdown" ref={genderDropdownRef}>
                    <div 
                      className="custom-dropdown-select"
                      onClick={() => setIsGenderDropdownOpen(!isGenderDropdownOpen)}
                    >
                      <span className={`custom-dropdown-value ${!gender ? 'placeholder' : ''}`}>
                        {gender 
                          ? genderOptions.find(g => g.id === gender)?.name || 'Select gender...'
                          : 'Select gender...'}
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
                            className={`custom-dropdown-item ${gender === option.id ? 'selected' : ''}`}
                            onClick={() => {
                              setGender(option.id);
                              setIsGenderDropdownOpen(false);
                            }}
                          >
                            {option.name}
                            {gender === option.id && (
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
          )}

          {/* Ingredient Allergies Section */}
          {/* Show if user hasn't completed onboarding before (guest or first-time login) */}
          {!hasCompletedOnboardingBefore && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>Ingredient Allergies</h2>
              </div>
              <div className="allergy-layout-container">
                <div className="allergy-left-content">
                  <p className="section-description">What are your ingredient allergies?</p>
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
                  {ingredientSearch && (filteredIngredients.length > 0 || canAddNewIngredient || isSearching) && (
                    <div className="allergy-dropdown">
                      {isSearching && (
                        <div className="allergy-dropdown-item" style={{ textAlign: 'center', color: '#666' }}>
                          Searching...
                        </div>
                      )}
                      {!isSearching && filteredIngredients.slice(0, 10).map((ingredient: AvailableIngredient) => {
                        // Only show checkmark if ingredient is actually in selectedAllergies
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
                        const ingredient = availableIngredients.find(ing => ing.id === ingredientId)
                          || searchResults.find(ing => ing.id === ingredientId);
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

          {/* Dietary Mode Section */}
          {/* Show if user hasn't completed onboarding before (guest or first-time login) */}
          {!hasCompletedOnboardingBefore && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>{sections[2].title}</h2>
              </div>
              <div className="allergy-layout-container">
              <div className="allergy-left-content">
                <p className="section-description">{sections[2].description}</p>
                <span className="section-subtitle">{sections[2].subtitle}</span>
                </div>
                <div className="meal-type-dropdown-wrapper">
                  <div className="custom-dropdown" ref={dietaryModeDropdownRef}>
                    <div 
                      className="custom-dropdown-select"
                      onClick={() => setIsDietaryModeDropdownOpen(!isDietaryModeDropdownOpen)}
                    >
                      <span className={`custom-dropdown-value ${!dietaryMode ? 'placeholder' : ''}`}>
                        {dietaryMode 
                          ? dietaryModeOptions.find(d => d.id === dietaryMode)?.name || 'Select dietary mode...'
                          : 'Select dietary mode...'}
                      </span>
                      <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                        <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    </div>
                    {isDietaryModeDropdownOpen && (
                      <div className="custom-dropdown-list">
                        {dietaryModeOptions.map(option => (
                          <div
                            key={option.id}
                            className={`custom-dropdown-item ${dietaryMode === option.id ? 'selected' : ''}`}
                            onClick={() => {
                              setDietaryMode(option.id);
                              setIsDietaryModeDropdownOpen(false);
                              // Reset BMI fields if not BMI-based
                              if (option.id !== 'bmi_based') {
                                setBmiHeight('');
                                setBmiWeight('');
                                setBmiActivityLevel('');
                              }
                            }}
                            style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                              <span style={{ fontWeight: '500' }}>{option.name}</span>
                              {dietaryMode === option.id && (
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                  <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                                </svg>
                              )}
                            </div>
                            {option.description && (
                              <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                                {option.description}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
              
              {/* BMI Form - Show when BMI-based is selected */}
              {dietaryMode === 'bmi_based' && (
                <div className="bmi-form-container" style={{ marginTop: '24px', padding: '20px', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
                  <h3 style={{ marginBottom: '16px', fontSize: '18px', fontWeight: '600' }}>BMI Information</h3>
                  <p style={{ marginBottom: '16px', fontSize: '14px', color: '#666' }}>
                    We'll automatically determine your dietary plan based on your BMI:
                    <br />• BMI &lt; 18.5: Weight Gain (High-Protein + High-Calorie)
                    <br />• BMI 18.5-24.9: Balanced Diet (No restrictions)
                    <br />• BMI &gt; 24.9: Weight Loss (Low-Carb + High-Protein + Low-Fat)
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                        Height (cm) *
                      </label>
                      <input
                        type="number"
                        min="50"
                        max="300"
                        value={bmiHeight}
                        onChange={(e) => setBmiHeight(e.target.value)}
                        placeholder="Enter your height in cm"
                        style={{
                          width: '100%',
                          padding: '10px',
                          border: '1px solid #ddd',
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                        Weight (kg) *
                      </label>
                      <input
                        type="number"
                        min="1"
                        max="500"
                        value={bmiWeight}
                        onChange={(e) => setBmiWeight(e.target.value)}
                        placeholder="Enter your weight in kg"
                        style={{
                          width: '100%',
                          padding: '10px',
                          border: '1px solid #ddd',
                          borderRadius: '6px',
                          fontSize: '14px'
                        }}
                      />
                    </div>
                    {/* Display calculated BMI and dietary plan */}
                    {bmiHeight && bmiWeight && parseFloat(bmiHeight) > 0 && parseFloat(bmiWeight) > 0 && (
                      <div style={{ 
                        padding: '12px', 
                        backgroundColor: '#e8f5e9', 
                        borderRadius: '6px',
                        border: '1px solid #4caf50'
                      }}>
                        {(() => {
                          const heightCm = parseFloat(bmiHeight);
                          const weightKg = parseFloat(bmiWeight);
                          const heightM = heightCm / 100.0;
                          const calculatedBMI = weightKg / (heightM * heightM);
                          let bmiStatus = '';
                          let planName = '';
                          let planColor = '#4caf50';
                          
                          if (calculatedBMI < 18.5) {
                            bmiStatus = 'Underweight';
                            planName = 'Weight Gain Plan';
                            planColor = '#ff9800';
                          } else if (calculatedBMI > 24.9) {
                            bmiStatus = 'Overweight';
                            planName = 'Weight Loss Plan';
                            planColor = '#f44336';
                          } else {
                            bmiStatus = 'Normal';
                            planName = 'Balanced Diet';
                            planColor = '#4caf50';
                          }
                          
                          return (
                            <div>
                              <div style={{ fontSize: '16px', fontWeight: '600', marginBottom: '8px' }}>
                                BMI: <span style={{ color: planColor }}>{calculatedBMI.toFixed(1)}</span> ({bmiStatus})
                              </div>
                              <div style={{ fontSize: '14px', color: '#666' }}>
                                Recommended: <strong style={{ color: planColor }}>{planName}</strong>
                              </div>
                            </div>
                          );
                        })()}
                      </div>
                    )}
                    <div>
                      <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', fontWeight: '500' }}>
                        Activity Level
                      </label>
                      <div className="custom-dropdown" ref={activityLevelDropdownRef}>
                        <div 
                          className="custom-dropdown-select"
                          onClick={() => setIsActivityLevelDropdownOpen(!isActivityLevelDropdownOpen)}
                        >
                          <span className={`custom-dropdown-value ${!bmiActivityLevel ? 'placeholder' : ''}`}>
                            {bmiActivityLevel 
                              ? activityLevelOptions.find(a => a.id === bmiActivityLevel)?.name || 'Select activity level...'
                              : 'Select activity level...'}
                          </span>
                          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                            <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                          </svg>
                        </div>
                        {isActivityLevelDropdownOpen && (
                          <div className="custom-dropdown-list">
                            {activityLevelOptions.map(option => (
                              <div
                                key={option.id}
                                className={`custom-dropdown-item ${bmiActivityLevel === option.id ? 'selected' : ''}`}
                                onClick={() => {
                                  setBmiActivityLevel(option.id);
                                  setIsActivityLevelDropdownOpen(false);
                                }}
                              >
                                {option.name}
                                {bmiActivityLevel === option.id && (
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
              )}
            </div>
          )}

          {/* Favorite Cuisines Section */}
          {/* Show if user hasn't completed onboarding before (guest or first-time login) */}
          {!hasCompletedOnboardingBefore && (
            <div className="onboarding-section">
              <div className="section-header">
                <h2>{sections[3].title}</h2>
              </div>
              <div className="allergy-left-content">
                <p className="section-description">{sections[3].description}</p>
                <span className="section-subtitle">{sections[3].subtitle}</span>
              </div>
              <div className="options-grid-cuisine">
                {cuisines.map(cuisine => (
                  <div
                    key={cuisine.id}
                    className={`option-card ${preferences.favoriteCuisines.includes(cuisine.id) ? 'selected' : ''}`}
                    onClick={() => handleCuisineToggle(cuisine.id)}
                  >
                    <div className="cuisine-flag">
                      {getCuisineFlag(cuisine.id)}
                    </div>
                    <h3>{cuisine.name}</h3>
                    {preferences.favoriteCuisines.includes(cuisine.id) && (
                      <div className="selected-indicator">✓</div>
                    )}
                  </div>
                ))}
              </div>
              <p className="selection-counter">
                {preferences.favoriteCuisines.includes('no_preference') 
                  ? 'No Preference selected' 
                  : `Selected ${preferences.favoriteCuisines.length}/3 countries`}
              </p>
            </div>
          )}

          {/* Meal Types Section */}
          <div className="onboarding-section">
            <div className="section-header">
              <h2>{sections[4].title}</h2>
            </div>
            <div className="allergy-layout-container">
              <div className="allergy-left-content">
                <p className="section-description">{sections[4].description}</p>
                <span className="section-subtitle">{sections[4].subtitle}</span>
              </div>
              <div className="meal-type-dropdown-wrapper">
                <div className="custom-dropdown" ref={mealTypeDropdownRef}>
                  <div 
                    className="custom-dropdown-select"
                    onClick={() => setIsMealTypeDropdownOpen(!isMealTypeDropdownOpen)}
                  >
                    <span className={`custom-dropdown-value ${!preferences.preferredMealTypes[0] ? 'placeholder' : ''}`}>
                      {preferences.preferredMealTypes[0] 
                        ? mealTypes.find(m => m.id === preferences.preferredMealTypes[0])?.name || 'Select dish category...'
                        : 'Select dish category...'}
                    </span>
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" className="custom-dropdown-arrow">
                      <path d="M2 4L6 8L10 4" stroke="#9e9e9e" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
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
                          style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}
                        >
                          <div style={{ display: 'flex', justifyContent: 'space-between', width: '100%', alignItems: 'center' }}>
                            <span style={{ fontWeight: '500' }}>{mealType.name}</span>
                            {preferences.preferredMealTypes[0] === mealType.id && (
                              <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                              </svg>
                            )}
                          </div>
                          {mealType.description && (
                            <span style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                              {mealType.description}
                            </span>
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
              <h2>{sections[5].title}</h2>
            </div>
            <div className="allergy-layout-container">
              <div className="allergy-left-content">
                <p className="section-description">{sections[5].description}</p>
                <span className="section-subtitle">{sections[5].subtitle}</span>
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
