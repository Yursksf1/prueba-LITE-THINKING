# API REST v1 - Contratos de API

Esta documentación define los contratos de la API REST v1 para el sistema de gestión de empresas, productos e inventario.

## 🔗 URL Base
```
/api/v1/
```

## 🔐 Autenticación

Todos los endpoints (excepto login) requieren autenticación mediante JWT (JSON Web Token).

### Headers requeridos
```
Authorization: Bearer <access_token>
```

---

## 📋 Tabla de Contenidos

1. [Autenticación](#autenticación)
2. [Empresas](#empresas)
3. [Productos](#productos)
4. [Inventario](#inventario)

---

## 🔑 Autenticación

### POST /api/v1/auth/login/

Autenticar usuario y obtener tokens JWT.

**Permisos:** Público (sin autenticación)

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response 200 OK:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "ADMINISTRATOR",
    "date_joined": "2026-01-09T00:00:00Z"
  }
}
```

**Response 400 Bad Request:**
```json
{
  "email": ["This field is required."],
  "password": ["This field is required."]
}
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Invalid credentials"
}
```

---

### GET /api/v1/auth/me

Obtener información del usuario autenticado.

**Permisos:** Autenticado

**Response 200 OK:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "ADMINISTRATOR",
  "date_joined": "2026-01-09T00:00:00Z"
}
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 🏢 Empresas

### GET /api/v1/companies

Listar todas las empresas.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**Response 200 OK:**
```json
[
  {
    "nit": "123456789",
    "name": "Empresa Demo S.A.S",
    "address": "Calle 123 #45-67, Bogotá",
    "phone": "+57 300 1234567"
  },
  {
    "nit": "987654321",
    "name": "Tech Solutions Ltda",
    "address": "Carrera 7 #12-34, Medellín",
    "phone": "+57 301 9876543"
  }
]
```

**Response 401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

### POST /api/v1/companies

Crear nueva empresa.

**Permisos:** ADMINISTRATOR

**Request Body:**
```json
{
  "nit": "123456789",
  "name": "Nueva Empresa S.A.S",
  "address": "Calle 100 #20-30, Cali",
  "phone": "+57 302 5555555"
}
```

**Response 201 Created:**
```json
{
  "nit": "123456789",
  "name": "Nueva Empresa S.A.S",
  "address": "Calle 100 #20-30, Cali",
  "phone": "+57 302 5555555",
  "created_at": "2026-01-09T10:30:00Z",
  "updated_at": "2026-01-09T10:30:00Z"
}
```

**Response 400 Bad Request:**
```json
{
  "nit": ["This field is required."],
  "name": ["This field is required."]
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### GET /api/v1/companies/{nit}

Obtener detalles de una empresa específica.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**URL Parameters:**
- `nit` (string): NIT de la empresa

**Response 200 OK:**
```json
{
  "nit": "123456789",
  "name": "Empresa Demo S.A.S",
  "address": "Calle 123 #45-67, Bogotá",
  "phone": "+57 300 1234567",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T00:00:00Z"
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

### PUT /api/v1/companies/{nit}

Actualizar empresa existente.

**Permisos:** ADMINISTRATOR

**URL Parameters:**
- `nit` (string): NIT de la empresa

**Request Body:**
```json
{
  "name": "Empresa Actualizada S.A.S",
  "address": "Nueva dirección",
  "phone": "+57 310 9999999"
}
```

**Response 200 OK:**
```json
{
  "nit": "123456789",
  "name": "Empresa Actualizada S.A.S",
  "address": "Nueva dirección",
  "phone": "+57 310 9999999",
  "created_at": "2026-01-09T00:00:00Z",
  "updated_at": "2026-01-09T10:45:00Z"
}
```

**Response 400 Bad Request:**
```json
{
  "phone": ["Invalid phone format."]
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

### DELETE /api/v1/companies/{nit}

Eliminar empresa.

**Permisos:** ADMINISTRATOR

**URL Parameters:**
- `nit` (string): NIT de la empresa

**Response 204 No Content:**
(Sin contenido)

**Response 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

## 📦 Productos

### GET /api/v1/companies/{nit}/products

Listar productos de una empresa específica.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**URL Parameters:**
- `nit` (string): NIT de la empresa

**Response 200 OK:**
```json
[
  {
    "code": "PROD001",
    "name": "Laptop HP ProBook",
    "company_nit": "123456789",
    "company_name": "Empresa Demo S.A.S"
  },
  {
    "code": "PROD002",
    "name": "Mouse Logitech MX Master",
    "company_nit": "123456789",
    "company_name": "Empresa Demo S.A.S"
  }
]
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

### POST /api/v1/companies/{nit}/products

Crear producto para una empresa específica.

**Permisos:** ADMINISTRATOR

**URL Parameters:**
- `nit` (string): NIT de la empresa

**Request Body:**
```json
{
  "code": "PROD003",
  "name": "Teclado Mecánico",
  "features": [
    "Switches Cherry MX Blue",
    "Retroiluminación RGB",
    "Cable USB-C"
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

**Response 201 Created:**
```json
{
  "code": "PROD003",
  "name": "Teclado Mecánico",
  "features": [
    "Switches Cherry MX Blue",
    "Retroiluminación RGB",
    "Cable USB-C"
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
  },
  "company_nit": "123456789",
  "company_name": "Empresa Demo S.A.S",
  "created_at": "2026-01-09T11:00:00Z",
  "updated_at": "2026-01-09T11:00:00Z"
}
```

**Response 400 Bad Request:**
```json
{
  "code": ["This field is required."],
  "prices": ["At least one price is required."]
}
```

**Response 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

## 📊 Inventario

### GET /api/v1/inventory/

Listar items del inventario, opcionalmente filtrado por empresa.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**Query Parameters:**
- `company_nit` (string, opcional): Filtrar por NIT de empresa

**Ejemplos:**
```
GET /api/v1/inventory/
GET /api/v1/inventory/?company_nit=123456789
```

**Response 200 OK:**
```json
[
  {
    "id": 1,
    "company_nit": "123456789",
    "company_name": "Empresa Demo S.A.S",
    "product_code": "PROD001",
    "product_name": "Laptop HP ProBook",
    "quantity": 50,
    "created_at": "2026-01-09T00:00:00Z",
    "updated_at": "2026-01-09T10:00:00Z"
  },
  {
    "id": 2,
    "company_nit": "123456789",
    "company_name": "Empresa Demo S.A.S",
    "product_code": "PROD002",
    "product_name": "Mouse Logitech MX Master",
    "quantity": 100,
    "created_at": "2026-01-09T00:00:00Z",
    "updated_at": "2026-01-09T09:30:00Z"
  }
]
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

### GET /api/v1/inventory/pdf/

Descargar reporte de inventario en formato PDF.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**Query Parameters:**
- `company_nit` (string, opcional): Filtrar por NIT de empresa

**Ejemplos:**
```
GET /api/v1/inventory/pdf/
GET /api/v1/inventory/pdf/?company_nit=123456789
```

**Response 200 OK:**
- **Content-Type:** `application/pdf`
- **Content-Disposition:** `attachment; filename="inventory_{nit}.pdf"` o `inventory_all.pdf`

**Nota:** Esta es una implementación placeholder. En producción, se generaría un PDF real utilizando una biblioteca como ReportLab o WeasyPrint.

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

---

### POST /api/v1/inventory/send-email/

Enviar reporte de inventario por correo electrónico.

**Permisos:** Autenticado (ADMINISTRATOR, EXTERNAL)

**Request Body:**
```json
{
  "email": "recipient@example.com",
  "company_nit": "123456789"
}
```

**Nota:** El campo `company_nit` es opcional. Si no se proporciona, se envía el inventario completo.

**Response 200 OK:**
```json
{
  "message": "Inventory report for Empresa Demo S.A.S sent successfully to recipient@example.com"
}
```

**Response 400 Bad Request:**
```json
{
  "email": ["Enter a valid email address."]
}
```

**Response 404 Not Found:**
```json
{
  "detail": "Company not found"
}
```

**Nota:** Esta es una implementación placeholder. En producción, se integraría con un servicio de correo electrónico real (SendGrid, AWS SES, etc.).

---

## 📝 Códigos de Error Comunes

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado exitosamente |
| 204 | No Content - Solicitud exitosa sin contenido de respuesta |
| 400 | Bad Request - Datos inválidos en la solicitud |
| 401 | Unauthorized - Credenciales inválidas o token faltante |
| 403 | Forbidden - Sin permisos para realizar la acción |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error - Error del servidor |

---

## 🔐 Roles y Permisos

### ADMINISTRATOR
- Acceso completo (lectura y escritura) a todos los endpoints
- Puede crear, actualizar y eliminar empresas
- Puede crear productos
- Puede ver y gestionar inventario
- Puede descargar PDFs y enviar correos

### EXTERNAL
- Solo lectura en empresas y productos
- Puede ver inventario
- Puede descargar PDFs
- Puede enviar correos de inventario
- **NO** puede crear, actualizar o eliminar recursos

---

## 🎯 Versionado

Esta API utiliza versionado explícito en la URL:
```
/api/v1/...
```

Esto permite:
- Estabilidad de contratos para clientes existentes
- Evolución de la API sin romper compatibilidad
- Migración gradual a nuevas versiones

---

## 📌 Notas de Implementación

### Separación de Responsabilidades
- La API REST es solo la capa de presentación
- La lógica de negocio reside en la capa de dominio (Python puro)
- La capa de aplicación orquesta casos de uso
- La infraestructura maneja persistencia y servicios externos

### Sin Lógica de Frontend
- Estos contratos son independientes de cualquier frontend
- Pueden ser consumidos por React, Vue, Angular, mobile apps, etc.
- La API no hace suposiciones sobre el cliente

### Placeholders
Los siguientes features son implementaciones placeholder:
- **Generación de PDF:** Se devuelve texto plano. En producción usar ReportLab/WeasyPrint
- **Envío de correos:** Se simula el envío. En producción integrar con SendGrid/AWS SES

---

## 🚀 Próximos Pasos

Para futuras versiones (v2, v3, etc.) considerar:
- Paginación en listados
- Filtros y búsquedas avanzadas
- Ordenamiento personalizable
- Rate limiting
- Webhooks
- GraphQL como alternativa
