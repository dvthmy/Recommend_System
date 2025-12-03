import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import { setUserId } from '../utils/auth';
import './Auth.css';

const Auth: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser, loadUserProfile } = useUser();
  const [activeTab, setActiveTab] = useState<'signup' | 'signin'>('signup');

  // Set active tab based on URL
  useEffect(() => {
    if (location.pathname === '/signin' || location.pathname === '/auth') {
      setActiveTab('signin');
    } else {
      setActiveTab('signup');
    }
  }, [location.pathname]);
  
  // Sign Up form data
  const [signUpData, setSignUpData] = useState({
    name: '',
    username: '',
    password: '',
    age: '',
    gender: ''
  });
  
  // Sign In form data
  const [signInData, setSignInData] = useState({
    username: '',
    password: ''
  });
  
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<{[key: string]: string}>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGenderDropdownOpen, setIsGenderDropdownOpen] = useState(false);
  const genderDropdownRef = useRef<HTMLDivElement>(null);
  const [showSignUpPassword, setShowSignUpPassword] = useState(false);
  const [showSignInPassword, setShowSignInPassword] = useState(false);
  
  const genderOptions = [
    { id: 'male', name: 'Male' },
    { id: 'female', name: 'Female' },
    { id: 'other', name: 'Other' }
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (genderDropdownRef.current && !genderDropdownRef.current.contains(event.target as Node)) {
        setIsGenderDropdownOpen(false);
      }
    };

    if (isGenderDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isGenderDropdownOpen]);

  // Sign Up handlers
  const handleSignUpChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setSignUpData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    setError(null);
  };

  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const newFieldErrors: {[key: string]: string} = {};

    // Validate required fields
    if (!signUpData.username) {
      newFieldErrors.username = 'Please enter your username';
    } else if (signUpData.username.length < 8) {
      newFieldErrors.username = 'Username must be at least 8 characters';
    }
    if (!signUpData.password) {
      newFieldErrors.password = 'Please enter your password';
    }
    if (!signUpData.age) {
      newFieldErrors.age = 'Please enter your age';
    } else {
      const age = parseInt(signUpData.age);
      if (isNaN(age) || age < 1 || age > 150) {
        newFieldErrors.age = 'Please enter a valid age (1-150)';
      }
    }
    if (!signUpData.gender) {
      newFieldErrors.gender = 'Please select a gender';
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      setIsSubmitting(false);
      return;
    }

    setIsSubmitting(true);

    try {
      const age = parseInt(signUpData.age);

      const response = await apiService.signUp({
        username: signUpData.username,
        name: signUpData.name || undefined,
        password: signUpData.password,
        age: age,
        gender: signUpData.gender
      });

      if (response.data) {
        setUser(response.data);
        localStorage.setItem('userId', response.data.user_id);
        // Store JWT token
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
        }
        navigate('/onboarding');
      } else {
        // Check if error is about username already exists
        const errorMessage = response.error || 'Sign up failed';
        if (errorMessage.toLowerCase().includes('username already exists') || 
            errorMessage.toLowerCase().includes('username') && errorMessage.toLowerCase().includes('already')) {
          setFieldErrors({ username: 'This username is already taken. Please choose another one.' });
        } else {
          setError(errorMessage);
        }
      }
    } catch (err: any) {
      // Check if error is about username already exists
      const errorMessage = err instanceof Error ? err.message : 'An error occurred';
      if (errorMessage.toLowerCase().includes('username already exists') || 
          (errorMessage.toLowerCase().includes('username') && errorMessage.toLowerCase().includes('already'))) {
        setFieldErrors({ username: 'This username is already taken. Please choose another one.' });
      } else {
        setError(errorMessage);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  // Sign In handlers
  const handleSignInChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSignInData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear field error when user starts typing
    if (fieldErrors[name]) {
      setFieldErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
    setError(null);
  };

  const handleSignInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    const newFieldErrors: {[key: string]: string} = {};

    // Validate required fields
    if (!signInData.username) {
      newFieldErrors.username = 'Please enter your username';
    }
    if (!signInData.password) {
      newFieldErrors.password = 'Please enter your password';
    }

    if (Object.keys(newFieldErrors).length > 0) {
      setFieldErrors(newFieldErrors);
      setIsSubmitting(false);
      return;
    }

    setIsSubmitting(true);

    try {

      const response = await apiService.signIn({
        username: signInData.username,
        password: signInData.password
      });

      if (response.data) {
        setUser(response.data);
        // Store JWT token
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
        }
        // Store userId (authenticated user - use localStorage)
        setUserId(response.data.user_id, false);
        // Load full user profile from database to get completed_onboarding and other fields
        await loadUserProfile(response.data.user_id);
        navigate('/');
      } else {
        setError(response.error || 'Sign in failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Continue as Guest
  const handleContinueAsGuest = async () => {
    setIsSubmitting(true);
    setError(null);
    
    try {
      const response = await apiService.createUser();
      if (response.data) {
        setUser(response.data);
        // Store userId (guest user - use sessionStorage)
        setUserId(response.data.user_id, true);
        navigate('/onboarding');
      } else {
        setError(response.error || 'Failed to create guest account. Please make sure the backend server is running.');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create guest account';
      setError(errorMessage.includes('fetch') || errorMessage.includes('Network') 
        ? 'Cannot connect to server. Please make sure the backend is running on http://localhost:8000'
        : errorMessage);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        {/* Tabs */}
        <div className="auth-tabs">
          <button
            className={`auth-tab ${activeTab === 'signup' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('signup');
              setError(null);
              setFieldErrors({});
            }}
          >
            Sign Up
          </button>
          <button
            className={`auth-tab ${activeTab === 'signin' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('signin');
              setError(null);
              setFieldErrors({});
            }}
          >
            Sign In
          </button>
        </div>

        {/* Sign Up Form */}
        {activeTab === 'signup' && (
          <div className="auth-form-container">
            <div className="auth-header">
              <h1>Sign Up</h1>
              <p>Create an account for a better experience</p>
            </div>

            <form onSubmit={handleSignUpSubmit} className="auth-form" noValidate>
              <div className="form-group">
                <label htmlFor="name">Full Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={signUpData.name}
                  onChange={handleSignUpChange}
                  placeholder="Enter your full name"
                />
              </div>

              <div className="form-group">
                <label htmlFor="username">Username</label>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={signUpData.username}
                  onChange={handleSignUpChange}
                  placeholder="Enter username"
                  className={fieldErrors.username ? 'error' : ''}
                />
                {fieldErrors.username && (
                  <span className="field-error">{fieldErrors.username}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showSignUpPassword ? "text" : "password"}
                    id="password"
                    name="password"
                    value={signUpData.password}
                    onChange={handleSignUpChange}
                    placeholder="Enter password"
                    className={fieldErrors.password ? 'error' : ''}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowSignUpPassword(!showSignUpPassword)}
                    aria-label={showSignUpPassword ? "Hide password" : "Show password"}
                  >
                    {showSignUpPassword ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        <line x1="1" y1="1" x2="23" y2="23" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        <circle cx="12" cy="12" r="3" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    )}
                  </button>
                </div>
                {fieldErrors.password && (
                  <span className="field-error">{fieldErrors.password}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="age">Age</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={signUpData.age}
                  onChange={handleSignUpChange}
                  placeholder="Enter your age"
                  min="1"
                  max="150"
                  className={fieldErrors.age ? 'error' : ''}
                />
                {fieldErrors.age && (
                  <span className="field-error">{fieldErrors.age}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="gender">Gender</label>
                <div className="custom-dropdown" ref={genderDropdownRef}>
                  <div 
                    className={`custom-dropdown-select ${fieldErrors.gender ? 'error' : ''}`}
                    onClick={() => setIsGenderDropdownOpen(!isGenderDropdownOpen)}
                  >
                    <span className={`custom-dropdown-value ${!signUpData.gender ? 'placeholder' : ''}`}>
                      {signUpData.gender 
                        ? genderOptions.find(g => g.id === signUpData.gender)?.name || 'Select gender'
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
                          className={`custom-dropdown-item ${signUpData.gender === option.id ? 'selected' : ''}`}
                          onClick={() => {
                            setSignUpData(prev => ({ ...prev, gender: option.id }));
                            setIsGenderDropdownOpen(false);
                            // Clear gender error when selected
                            if (fieldErrors.gender) {
                              setFieldErrors(prev => {
                                const newErrors = { ...prev };
                                delete newErrors.gender;
                                return newErrors;
                              });
                            }
                          }}
                        >
                          {option.name}
                          {signUpData.gender === option.id && (
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                              <path d="M13.3334 4L6.00002 11.3333L2.66669 8" stroke="#4caf50" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                            </svg>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                {fieldErrors.gender && (
                  <span className="field-error">{fieldErrors.gender}</span>
                )}
              </div>

              {error && (
                <div className="error-message">
                  <p>{error}</p>
                </div>
              )}

              <button 
                type="submit" 
                className="btn btn-primary btn-block"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing up...' : 'Sign Up'}
              </button>
            </form>

            <div className="auth-divider">
              <span>OR</span>
            </div>

            <button 
              onClick={handleContinueAsGuest}
              className="btn btn-outline btn-block"
            >
              Continue as Guest
            </button>
          </div>
        )}

        {/* Sign In Form */}
        {activeTab === 'signin' && (
          <div className="auth-form-container">
            <div className="auth-header">
              <h1>Sign In</h1>
              <p>Welcome back!</p>
            </div>

            <form onSubmit={handleSignInSubmit} className="auth-form" noValidate>
              <div className="form-group">
                <label htmlFor="signin-username">Username</label>
                <input
                  type="text"
                  id="signin-username"
                  name="username"
                  value={signInData.username}
                  onChange={handleSignInChange}
                  placeholder="Enter username"
                  className={fieldErrors.username ? 'error' : ''}
                />
                {fieldErrors.username && (
                  <span className="field-error">{fieldErrors.username}</span>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="signin-password">Password</label>
                <div className="password-input-wrapper">
                  <input
                    type={showSignInPassword ? "text" : "password"}
                    id="signin-password"
                    name="password"
                    value={signInData.password}
                    onChange={handleSignInChange}
                    placeholder="Enter password"
                    className={fieldErrors.password ? 'error' : ''}
                  />
                  <button
                    type="button"
                    className="password-toggle"
                    onClick={() => setShowSignInPassword(!showSignInPassword)}
                    aria-label={showSignInPassword ? "Hide password" : "Show password"}
                  >
                    {showSignInPassword ? (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        <line x1="1" y1="1" x2="23" y2="23" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    ) : (
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                        <circle cx="12" cy="12" r="3" stroke="#999" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                      </svg>
                    )}
                  </button>
                </div>
                {fieldErrors.password && (
                  <span className="field-error">{fieldErrors.password}</span>
                )}
              </div>

              {error && (
                <div className="error-message">
                  <p>{error}</p>
                </div>
              )}

              <button 
                type="submit" 
                className="btn btn-primary btn-block"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Signing in...' : 'Sign In'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};

export default Auth;

