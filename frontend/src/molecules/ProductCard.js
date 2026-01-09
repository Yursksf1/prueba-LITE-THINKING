import Card from '../atoms/Card';
import './ProductCard.css';

function ProductCard({ product }) {
  const formatPrice = (amount) => {
    return new Intl.NumberFormat('es-CO').format(amount);
  };

  return (
    <Card className="product-card">
      <div className="product-card-header">
        <h3 className="product-code">{product.code}</h3>
        <span className="product-company">{product.company_name}</span>
      </div>
      
      <h4 className="product-name">{product.name}</h4>
      
      {product.features && product.features.length > 0 && (
        <div className="product-features">
          <p className="features-title">Características:</p>
          <ul className="features-list">
            {product.features.map((feature, index) => (
              <li key={index}>{feature}</li>
            ))}
          </ul>
        </div>
      )}
      
      {product.prices && Object.keys(product.prices).length > 0 && (
        <div className="product-prices">
          <p className="prices-title">Precios:</p>
          <div className="prices-list">
            {Object.entries(product.prices).map(([currency, priceData]) => (
              <div key={currency} className="price-item">
                <span className="currency">{currency}</span>
                <span className="amount">{formatPrice(priceData.amount)}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </Card>
  );
}

export default ProductCard;
