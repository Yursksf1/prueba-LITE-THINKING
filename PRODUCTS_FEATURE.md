# Product Management Feature with Multi-Currency Support

## Overview

This feature allows users to view and create products associated with a company, including the management of prices in multiple currencies.

## Features Implemented

### For All Authenticated Users
- **View Products by Company**: Navigate from the companies list to view all products for a specific company
- **Product Information Display**:
  - Product Code
  - Product Name
  - Characteristics/Features (list)
  - Prices by Currency (multiple currencies supported)

### For Administrator Users
- **Create Products**: Modal form to create new products with:
  - Code (required)
  - Name (required)
  - Dynamic list of features (add/remove)
  - Dynamic list of prices with currency and amount (add/remove)
  - At least one price is required
  
## User Interface

### Companies Page
- Updated `CompanyCard` component with "Ver Productos" button
- All users can click to view products for any company

### Products Page (`/companies/:nit/products`)
- Back button to return to companies list
- Company name displayed in header
- Grid layout of product cards
- "Crear Producto" button (Admin only)
- Loading and error states

### Product Creation Modal
- Large modal with product form
- Multiple sections:
  - Basic information (code, name)
  - Dynamic features list (add/remove features)
  - Dynamic prices list (add/remove prices)
- Currency selector with common currencies: USD, COP, EUR, GBP, JPY, MXN, BRL
- Form validation
- Loading state during submission

## Technical Implementation

### New Components

#### Atoms
- No new atoms (reused existing: Button, Input, Card, Modal)

#### Molecules
- **ProductCard** (`molecules/ProductCard.js`)
  - Displays product information
  - Shows all prices formatted by currency
  - Lists all features
  
- **ProductForm** (`molecules/ProductForm.js`)
  - Dynamic form for product creation
  - Handles multiple features (add/remove)
  - Handles multiple prices (add/remove)
  - Currency selection dropdown
  - Transforms data to match API contract

#### Organisms
- **ProductList** (`organisms/ProductList.js`)
  - Fetches products for a company
  - Grid layout of product cards
  - Handles product creation (Admin only)
  - Error handling (403, 404, 500)
  - Loading states

#### Pages
- **ProductsPage** (`pages/ProductsPage.js`)
  - Protected route
  - Fetches company information
  - Renders ProductList organism
  - Navigation back to companies

### API Integration

#### New Service
- **productService** (`services/api.js`)
  - `getByCompany(nit)`: Fetch products for a company
  - `create(nit, productData)`: Create new product

### Routing
- New route: `/companies/:nit/products`
- Protected with authentication
- Dynamic NIT parameter

## API Contract

### GET `/api/v1/companies/{nit}/products/`
**Permissions**: Authenticated (ADMINISTRATOR, EXTERNAL)

**Response 200**:
```json
[
  {
    "code": "PROD001",
    "name": "Laptop HP ProBook",
    "company_nit": "123456789",
    "company_name": "Company Name"
  }
]
```

### POST `/api/v1/companies/{nit}/products/`
**Permissions**: ADMINISTRATOR only

**Request**:
```json
{
  "code": "PROD003",
  "name": "Teclado Mecánico",
  "features": [
    "Switches Cherry MX Blue",
    "Retroiluminación RGB"
  ],
  "prices": {
    "USD": {
      "amount": 150.00,
      "currency": "USD"
    },
    "COP": {
      "amount": 600000.00,
      "currency": "COP"
    }
  }
}
```

**Response 201**:
```json
{
  "code": "PROD003",
  "name": "Teclado Mecánico",
  "features": ["Switches Cherry MX Blue", "Retroiluminación RGB"],
  "prices": {
    "USD": {"amount": 150.00, "currency": "USD"},
    "COP": {"amount": 600000.00, "currency": "COP"}
  },
  "company_nit": "123456789",
  "company_name": "Company Name",
  "created_at": "2026-01-09T11:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

## Error Handling

### HTTP Status Codes
- **400**: Invalid data (missing required fields, validation errors)
- **403**: Forbidden (non-admin trying to create products)
- **404**: Company not found
- **500**: Internal server error

### User-Friendly Messages
- Loading states: "Cargando productos..."
- Empty state: "No hay productos registrados para esta empresa."
- Errors displayed in red alert boxes with appropriate messages

## Design Decisions

### No Hardcoded NITs
- NIT is always passed as a route parameter or prop
- No hardcoded company identifiers

### Reusable Components
- All components follow Atomic Design principles
- Components can be reused in other contexts
- Clear separation of concerns

### Permission-Based UI
- "Crear Producto" button only visible to administrators
- Read-only view for non-administrators
- Backend enforces permissions

### Dynamic Form Fields
- Users can add/remove features as needed
- Users can add/remove prices for different currencies
- At least one price required
- Empty features are filtered out

### No Currency Conversion
- Prices are stored and displayed as-is
- No automatic currency conversion
- Each price is independent

### Responsive Design
- Mobile-friendly layouts
- Grid adapts to screen size
- Modal adjusts to viewport

## Future Enhancements (Out of Scope)

- ❌ Edit products
- ❌ Delete products
- ❌ Product inventory/stock
- ❌ Advanced filters
- ❌ Search functionality
- ❌ Currency conversion
- ❌ Price history
- ❌ Bulk operations

## Testing

### Build
```bash
cd frontend
npm run build
```
✅ Build passes successfully with no warnings

### Manual Testing
1. Login as administrator
2. Navigate to companies page
3. Click "Ver Productos" on any company
4. View products list
5. Click "Crear Producto"
6. Fill form with multiple features and prices
7. Submit form
8. Verify new product appears in list

## File Structure

```
frontend/src/
├── molecules/
│   ├── ProductCard.js          # Product display card
│   ├── ProductCard.css
│   ├── ProductForm.js          # Product creation form
│   └── ProductForm.css
├── organisms/
│   ├── ProductList.js          # Products list with CRUD
│   └── ProductList.css
├── pages/
│   ├── ProductsPage.js         # Products page container
│   └── ProductsPage.css
└── services/
    └── api.js                  # Added productService
```

## Dependencies

No new dependencies were added. The feature uses:
- React 19.2
- React Router v7
- Axios
- Existing component library

## Acceptance Criteria

✅ Product listing functional
✅ Clear visualization of prices by currency
✅ Form prepared for multiple prices (add/remove)
✅ Correct API integration
✅ Does not break existing functionality
✅ Permission-based access (Admin can create, all can view)
✅ Error handling for 403, 400, 500
✅ Loading states
✅ No hardcoded NITs
✅ Reusable components
