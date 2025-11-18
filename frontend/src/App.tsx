import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import { UserProvider } from './contexts/UserContext';
import Navigation from './components/Navigation';
import Home from './components/Home';
import Onboarding from './components/Onboarding';
import FoodSuggestions from './components/FoodSuggestions';
import FoodDetail from './components/FoodDetail';
import IngredientDetail from './components/IngredientDetail';
import History from './components/History';
import Profile from './components/Profile';
import Auth from './components/Auth';
import './App.css';

function AppContent() {
  const location = useLocation();
  const isAuthPage = location.pathname === '/auth' || location.pathname === '/signup' || location.pathname === '/signin';

  return (
    <div className="app">
      {!isAuthPage && <Navigation />}
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/signup" element={<Auth />} />
          <Route path="/signin" element={<Auth />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/suggestions" element={<FoodSuggestions />} />
                <Route path="/food/:id" element={<FoodDetail />} />
                <Route path="/ingredient/:id" element={<IngredientDetail />} />
                <Route path="/history" element={<History />} />
                <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <UserProvider>
      <Router>
        <AppContent />
      </Router>
    </UserProvider>
  );
}

export default App;
