import Card from '../atoms/Card';
import Button from '../atoms/Button';
import { authService } from '../services/api';
import './CompanyCard.css';

function CompanyCard({ company, onEdit, onDelete }) {
  const currentUser = authService.getCurrentUser();
  const isAdmin = currentUser?.role === 'ADMINISTRATOR';

  return (
    <Card className="company-card">
      <h3 className="company-name">{company.name}</h3>
      <div className="company-info">
        <p><strong>NIT:</strong> {company.nit}</p>
        <p><strong>Dirección:</strong> {company.address}</p>
        <p><strong>Teléfono:</strong> {company.phone}</p>
      </div>
      
      {isAdmin && (
        <div className="company-actions">
          <Button 
            variant="primary" 
            onClick={() => onEdit(company)}
          >
            Editar
          </Button>
          <Button 
            variant="danger" 
            onClick={() => onDelete(company)}
          >
            Eliminar
          </Button>
        </div>
      )}
    </Card>
  );
}

export default CompanyCard;
