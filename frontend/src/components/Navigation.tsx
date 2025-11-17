import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import './Navigation.css';

interface NavigationProps {
  isLoggedIn?: boolean;
}

const Navigation: React.FC<NavigationProps> = ({ isLoggedIn: propIsLoggedIn }: NavigationProps) => {
  const location = useLocation();
  const { user } = useUser();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // Determine if user is logged in: 
  // - Authenticated user: has username AND access_token
  // - Guest user: has user_id but no username or token
  // Check token directly in render - will update when component re-renders (e.g., when user context changes)
  const hasToken = !!localStorage.getItem('access_token');
  const isAuthenticated = !!(user?.username && hasToken);
  const isLoggedIn = propIsLoggedIn !== undefined ? propIsLoggedIn : isAuthenticated;

  const navigationItems = [
    { path: '/', label: 'Home' },
    { path: '/onboarding', label: 'Onboarding' },
    { path: '/suggestions', label: 'Suggestions' },
    { path: '/history', label: 'History' },
  ];

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true;
    if (path !== '/' && location.pathname.startsWith(path)) return true;
    return false;
  };

  return (
    <nav className="navigation">
      <div className="container">
        <div className="nav-content">
          {/* Logo */}
          <Link to="/" className="nav-logo">
            <span className="logo-text">FoodAI</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="nav-menu desktop-only">
            {navigationItems.map((item) => {
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                >
                  <span className="nav-label">{item.label}</span>
                </Link>
              );
            })}
          </div>

          {/* User Menu */}
          <div className="nav-user">
            {isLoggedIn ? (
              <div className="user-menu">
                <Link to="/profile" className="user-avatar">
                  {user?.username || 'Profile'}
                </Link>
              </div>
            ) : (
              <div className="auth-buttons">
                <Link to="/signin" className="btn btn-outline btn-sm">
                  Sign In
                </Link>
                <Link to="/signup" className="btn btn-primary btn-sm">
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button
            className="mobile-menu-toggle"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMobileMenuOpen ? 'Close' : 'Menu'}
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className={`nav-menu mobile ${isMobileMenuOpen ? 'open' : ''}`}>
          {navigationItems.map((item) => {
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive(item.path) ? 'active' : ''}`}
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <span className="nav-label">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
