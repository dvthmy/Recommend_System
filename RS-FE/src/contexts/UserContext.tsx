import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { UserProfile, UserAllergiesResponse, UserDislikesResponse, UserCuisinesResponse } from '../types/api';
import { apiService } from '../services/api';

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
  createNewUser: () => Promise<void>;
  clearError: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

interface UserProviderProps {
  children: ReactNode;
}

export const UserProvider: React.FC<UserProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [allergies, setAllergies] = useState<UserAllergiesResponse | null>(null);
  const [dislikes, setDislikes] = useState<UserDislikesResponse | null>(null);
  const [favoriteCuisines, setFavoriteCuisines] = useState<UserCuisinesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  const loadUserProfile = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getUserProfile(userId);
      if (response.data) {
        setUser(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load user profile');
    } finally {
      setIsLoading(false);
    }
  };

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
      setError(err instanceof Error ? err.message : 'Failed to update user profile');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserAllergies = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getUserAllergies(userId);
      if (response.data) {
        setAllergies(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load user allergies');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserDislikes = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getUserDislikes(userId);
      if (response.data) {
        setDislikes(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load user dislikes');
    } finally {
      setIsLoading(false);
    }
  };

  const loadUserFavoriteCuisines = async (userId: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getUserFavoriteCuisines(userId);
      if (response.data) {
        setFavoriteCuisines(response.data);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load favorite cuisines');
    } finally {
      setIsLoading(false);
    }
  };

  const initializeUser = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Check if user exists in localStorage
      const savedUserId = localStorage.getItem('userId');
      
      if (savedUserId) {
        // Try to load existing user profile
        try {
          await loadUserProfile(savedUserId);
          return;
        } catch (err) {
          console.log('Failed to load existing user, creating new one');
          // If user doesn't exist in database, create new one
        }
      }
      
      // Create new user
      await createNewUser();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initialize user');
    } finally {
      setIsLoading(false);
    }
  };

  const createNewUser = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await apiService.createUser();
      if (response.data) {
        setUser(response.data);
        // Save user ID to localStorage
        localStorage.setItem('userId', response.data.user_id);
      } else if (response.error) {
        setError(response.error);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create user');
    } finally {
      setIsLoading(false);
    }
  };

  // Load user data from localStorage on mount
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
    createNewUser,
    clearError,
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};
