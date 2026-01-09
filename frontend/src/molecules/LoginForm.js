import { useState } from 'react';
import Input from '../atoms/Input';
import Button from '../atoms/Button';
import './LoginForm.css';

function LoginForm({ onSubmit, loading, error }) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="login-form">
      <h2 className="login-form-title">Iniciar Sesión</h2>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <Input
        type="email"
        name="email"
        value={formData.email}
        onChange={handleChange}
        placeholder="correo@ejemplo.com"
        label="Correo Electrónico"
        required
        disabled={loading}
      />
      
      <Input
        type="password"
        name="password"
        value={formData.password}
        onChange={handleChange}
        placeholder="********"
        label="Contraseña"
        required
        disabled={loading}
      />
      
      <Button
        type="submit"
        variant="primary"
        fullWidth
        disabled={loading}
      >
        {loading ? 'Ingresando...' : 'Ingresar'}
      </Button>
    </form>
  );
}

export default LoginForm;
