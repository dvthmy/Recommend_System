import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import {
  UserProfile,
  UserAllergiesResponse,
  UserDislikesResponse,
  UserCuisinesResponse,
  UserDietsResponse,
} from "../types/api";
import { apiService } from "../services/api";
import { getUserId, setUserId, removeUserId, isNewSession, clearGuestSession, getOrCreateSessionId } from "../utils/auth";

interface UserContextType {
  user: UserProfile | null;
  allergies: UserAllergiesResponse | null;
  dislikes: UserDislikesResponse | null;
  favoriteCuisines: UserCuisinesResponse | null;
  diets: UserDietsResponse | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: UserProfile | null) => void;
  loadUserProfile: (userId: string) => Promise<boolean>;
  updateUserProfile: (userId: string, updates: Partial<UserProfile>) => Promise<void>;
  loadUserAllergies: (userId: string) => Promise<void>;
  loadUserDislikes: (userId: string) => Promise<void>;
  loadUserFavoriteCuisines: (userId: string) => Promise<void>;
  loadUserDiets: (userId: string) => Promise<void>;
  initializeUser: () => Promise<void>;
  clearError: () => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const ctx = useContext(UserContext);
  if (!ctx) throw new Error("useUser must be used within a UserProvider");
  return ctx;
};

interface Props {
  children: ReactNode;
}

