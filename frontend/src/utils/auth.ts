/**
 * Authentication utility functions
 */

export const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const setToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('userId');
  sessionStorage.removeItem('guestUserId'); // Also clear guest userId
};

export const isAuthenticated = (): boolean => {
  return !!getToken();
};

// Helper functions for userId management
// Authenticated users: userId in localStorage (persists across sessions)
// Guest users: userId in sessionStorage (cleared when tab/browser closes)
export const getUserId = (): string | null => {
  // First check localStorage (for authenticated users)
  const localUserId = localStorage.getItem('userId');
  if (localUserId) {
    return localUserId;
  }
  // Then check sessionStorage (for guest users)
  return sessionStorage.getItem('guestUserId');
};

export const setUserId = (userId: string, isGuest: boolean = false): void => {
  if (isGuest) {
    // Guest users: store in sessionStorage (will be cleared when tab closes)
    sessionStorage.setItem('guestUserId', userId);
    // Also keep in localStorage temporarily for backward compatibility during migration
    // But we'll check sessionStorage first
  } else {
    // Authenticated users: store in localStorage (persists across sessions)
    localStorage.setItem('userId', userId);
    // Clear guest userId if exists
    sessionStorage.removeItem('guestUserId');
  }
};

export const removeUserId = (): void => {
  localStorage.removeItem('userId');
  sessionStorage.removeItem('guestUserId');
  // Note: Don't clear appSessionId here - it should persist for the tab session
};

// Helper to check if a userId belongs to a guest user
// Guest user IDs always start with "guest_"
export const isGuestUserId = (userId: string | null | undefined): boolean => {
  return userId ? userId.startsWith('guest_') : false;
};

// Session management for guest users
// Each new tab/browser session gets a new session ID
// When tab closes and reopens, sessionStorage is cleared, so new session ID will be created
export const getOrCreateSessionId = (): string => {
  let sessionId = sessionStorage.getItem('appSessionId');
  if (!sessionId) {
    // Create new session ID for this tab
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('appSessionId', sessionId);
  }
  return sessionId;
};

export const isNewSession = (): boolean => {
  const savedGuestUserId = sessionStorage.getItem('guestUserId');
  const savedSessionId = sessionStorage.getItem('appSessionId');
  
  // If no guest userId exists, it's definitely a new session
  if (!savedGuestUserId) {
    return true;
  }
  
  // If no session ID exists, it's a new session (tab was closed and reopened)
  if (!savedSessionId) {
    return true;
  }
  
  // Get current session ID (will create new one if doesn't exist)
  const currentSessionId = getOrCreateSessionId();
  
  // If session IDs don't match, it's a new session
  // This shouldn't normally happen, but could if sessionStorage was partially cleared
  return currentSessionId !== savedSessionId;
};

export const clearGuestSession = (): void => {
  sessionStorage.removeItem('guestUserId');
  // Note: Don't clear appSessionId here - it identifies the current session
};

