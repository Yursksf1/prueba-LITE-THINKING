import { useState, useEffect, useCallback } from 'react';
import ProductCard from '../molecules/ProductCard';
import ProductForm from '../molecules/ProductForm';
import Modal from '../atoms/Modal';
import Button from '../atoms/Button';
import { productService, authService } from '../services/api';
import './ProductList.css';

function ProductList({ companyNit, companyName }) {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [formLoading, setFormLoading] = useState(false);

  const currentUser = authService.getCurrentUser();
  const isAdmin = currentUser?.role === 'ADMINISTRATOR';

  const loadProducts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await productService.getByCompany(companyNit);
      setProducts(data);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Empresa no encontrada.');
      } else if (err.response?.status === 403) {
        setError('No tiene permisos para ver los productos.');
      } else {
        setError('Error al cargar productos. Por favor, intente nuevamente.');
      }
      console.error('Error loading products:', err);
    } finally {
      setLoading(false);
    }
  }, [companyNit]);

  useEffect(() => {
    loadProducts();
  }, [loadProducts]);

  const handleCreateClick = () => {
    setIsFormModalOpen(true);
  };

  const handleFormSubmit = async (productData) => {
    try {
      setFormLoading(true);
      setError(null);
      await productService.create(companyNit, productData);
      setIsFormModalOpen(false);
      await loadProducts();
    } catch (err) {
      if (err.response?.status === 403) {
        setError('No tiene permisos para crear productos.');
      } else if (err.response?.status === 400) {
        setError(err.response?.data?.message || 'Datos inválidos. Verifique el formulario.');
      } else {
        setError('Error al crear el producto. Por favor, intente nuevamente.');
      }
      console.error('Error creating product:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleModalClose = () => {
    if (!formLoading) {
      setIsFormModalOpen(false);
    }
  };

  if (loading) {
    return <div className="loading">Cargando productos...</div>;
  }

  return (
    <div className="product-list-container">
      <div className="product-list-header">
        <div>
          <h2 className="product-list-title">Productos</h2>
          <p className="product-list-subtitle">{companyName}</p>
        </div>
        
        {isAdmin && (
          <Button variant="primary" onClick={handleCreateClick}>
            + Crear Producto
          </Button>
        )}
      </div>

      {error && <div className="error">{error}</div>}

      {products.length === 0 ? (
        <div className="empty">No hay productos registrados para esta empresa.</div>
      ) : (
        <div className="product-list">
          {products.map((product) => (
            <ProductCard key={product.code} product={product} />
          ))}
        </div>
      )}

      {/* Form Modal */}
      <Modal
        isOpen={isFormModalOpen}
        onClose={handleModalClose}
        title="Crear Producto"
        size="large"
      >
        <ProductForm
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          loading={formLoading}
        />
      </Modal>
    </div>
  );
}

export default ProductList;
