import { useState, useEffect } from 'react';
import CompanyCard from '../molecules/CompanyCard';
import CompanyForm from '../molecules/CompanyForm';
import Modal from '../atoms/Modal';
import Button from '../atoms/Button';
import { companyService, authService } from '../services/api';
import './CompanyList.css';

function CompanyList() {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFormModalOpen, setIsFormModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  const [deleteLoading, setDeleteLoading] = useState(false);

  const currentUser = authService.getCurrentUser();
  const isAdmin = currentUser?.role === 'ADMINISTRATOR';

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

  const handleCreateClick = () => {
    setSelectedCompany(null);
    setIsFormModalOpen(true);
  };

  const handleEditClick = (company) => {
    setSelectedCompany(company);
    setIsFormModalOpen(true);
  };

  const handleDeleteClick = (company) => {
    setSelectedCompany(company);
    setIsDeleteModalOpen(true);
  };

  const handleFormSubmit = async (formData) => {
    try {
      setFormLoading(true);
      setError(null);

      if (selectedCompany) {
        // Update existing company
        await companyService.update(selectedCompany.nit, formData);
      } else {
        // Create new company
        await companyService.create(formData);
      }

      setIsFormModalOpen(false);
      setSelectedCompany(null);
      await loadCompanies();
    } catch (err) {
      setError(
        err.response?.data?.message || 
        `Error al ${selectedCompany ? 'actualizar' : 'crear'} la empresa. Por favor, intente nuevamente.`
      );
      console.error('Error submitting form:', err);
    } finally {
      setFormLoading(false);
    }
  };

  const handleDeleteConfirm = async () => {
    if (!selectedCompany) return;

    try {
      setDeleteLoading(true);
      setError(null);
      await companyService.delete(selectedCompany.nit);
      setIsDeleteModalOpen(false);
      setSelectedCompany(null);
      await loadCompanies();
    } catch (err) {
      setError('Error al eliminar la empresa. Por favor, intente nuevamente.');
      console.error('Error deleting company:', err);
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleModalClose = () => {
    if (!formLoading && !deleteLoading) {
      setIsFormModalOpen(false);
      setIsDeleteModalOpen(false);
      setSelectedCompany(null);
    }
  };

  if (loading) {
    return <div className="loading">Cargando empresas...</div>;
  }

  return (
    <div className="company-list-container">
      {isAdmin && (
        <div className="company-list-header">
          <Button variant="primary" onClick={handleCreateClick}>
            + Crear Empresa
          </Button>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      {companies.length === 0 ? (
        <div className="empty">No hay empresas registradas.</div>
      ) : (
        <div className="company-list">
          {companies.map((company) => (
            <CompanyCard 
              key={company.nit} 
              company={company}
              onEdit={handleEditClick}
              onDelete={handleDeleteClick}
            />
          ))}
        </div>
      )}

      {/* Form Modal */}
      <Modal
        isOpen={isFormModalOpen}
        onClose={handleModalClose}
        title={selectedCompany ? 'Editar Empresa' : 'Crear Empresa'}
      >
        <CompanyForm
          company={selectedCompany}
          onSubmit={handleFormSubmit}
          onCancel={handleModalClose}
          loading={formLoading}
        />
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={isDeleteModalOpen}
        onClose={handleModalClose}
        title="Confirmar Eliminación"
        size="small"
      >
        <div className="delete-confirmation">
          <p>¿Está seguro que desea eliminar la empresa:</p>
          <p className="company-name-delete"><strong>{selectedCompany?.name}</strong></p>
          <p>Esta acción no se puede deshacer.</p>
          
          <div className="delete-actions">
            <Button
              variant="secondary"
              onClick={handleModalClose}
              disabled={deleteLoading}
            >
              Cancelar
            </Button>
            <Button
              variant="danger"
              onClick={handleDeleteConfirm}
              disabled={deleteLoading}
            >
              {deleteLoading ? 'Eliminando...' : 'Eliminar'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

export default CompanyList;
