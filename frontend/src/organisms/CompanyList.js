import { useState, useEffect } from 'react';
import CompanyCard from '../molecules/CompanyCard';
import { companyService } from '../services/api';
import './CompanyList.css';

function CompanyList() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await companyService.getAll();
      setCompanies(data);
    } catch (err) {
      setError('Error al cargar empresas. Por favor, intente nuevamente.');
      console.error('Error loading companies:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando empresas...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (companies.length === 0) {
    return <div className="empty">No hay empresas registradas.</div>;
  }

  return (
    <div className="company-list">
      {companies.map((company) => (
        <CompanyCard key={company.nit} company={company} />
      ))}
    </div>
  );
}

export default CompanyList;
