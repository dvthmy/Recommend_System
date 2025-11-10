import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import './Navigation.css';

interface NavigationProps {
  isLoggedIn?: boolean;
}

const Navigation: React.FC<NavigationProps> = ({ isLoggedIn = false }) => {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const navigationItems = [
    { path: '/', label: 'Home' },
    { path: '/upload', label: 'Upload' },
    { path: '/suggestions', label: 'Suggestions' },
    { path: '/foods', label: 'Foods' },
    { path: '/ingredients', label: 'Ingredients' },
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
                  Profile
                </Link>
              </div>
            ) : (
              <Link to="/onboarding" className="btn btn-primary btn-sm">
                Get Started
              </Link>
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
