import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import {
  UserProfile,
  UserAllergiesResponse,
  UserDislikesResponse,
  UserCuisinesResponse,
} from "../types/api";
import { apiService } from "../services/api";

interface UserContextType {
  user: UserProfile | null;
  allergies: UserAllergiesResponse | null;
  dislikes: UserDislikesResponse | null;
  favoriteCuisines: UserCuisinesResponse | null;
  isLoading: boolean;
  error: string | null;
  setUser: (user: UserProfile | null) => void;
  loadUserProfile: (userId: string) => Promise<boolean>;
  updateUserProfile: (userId: string, updates: Partial<UserProfile>) => Promise<void>;
  loadUserAllergies: (userId: string) => Promise<void>;
  loadUserDislikes: (userId: string) => Promise<void>;
  loadUserFavoriteCuisines: (userId: string) => Promise<void>;
  initializeUser: () => Promise<void>;
  clearError: () => void;
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
        localStorage.setItem("userId", response.data.user_id);
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
        // No token - this is a guest user, auto-create is allowed
        console.warn("⚠️ Guest user not found in DB, auto-creating...");
        try {
          const created = await apiService.createUser();
          if (created.data) {
            setUser(created.data);
            localStorage.setItem("userId", created.data.user_id);
            return true;
          } else {
            console.error("Failed to create user:", created.error);
            setError(created.error || "Failed to create new user");
            return false;
          }
        } catch (createErr) {
          console.error("Error creating user:", createErr);
          setError("Failed to create new user. Please try again.");
          return false;
        }
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
        // Only update if cuisines array length changed or if cuisines doesn't exist
        if (!favoriteCuisines || favoriteCuisines.favorite_cuisines?.length !== res.data.favorite_cuisines?.length) {
          setFavoriteCuisines(res.data);
        }
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

  // =====================
  // 🔹 Initialize user
  // =====================
  const initializeUser = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const savedUserId = localStorage.getItem("userId");
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
          localStorage.removeItem("userId");
          setUser(null);
          console.warn("Token expired or invalid — clearing authentication.");
        }
      }

      // Don't auto-create guest user on initialization
      // Guest user will be created only when user clicks "Continue as Guest"
      // This prevents unnecessary API calls on every page load
      console.log("No authenticated user found. User can sign in or continue as guest.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Initialization failed");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    initializeUser();
  }, []);

  const value: UserContextType = {
    user,
    allergies,
    dislikes,
    favoriteCuisines,
    isLoading,
    error,
    setUser,
    loadUserProfile,
    updateUserProfile,
    loadUserAllergies,
    loadUserDislikes,
    loadUserFavoriteCuisines,
    initializeUser,
    clearError,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};
