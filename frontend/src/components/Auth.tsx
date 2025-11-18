import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import { apiService } from '../services/api';
import './Auth.css';

const Auth: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { setUser } = useUser();
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
    confirmPassword: '',
    age: '',
    gender: ''
  });
  
  // Sign In form data
  const [signInData, setSignInData] = useState({
    username: '',
    password: ''
  });
  
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Sign Up handlers
  const handleSignUpChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setSignUpData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
  };

  const handleSignUpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (!signUpData.username || !signUpData.password || !signUpData.confirmPassword || !signUpData.age || !signUpData.gender) {
        setError('Please fill in all required fields');
        setIsSubmitting(false);
        return;
      }

      if (signUpData.password !== signUpData.confirmPassword) {
        setError('Passwords do not match');
        setIsSubmitting(false);
        return;
      }

      const age = parseInt(signUpData.age);
      if (isNaN(age) || age < 1 || age > 150) {
        setError('Invalid age');
        setIsSubmitting(false);
        return;
      }

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
        setError(response.error || 'Sign up failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
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
    setError(null);
  };

  const handleSignInSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      if (!signInData.username || !signInData.password) {
        setError('Please fill in all required fields');
        setIsSubmitting(false);
        return;
      }

      const response = await apiService.signIn({
        username: signInData.username,
        password: signInData.password
      });

      if (response.data) {
        setUser(response.data);
        localStorage.setItem('userId', response.data.user_id);
        // Store JWT token
        if (response.data.access_token) {
          localStorage.setItem('access_token', response.data.access_token);
        }
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
        localStorage.setItem('userId', response.data.user_id);
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
            }}
          >
            Sign Up
          </button>
          <button
            className={`auth-tab ${activeTab === 'signin' ? 'active' : ''}`}
            onClick={() => {
              setActiveTab('signin');
              setError(null);
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

            <form onSubmit={handleSignUpSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={signUpData.name}
                  onChange={handleSignUpChange}
                  placeholder="Enter your name"
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
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">Password</label>
                <input
                  type="password"
                  id="password"
                  name="password"
                  value={signUpData.password}
                  onChange={handleSignUpChange}
                  placeholder="Enter password"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={signUpData.confirmPassword}
                  onChange={handleSignUpChange}
                  placeholder="Confirm your password"
                  required
                />
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
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="gender">Gender</label>
                <select
                  id="gender"
                  name="gender"
                  value={signUpData.gender}
                  onChange={handleSignUpChange}
                  required
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                </select>
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

            <form onSubmit={handleSignInSubmit} className="auth-form">
              <div className="form-group">
                <label htmlFor="signin-username">Username</label>
                <input
                  type="text"
                  id="signin-username"
                  name="username"
                  value={signInData.username}
                  onChange={handleSignInChange}
                  placeholder="Enter username"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="signin-password">Password</label>
                <input
                  type="password"
                  id="signin-password"
                  name="password"
                  value={signInData.password}
                  onChange={handleSignInChange}
                  placeholder="Enter password"
                  required
                />
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

