import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';
import Navigation from './components/Navigation';
import Home from './components/Home';
import Onboarding from './components/Onboarding';
import UploadIngredients from './components/UploadIngredients';
import FoodSuggestions from './components/FoodSuggestions';
import FoodDetail from './components/FoodDetail';
import FoodList from './components/FoodList';
import IngredientDetail from './components/IngredientDetail';
import History from './components/History';
import Profile from './components/Profile';
import './App.css';

function App() {
  return (
    <UserProvider>
      <Router>
        <div className="app">
          <Navigation isLoggedIn={true} />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/onboarding" element={<Onboarding />} />
              <Route path="/upload" element={<UploadIngredients />} />
              <Route path="/suggestions" element={<FoodSuggestions />} />
                    <Route path="/foods" element={<FoodList />} />
                    <Route path="/food/:id" element={<FoodDetail />} />
                    <Route path="/ingredient/:id" element={<IngredientDetail />} />
                    <Route path="/history" element={<History />} />
                    <Route path="/profile" element={<Profile />} />
            </Routes>
          </main>
        </div>
      </Router>
    </UserProvider>
  );
}

export default App;