export const UserProvider: React.FC<Props> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [allergies, setAllergies] = useState<UserAllergiesResponse | null>(null);
  const [dislikes, setDislikes] = useState<UserDislikesResponse | null>(null);
  const [favoriteCuisines, setFavoriteCuisines] = useState<UserCuisinesResponse | null>(null);
  const [diets, setDiets] = useState<UserDietsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  // =====================
  // 🔹 Load user profile
  // =====================
  const loadUserProfile = async (userId: string): Promise<boolean> => {
    // Prevent duplicate calls if already loading
    if (isLoading) {
      return false;
    }
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiService.getUserProfile(userId);

        if (response.data) {
          // Always update user data to ensure latest changes are reflected
          setUser(response.data);
          // Check if this is a guest user (no token) or authenticated user
          const isGuest = !localStorage.getItem("access_token");
          setUserId(response.data.user_id, isGuest);
          return true;
      } else {
        throw new Error(response.error || "User not found");
      }
    } catch (err) {
      // Check if user is authenticated (has token)
      const hasToken = localStorage.getItem("access_token");
      
      if (hasToken) {
        // User is authenticated but profile not found - this is an error
        // Clear invalid session
        console.error("⚠️ Authenticated user not found in DB. Clearing session.");
        localStorage.removeItem("access_token");
        localStorage.removeItem("userId");
        setUser(null);
        setError("User session expired. Please sign in again.");
        return false;
      } else {
        // No token - this could be a guest user, but don't auto-create
        // Guest user should only be created when user explicitly clicks "Continue as Guest"
        // Return false so caller knows user doesn't exist yet
        console.log("⚠️ User not found and no token - user needs to sign in or continue as guest");
        setUser(null);
        localStorage.removeItem("userId"); // Clear invalid userId
        return false;
      }
    } finally {
      setIsLoading(false);
    }
  };

  // =====================
  // 🔹 Update user
  // =====================
  const updateUserProfile = async (userId: string, updates: Partial<UserProfile>) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiService.updateUserProfile(userId, updates);
      if (response.data) {
        setUser(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update user profile");
    } finally {
      setIsLoading(false);
    }
  };

  // =====================
  // 🔹 Load preferences
  // =====================
  const loadUserAllergies = async (userId: string) => {
    try {
      const res = await apiService.getUserAllergies(userId);
      if (res.data) {
        // Only update if allergies array length changed or if allergies doesn't exist
        if (!allergies || allergies.allergies?.length !== res.data.allergies?.length) {
          setAllergies(res.data);
        }
      }
    } catch (err) {
      console.error("Failed to load allergies:", err);
    }
  };

  const loadUserDislikes = async (userId: string) => {
    try {
      const res = await apiService.getUserDislikes(userId);
      if (res.data) setDislikes(res.data);
    } catch (err) {
      console.error("Failed to load dislikes:", err);
    }
  };

  const loadUserFavoriteCuisines = async (userId: string) => {
    try {
      const res = await apiService.getUserFavoriteCuisines(userId);
      if (res.data) {
        // Always update favorite cuisines to ensure UI reflects latest changes
        // (previously we only updated when length changed, which broke edits that
        //  swapped cuisines with the same count)
        setFavoriteCuisines(res.data);
      } else if (res.error) {
        // If API returns error (e.g., 404), set to null so onboarding shows the section
        setFavoriteCuisines(null);
      }
    } catch (err) {
      console.error("Failed to load cuisines:", err);
      // If error occurs, set to null so onboarding shows the section
      setFavoriteCuisines(null);
    }
  };

  const loadUserDiets = async (userId: string) => {
    try {
      const res = await apiService.getUserDiets(userId);
      if (res.data) {
        // Only update if diets array length changed or if it doesn't exist
        if (!diets || diets.diets?.length !== res.data.diets?.length) {
          setDiets(res.data);
        }
      } else if (res.error) {
        // If API returns error (e.g., 404), set to null so onboarding shows the section
        setDiets(null);
      }
    } catch (err) {
      console.error("Failed to load diets:", err);
      // If error occurs, set to null so onboarding shows the section
      setDiets(null);
    }
  };

  // =====================
  // 🔹 Initialize user
  // =====================
  const initializeUser = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Clean up deprecated/unused localStorage keys on app initialization
      // These keys may have been created in older versions or manually in DevTools
      localStorage.removeItem('registeredUsernames'); // Deprecated - no longer used
      localStorage.removeItem('homeFormData'); // Deprecated - no longer used
      localStorage.removeItem('authToken'); // Deprecated - use 'access_token' instead
      localStorage.removeItem('foodRatings'); // Deprecated - ratings stored in backend, not localStorage
      localStorage.removeItem('userData'); // Deprecated - user data stored in state/backend, not localStorage
      localStorage.removeItem('isGuest'); // Deprecated - isGuest is calculated, not stored (computed from access_token)
      
      const savedUserId = getUserId(); // Get from localStorage or sessionStorage
      const savedToken = localStorage.getItem("access_token");

      // If we have both userId and token, verify token first
      if (savedUserId && savedToken) {
        // Verify token is still valid
        const verifyRes = await apiService.verifyToken();
        
        if (verifyRes.data?.valid) {
          // Token is valid, load user profile using loadUserProfile
          // This will handle errors properly (won't auto-create if authenticated)
          const success = await loadUserProfile(savedUserId);
          if (success) {
            return;
          }
        } else {
          // Token is invalid or expired, try to refresh
          try {
            const refreshRes = await apiService.refreshToken();
            if (refreshRes.data?.access_token) {
              // Token refreshed successfully, save new token and load profile
              localStorage.setItem("access_token", refreshRes.data.access_token);
              const success = await loadUserProfile(savedUserId);
              if (success) {
                return;
              }
            }
          } catch (refreshError) {
            // Refresh failed, clear tokens
            console.warn("Token refresh failed:", refreshError);
          }
          
          // If refresh failed or profile load failed, clear tokens
          localStorage.removeItem("access_token");
          removeUserId(); // Clear both localStorage and sessionStorage
          setUser(null);
          console.warn("Token expired or invalid — clearing authentication.");
        }
      }

      // For guest users, create a temporary user object in sessionStorage only (not in database)
      // Check if we already have a guest userId (no token but has userId)
      if (savedUserId && !savedToken) {
        // Check if this is a guest user (user_id starts with "guest_")
        const isGuest = savedUserId?.startsWith('guest_') ?? false;
        
        if (isGuest) {
          // Check if this is a new session (new tab or reopened browser)
          // sessionStorage is automatically cleared when tab closes, so isNewSession will return true
          if (isNewSession()) {
            // New session - clear old guest data and create new guest
            console.log("🔄 New session detected - clearing old guest user and creating new one");
            clearGuestSession();
            // Continue to create new guest user below
          } else {
            // Same session - try to load existing guest user from database
            const success = await loadUserProfile(savedUserId);
            if (success) {
              console.log("✅ Loaded existing guest user from database");
              return;
            } else {
              // Guest user doesn't exist in database, create temporary one from sessionStorage
              const tempGuestUser: UserProfile = {
                user_id: savedUserId,
                username: undefined,
                name: undefined,
                age: undefined,
                age_group: undefined,
                gender: undefined,
                locale: "vi-VN",
                skill_level: "beginner",
                max_cook_time: 60,
                meal_preferences: [],
                completed_onboarding: false,
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString()
              };
              setUser(tempGuestUser);
              console.log("✅ Loaded temporary guest user from sessionStorage (same session):", savedUserId);
              return;
            }
          }
        } else {
          // This is an authenticated user that doesn't exist - shouldn't happen, but handle it
          removeUserId();
        }
      }

      // No user found OR new session - create temporary guest user in sessionStorage only (not in database)
      // This will be automatically cleared when tab/browser closes
      const tempUserId = `guest_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      const tempGuestUser: UserProfile = {
        user_id: tempUserId,
        username: undefined,
        name: undefined,
        age: undefined,
        age_group: undefined,
        gender: undefined,
        locale: "vi-VN",
        skill_level: "beginner",
        max_cook_time: 60,
        meal_preferences: [],
        completed_onboarding: false,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setUser(tempGuestUser);
      setUserId(tempUserId, true); // Store in sessionStorage for guest users
      // Ensure session ID is created for this session
      getOrCreateSessionId();
      console.log("✅ Created temporary guest user in sessionStorage (will be cleared when tab closes):", tempUserId);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Initialization failed");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    initializeUser();
  }, []);

  // =====================
  // 🔹 Logout
  // =====================
  const logout = () => {
    // Clear all localStorage and sessionStorage data
    localStorage.removeItem('access_token');
    removeUserId(); // Clear both localStorage and sessionStorage
    clearGuestSession(); // Clear guest session data
    localStorage.removeItem('userPreferences');
    localStorage.removeItem('uploadedIngredients');
    localStorage.removeItem('likedRecipes');
    
    // Clean up deprecated/unused localStorage keys
    // These keys may have been created in older versions or manually in DevTools
    localStorage.removeItem('registeredUsernames'); // Deprecated - no longer used
    localStorage.removeItem('homeFormData'); // Deprecated - no longer used
    localStorage.removeItem('authToken'); // Deprecated - use 'access_token' instead
    localStorage.removeItem('foodRatings'); // Deprecated - ratings stored in backend, not localStorage
    localStorage.removeItem('userData'); // Deprecated - user data stored in state/backend, not localStorage
    localStorage.removeItem('isGuest'); // Deprecated - isGuest is calculated, not stored (computed from access_token)
    
    // Clear all state
    setUser(null);
    setAllergies(null);
    setDislikes(null);
    setFavoriteCuisines(null);
    setDiets(null);
    setError(null);
    
    console.log('User logged out successfully');
  };

  const value: UserContextType = {
    user,
    allergies,
    dislikes,
    favoriteCuisines,
    diets,
    isLoading,
    error,
    setUser,
    loadUserProfile,
    updateUserProfile,
    loadUserAllergies,
    loadUserDislikes,
    loadUserFavoriteCuisines,
    loadUserDiets,
    initializeUser,
    clearError,
    logout,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
