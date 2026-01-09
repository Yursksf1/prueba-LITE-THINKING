import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import LoginForm from '../molecules/LoginForm';
import { authService } from '../services/api';
import './LoginPage.css';

function LoginPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (formData) => {
    try {
      setLoading(true);
      setError(null);
      await authService.login(formData.email, formData.password);
      navigate('/companies');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al iniciar sesión. Verifique sus credenciales.');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h1>Lite Thinking</h1>
          <p>Sistema de Gestión de Empresas</p>
        </div>
        <LoginForm onSubmit={handleLogin} loading={loading} error={error} />
      </div>
    </div>
  );
}

export default LoginPage;
