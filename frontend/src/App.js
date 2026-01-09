import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import CompaniesPage from './pages/CompaniesPage';
import ProductsPage from './pages/ProductsPage';
import ProtectedRoute from './utils/ProtectedRoute';
import { authService } from './services/api';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route 
          path="/companies" 
          element={
            <ProtectedRoute>
              <CompaniesPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/companies/:nit/products" 
          element={
            <ProtectedRoute>
              <ProductsPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/" 
          element={
            authService.isAuthenticated() ? 
              <Navigate to="/companies" replace /> : 
              <Navigate to="/login" replace />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
