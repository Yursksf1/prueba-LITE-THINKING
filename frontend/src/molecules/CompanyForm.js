import { useState, useEffect } from 'react';
import Input from '../atoms/Input';
import Button from '../atoms/Button';
import './CompanyForm.css';

function CompanyForm({ company, onSubmit, onCancel, loading = false }) {
  const [formData, setFormData] = useState({
    nit: '',
    name: '',
    address: '',
    phone: ''
  });

  const [errors, setErrors] = useState({});
  const isEditMode = !!company;

  useEffect(() => {
    if (company) {
      setFormData({
        nit: company.nit || '',
        name: company.name || '',
        address: company.address || '',
        phone: company.phone || ''
      });
    }
  }, [company]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }));
    }
  };

  const validate = () => {
    const newErrors = {};

    if (!formData.nit.trim()) {
      newErrors.nit = 'El NIT es requerido';
    }

    if (!formData.name.trim()) {
      newErrors.name = 'El nombre es requerido';
    }

    if (!formData.address.trim()) {
      newErrors.address = 'La dirección es requerida';
    }

    if (!formData.phone.trim()) {
      newErrors.phone = 'El teléfono es requerido';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validate()) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="company-form">
      <div className="form-group">
        <Input
          label="NIT"
          name="nit"
          value={formData.nit}
          onChange={handleChange}
          placeholder="Ej: 123456789"
          required
          disabled={isEditMode || loading}
        />
        {errors.nit && <span className="error-message">{errors.nit}</span>}
      </div>

      <div className="form-group">
        <Input
          label="Nombre de la Empresa"
          name="name"
          value={formData.name}
          onChange={handleChange}
          placeholder="Ej: Empresa Demo S.A.S"
          required
          disabled={loading}
        />
        {errors.name && <span className="error-message">{errors.name}</span>}
      </div>

      <div className="form-group">
        <Input
          label="Dirección"
          name="address"
          value={formData.address}
          onChange={handleChange}
          placeholder="Ej: Calle 123 #45-67, Bogotá"
          required
          disabled={loading}
        />
        {errors.address && <span className="error-message">{errors.address}</span>}
      </div>

      <div className="form-group">
        <Input
          label="Teléfono"
          name="phone"
          type="tel"
          value={formData.phone}
          onChange={handleChange}
          placeholder="Ej: +57 300 1234567"
          required
          disabled={loading}
        />
        {errors.phone && <span className="error-message">{errors.phone}</span>}
      </div>

      <div className="form-actions">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
          disabled={loading}
        >
          Cancelar
        </Button>
        <Button
          type="submit"
          variant="primary"
          disabled={loading}
        >
          {loading ? 'Guardando...' : (isEditMode ? 'Actualizar' : 'Crear')}
        </Button>
      </div>
    </form>
  );
}

export default CompanyForm;
