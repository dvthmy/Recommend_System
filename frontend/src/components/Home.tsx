import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../contexts/UserContext';
import './Home.css';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const { user, isLoading } = useUser();

  const handleStart = () => {
    if (user) {
      navigate('/onboarding');
    } else {
      console.log('User not initialized yet');
    }
  };

  const handleUpload = () => {
    if (user) {
      navigate('/upload');
    } else {
      console.log('User not initialized yet');
    }
  };

  if (isLoading) {
    return (
      <div className="home-container">
        <div className="container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h3>Initializing...</h3>
            <p>Setting up your personalized experience</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="home-container">
      <div className="container">
        <div className="home-hero">
          <div className="hero-content">
            <h1 className="hero-title">
              Discover amazing dishes from your ingredients
            </h1>
            <p className="hero-description">
              FoodAI uses artificial intelligence to analyze ingredients and suggest the most suitable dishes based on your preferences.
            </p>
            
            <div className="hero-actions">
              <button className="btn btn-primary btn-lg" onClick={handleStart}>
                Get Started Now
              </button>
              <button className="btn btn-outline btn-lg" onClick={handleUpload}>
                Upload Ingredient Photos
              </button>
            </div>
          </div>
          
          <div className="hero-image">
            <div className="food-showcase">
              <div className="food-item">
                <div className="food-placeholder"></div>
                <span>Pho Bo</span>
              </div>
              <div className="food-item">
                <div className="food-placeholder"></div>
                <span>Salad</span>
              </div>
              <div className="food-item">
                <div className="food-placeholder"></div>
                <span>Asian Cuisine</span>
              </div>
            </div>
          </div>
        </div>

        <div className="features-section">
          <h2 className="features-title">Why Choose FoodAI?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
              </div>
              <h3>Smart AI</h3>
              <p>Analyze ingredients with advanced AI technology</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
              </div>
              <h3>Fast</h3>
              <p>Get dish suggestions in just seconds</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
              </div>
              <h3>Personalized</h3>
              <p>Suggestions based on your preferences and dietary restrictions</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">
              </div>
              <h3>Easy to Use</h3>
              <p>Friendly, simple and intuitive interface</p>
            </div>
          </div>
        </div>

        <div className="how-it-works">
          <h2 className="how-title">How It Works</h2>
          <div className="steps">
            <div className="step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Upload Ingredient Photos</h3>
                <p>Take or upload photos of your ingredients</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>AI Analysis</h3>
                <p>AI system identifies and lists the ingredients</p>
              </div>
            </div>
            <div className="step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Get Dish Suggestions</h3>
                <p>Receive suggestions for dishes that match your ingredients</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home;
