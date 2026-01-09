import Card from '../atoms/Card';
import './CompanyCard.css';

function CompanyCard({ company }) {
  return (
    <Card className="company-card">
      <h3 className="company-name">{company.name}</h3>
      <div className="company-info">
        <p><strong>NIT:</strong> {company.nit}</p>
        <p><strong>Dirección:</strong> {company.address}</p>
        <p><strong>Teléfono:</strong> {company.phone}</p>
      </div>
    </Card>
  );
}

export default CompanyCard;
