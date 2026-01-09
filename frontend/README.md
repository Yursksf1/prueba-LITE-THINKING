# Frontend - Lite Thinking

Frontend de React 19.2 siguiendo principios de Atomic Design.

## 🏗️ Estructura del Proyecto

```
src/
├── atoms/              # Componentes básicos reutilizables
│   ├── Button.js       # Botón básico
│   ├── Input.js        # Campo de entrada
│   └── Card.js         # Tarjeta contenedora
│
├── molecules/          # Componentes compuestos
│   ├── LoginForm.js    # Formulario de login
│   └── CompanyCard.js  # Tarjeta de empresa
│
├── organisms/          # Componentes complejos
│   ├── Navbar.js       # Barra de navegación
│   ├── Footer.js       # Pie de página
│   └── CompanyList.js  # Lista de empresas
│
├── templates/          # Plantillas de página
│   └── MainLayout.js   # Layout principal
│
├── pages/              # Páginas completas
│   ├── LoginPage.js    # Página de login
│   └── CompaniesPage.js # Página de empresas
│
├── services/           # Servicios de API
│   └── api.js          # Cliente HTTP y servicios
│
└── utils/              # Utilidades
    └── ProtectedRoute.js # Ruta protegida
```

## 🚀 Características

- **React 19.2** con hooks modernos
- **React Router** para navegación
- **Axios** para consumo de API REST
- **Atomic Design** para organización de componentes
- **Autenticación JWT** con localStorage
- **Variables de entorno** para configuración

## 📦 Dependencias

- `react` ^19.2.3
- `react-dom` ^19.2.3
- `react-router-dom` ^7.1.3
- `axios` ^1.7.9

## 🔧 Configuración

1. Crear archivo `.env` en la raíz del frontend:

```env
REACT_APP_API_URL=http://localhost:8000
```

2. Instalar dependencias:

```bash
npm install
```

3. Ejecutar en desarrollo:

```bash
npm start
```

## 🐳 Docker

El proyecto incluye `Dockerfile` y está configurado en `docker-compose.yml`:

```bash
docker-compose up frontend
```

## 📱 Vistas Implementadas

### Login
- Ruta: `/login`
- Formulario de autenticación
- Validación de credenciales
- Redirección automática tras login exitoso

### Listado de Empresas
- Ruta: `/companies`
- Lista de empresas registradas
- Vista de solo lectura
- Protegida por autenticación

## 🔐 Autenticación

- Token JWT almacenado en `localStorage`
- Interceptor de Axios para agregar token automáticamente
- Redirección a login en caso de token inválido
- Componente `ProtectedRoute` para rutas privadas

## 🎨 Atomic Design

### Atoms (Átomos)
Componentes básicos que no pueden descomponerse:
- Button, Input, Card

### Molecules (Moléculas)
Combinación de átomos:
- LoginForm, CompanyCard

### Organisms (Organismos)
Componentes complejos con lógica:
- Navbar, Footer, CompanyList

### Templates (Plantillas)
Estructura de páginas:
- MainLayout

### Pages (Páginas)
Páginas completas:
- LoginPage, CompaniesPage

## 🌐 API

El frontend consume la API REST del backend:

- `POST /api/v1/auth/login` - Autenticación
- `GET /api/v1/companies` - Listar empresas

La URL base se configura mediante `REACT_APP_API_URL`.

## 📝 Próximos Pasos

- Agregar vista de detalle de empresa
- Implementar gestión de productos
- Agregar vista de inventario
- Mejorar manejo de errores
- Agregar loading states
- Implementar paginación

## 🧪 Testing

```bash
npm test
```

## 🏗️ Build

```bash
npm run build
```
