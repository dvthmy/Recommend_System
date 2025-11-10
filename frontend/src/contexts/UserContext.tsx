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
  loadUserProfile: (userId: string) => Promise<void>;
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
  const loadUserProfile = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await apiService.getUserProfile(userId);

      if (response.data) {
        setUser(response.data);
        localStorage.setItem("userId", response.data.user_id);
      } else {
        throw new Error(response.error || "User not found");
      }
    } catch (err) {
      console.warn("⚠️ User not found in DB, auto-creating...");
      // if backend auto-create works, retry
      const created = await apiService.createUser();
      if (created.data) {
        setUser(created.data);
        localStorage.setItem("userId", created.data.user_id);
      } else {
        setError("Failed to create new user");
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
      if (res.data) setAllergies(res.data);
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
      if (res.data) setFavoriteCuisines(res.data);
    } catch (err) {
      console.error("Failed to load cuisines:", err);
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

      if (savedUserId) {
        // attempt to load existing
        const profileRes = await apiService.getUserProfile(savedUserId);

        if (profileRes.data) {
          setUser(profileRes.data);
          return;
        } else {
          console.warn("User not found — backend may have been reset.");
        }
      }

      // if missing or not found → create new
      const created = await apiService.createUser();
      if (created.data) {
        setUser(created.data);
        localStorage.setItem("userId", created.data.user_id);
      } else {
        setError("Failed to create user");
      }
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
