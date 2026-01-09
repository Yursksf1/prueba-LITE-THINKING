import { useParams, useNavigate } from 'react-router-dom';
import { useState, useEffect, useCallback } from 'react';
import MainLayout from '../templates/MainLayout';
import Button from '../atoms/Button';
import Modal from '../atoms/Modal';
import Input from '../atoms/Input';
import { inventoryService, companyService, authService } from '../services/api';
import './InventoryPage.css';

function InventoryPage() {
  const { nit } = useParams();
  const navigate = useNavigate();
  const [company, setCompany] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEmailModalOpen, setIsEmailModalOpen] = useState(false);
  const [email, setEmail] = useState('');
  const [emailLoading, setEmailLoading] = useState(false);
  const [emailError, setEmailError] = useState(null);
  const [emailSuccess, setEmailSuccess] = useState(false);
  const [downloadLoading, setDownloadLoading] = useState(false);

  const currentUser = authService.getCurrentUser();
  const isAdmin = currentUser?.role === 'ADMINISTRATOR';

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [companyData, inventoryData] = await Promise.all([
        companyService.getByNit(nit),
        inventoryService.getByCompany(nit)
      ]);
      
      setCompany(companyData);
      setInventory(inventoryData);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Empresa no encontrada.');
      } else {
        setError('Error al cargar el inventario. Por favor, intente nuevamente.');
      }
      console.error('Error loading inventory:', err);
    } finally {
      setLoading(false);
    }
  }, [nit]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleBackClick = () => {
    navigate(`/companies/${nit}/products`);
  };

  const handleDownloadPdf = async () => {
    try {
      setDownloadLoading(true);
      setError(null);
      
      const blob = await inventoryService.downloadPdf(nit);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `inventory_${nit}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Error al descargar el PDF. Por favor, intente nuevamente.');
      console.error('Error downloading PDF:', err);
    } finally {
      setDownloadLoading(false);
    }
  };

  const handleSendEmailClick = () => {
    setEmail('');
    setEmailError(null);
    setEmailSuccess(false);
    setIsEmailModalOpen(true);
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    
    if (!email) {
      setEmailError('El correo electrónico es requerido.');
      return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setEmailError('Por favor ingrese un correo electrónico válido.');
      return;
    }
    
    try {
      setEmailLoading(true);
      setEmailError(null);
      
      await inventoryService.sendEmail(nit, email);
      setEmailSuccess(true);
      
      setTimeout(() => {
        setIsEmailModalOpen(false);
        setEmailSuccess(false);
      }, 2000);
    } catch (err) {
      if (err.response?.status === 400) {
        setEmailError('Correo electrónico inválido.');
      } else {
        setEmailError('Error al enviar el correo. Por favor, intente nuevamente.');
      }
      console.error('Error sending email:', err);
    } finally {
      setEmailLoading(false);
    }
  };

  const handleModalClose = () => {
    if (!emailLoading) {
      setIsEmailModalOpen(false);
      setEmail('');
      setEmailError(null);
      setEmailSuccess(false);
    }
  };

  const formatPrice = (prices) => {
    if (!prices || typeof prices !== 'object') return 'N/A';
    
    const priceStrings = Object.entries(prices).map(([currency, priceData]) => {
      const amount = priceData?.amount || priceData;
      return `${currency}: ${parseFloat(amount).toFixed(2)}`;
    });
    
    return priceStrings.join(' | ');
  };

  return (
    <MainLayout>
      <div className="inventory-page">
        <div className="page-header">
          <Button variant="secondary" onClick={handleBackClick}>
            ← Volver a Productos
          </Button>
        </div>

        {loading ? (
          <div className="loading">Cargando inventario...</div>
        ) : error ? (
          <div className="error">{error}</div>
        ) : (
          <>
            <div className="inventory-header">
              <div>
                <h1 className="page-title">Inventario</h1>
                <p className="page-subtitle">{company?.name}</p>
              </div>
              
              {isAdmin && (
                <div className="inventory-actions">
                  <Button 
                    variant="primary" 
                    onClick={handleDownloadPdf}
                    disabled={downloadLoading}
                  >
                    {downloadLoading ? 'Descargando...' : '📥 Descargar PDF'}
                  </Button>
                  <Button 
                    variant="primary" 
                    onClick={handleSendEmailClick}
                  >
                    📧 Enviar PDF
                  </Button>
                </div>
              )}
            </div>

            {inventory.length === 0 ? (
              <div className="empty">No hay productos en el inventario de esta empresa.</div>
            ) : (
              <div className="inventory-table-container">
                <table className="inventory-table">
                  <thead>
                    <tr>
                      <th>Código del Producto</th>
                      <th>Nombre</th>
                      <th>Cantidad</th>
                      <th>Precios</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventory.map((item) => (
                      <tr key={item.id}>
                        <td>{item.product_code}</td>
                        <td>{item.product_name}</td>
                        <td className="quantity">{item.quantity}</td>
                        <td className="prices">{formatPrice(item.prices)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </>
        )}

        {/* Email Modal */}
        <Modal
          isOpen={isEmailModalOpen}
          onClose={handleModalClose}
          title="Enviar Inventario por Correo"
          size="small"
        >
          <form onSubmit={handleEmailSubmit} className="email-form">
            <Input
              type="email"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="correo@ejemplo.com"
              label="Correo electrónico"
              required
              disabled={emailLoading || emailSuccess}
            />
            
            {emailError && <div className="error">{emailError}</div>}
            {emailSuccess && <div className="success">¡Correo enviado exitosamente!</div>}
            
            <div className="email-actions">
              <Button
                type="button"
                variant="secondary"
                onClick={handleModalClose}
                disabled={emailLoading || emailSuccess}
              >
                Cancelar
              </Button>
              <Button
                type="submit"
                variant="primary"
                disabled={emailLoading || emailSuccess}
              >
                {emailLoading ? 'Enviando...' : 'Enviar'}
              </Button>
            </div>
          </form>
        </Modal>
      </div>
    </MainLayout>
  );
}

export default InventoryPage;
