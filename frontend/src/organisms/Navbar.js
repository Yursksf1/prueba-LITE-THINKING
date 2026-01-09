import { useNavigate } from 'react-router-dom';
import Button from '../atoms/Button';
import { authService } from '../services/api';
import './Navbar.css';

function Navbar() {
  const navigate = useNavigate();
  const user = authService.getCurrentUser();
  const isAuthenticated = authService.isAuthenticated();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-brand" onClick={() => navigate('/')}>
          <h1>Lite Thinking</h1>
        </div>
        
        <div className="navbar-menu">
          {isAuthenticated ? (
            <>
              <span className="navbar-user">
                Hola, {user?.first_name || user?.email}
              </span>
              <Button onClick={handleLogout} variant="secondary">
                Cerrar Sesión
              </Button>
            </>
          ) : (
            <Button onClick={() => navigate('/login')} variant="primary">
              Iniciar Sesión
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
