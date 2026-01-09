import { useState } from 'react';
import Input from '../atoms/Input';
import Button from '../atoms/Button';
import './ProductForm.css';

const AVAILABLE_CURRENCIES = ['USD', 'COP', 'EUR', 'GBP', 'JPY', 'MXN', 'BRL'];

function ProductForm({ onSubmit, onCancel, loading = false }) {
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    features: [''],
    prices: [{ currency: 'USD', amount: '' }]
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFeatureChange = (index, value) => {
    const newFeatures = [...formData.features];
    newFeatures[index] = value;
    setFormData(prev => ({
      ...prev,
      features: newFeatures
    }));
  };

  const addFeature = () => {
    setFormData(prev => ({
      ...prev,
      features: [...prev.features, '']
    }));
  };

  const removeFeature = (index) => {
    if (formData.features.length > 1) {
      const newFeatures = formData.features.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        features: newFeatures
      }));
    }
  };

  const handlePriceChange = (index, field, value) => {
    const newPrices = [...formData.prices];
    newPrices[index] = {
      ...newPrices[index],
      [field]: value
    };
    setFormData(prev => ({
      ...prev,
      prices: newPrices
    }));
  };

  const addPrice = () => {
    setFormData(prev => ({
      ...prev,
      prices: [...prev.prices, { currency: 'USD', amount: '' }]
    }));
  };

  const removePrice = (index) => {
    if (formData.prices.length > 1) {
      const newPrices = formData.prices.filter((_, i) => i !== index);
      setFormData(prev => ({
        ...prev,
        prices: newPrices
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Transform data to match new API contract: { "USD": 100.0, ... }
    const prices = {};
    formData.prices.forEach(price => {
      if (price.currency && price.amount) {
        prices[price.currency] = parseFloat(price.amount);
      }
    });

    // Filter out empty features
    const features = formData.features.filter(f => f.trim() !== '');

    const productData = {
      code: formData.code,
      name: formData.name,
      features: features.length > 0 ? features : [],
      prices: prices
    };

    onSubmit(productData);
  };

  return (
    <form onSubmit={handleSubmit} className="product-form">
      <Input
        name="code"
        label="Código del Producto *"
        value={formData.code}
        onChange={handleInputChange}
        placeholder="Ej: PROD001"
        required
        disabled={loading}
      />

      <Input
        name="name"
        label="Nombre del Producto *"
        value={formData.name}
        onChange={handleInputChange}
        placeholder="Ej: Laptop HP ProBook"
        required
        disabled={loading}
      />

      <div className="form-section">
        <div className="section-header">
          <label className="section-label">Características</label>
          <Button 
            type="button" 
            variant="secondary" 
            onClick={addFeature}
            disabled={loading}
          >
            + Agregar Característica
          </Button>
        </div>
        
        {formData.features.map((feature, index) => (
          <div key={index} className="dynamic-field">
            <input
              type="text"
              value={feature}
              onChange={(e) => handleFeatureChange(index, e.target.value)}
              placeholder={`Característica ${index + 1}`}
              className="input-field"
              disabled={loading}
            />
            {formData.features.length > 1 && (
              <Button 
                type="button" 
                variant="danger" 
                onClick={() => removeFeature(index)}
                disabled={loading}
              >
                Eliminar
              </Button>
            )}
          </div>
        ))}
      </div>

      <div className="form-section">
        <div className="section-header">
          <label className="section-label">Precios por Moneda *</label>
          <Button 
            type="button" 
            variant="secondary" 
            onClick={addPrice}
            disabled={loading}
          >
            + Agregar Precio
          </Button>
        </div>
        
        {formData.prices.map((price, index) => (
          <div key={index} className="dynamic-field price-field">
            <select
              value={price.currency}
              onChange={(e) => handlePriceChange(index, 'currency', e.target.value)}
              className="input-field currency-select"
              disabled={loading}
            >
              {AVAILABLE_CURRENCIES.map(currency => (
                <option key={currency} value={currency}>{currency}</option>
              ))}
            </select>
            
            <input
              type="number"
              value={price.amount}
              onChange={(e) => handlePriceChange(index, 'amount', e.target.value)}
              placeholder="Monto"
              step="0.01"
              min="0"
              className="input-field price-input"
              required
              disabled={loading}
            />
            
            {formData.prices.length > 1 && (
              <Button 
                type="button" 
                variant="danger" 
                onClick={() => removePrice(index)}
                disabled={loading}
              >
                Eliminar
              </Button>
            )}
          </div>
        ))}
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
          {loading ? 'Creando...' : 'Crear Producto'}
        </Button>
      </div>
    </form>
  );
}

export default ProductForm;
