import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '../templates/MainLayout';
import ProductList from '../organisms/ProductList';
import Button from '../atoms/Button';
import { companyService } from '../services/api';
import './ProductsPage.css';

function ProductsPage() {
  const { nit } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCompany = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await companyService.getByNit(nit);
      setCompany(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Empresa no encontrada.');
      } else {
        setError('Error al cargar la empresa. Por favor, intente nuevamente.');
      }
      console.error('Error loading company:', err);
    } finally {
      setLoading(false);
    }
  }, [nit]);

  useEffect(() => {
    loadCompany();
  }, [loadCompany]);

  const handleBackClick = () => {
    navigate('/companies');
  };

  return (
    <MainLayout>
      <div className="products-page">
        <div className="page-header">
          <Button variant="secondary" onClick={handleBackClick}>
            ← Volver a Empresas
          </Button>
        </div>

        {loading ? (
          <div className="loading">Cargando...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <ProductList companyNit={nit} companyName={company.name} />
        )}
      </div>
    </MainLayout>
  );
}

export default ProductsPage;
