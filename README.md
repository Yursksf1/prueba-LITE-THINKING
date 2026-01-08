# Prueba Técnica Lite Thinking – 2026  
**Python · Django · React · PostgreSQL**

Este proyecto corresponde a una prueba técnica cuyo objetivo es demostrar buenas prácticas de desarrollo, diseño de arquitectura, separación de responsabilidades y uso consciente de tecnologías modernas como IA, manteniendo claridad y simplicidad.

---

## 🧠 Visión General de la Arquitectura

El proyecto está diseñado siguiendo principios de **Arquitectura Limpia (Clean Architecture)**, donde las reglas de negocio están completamente desacopladas de frameworks, infraestructura y detalles de implementación.

### Arquitectura de Alto Nivel

```
Frontend (React)
        |
        v
API (Django REST Framework)
        |
        v
Capa de Aplicación (Casos de Uso)
        |
        v
Capa de Dominio (Python puro - Poetry)
        |
        v
Infraestructura (Django ORM, PostgreSQL, Integraciones)
```

### Principios Clave

- El dominio no depende de Django ni de HTTP
- Las dependencias siempre apuntan hacia el dominio
- Las reglas de negocio son independientes de:
  - Frameworks
  - Persistencia
  - APIs externas
- La infraestructura se adapta al dominio, no al contrario

---

## 📦 Estructura del Proyecto

```
.
├── backend/
│   ├── api/                    # Vistas, serializers y permisos (REST)
│   ├── application/            # Casos de uso y orquestación
│   ├── infrastructure/         # Persistencia, autenticación e integraciones
│   ├── config/                 # Configuración de Django
│   └── manage.py
│
├── domain/                     # Paquete independiente del dominio (Poetry)
│   ├── pyproject.toml
│   └── src/domain/
│       ├── entities/
│       ├── services/
│       └── exceptions/
│
├── frontend/
│   └── src/
│       ├── atoms/
│       ├── molecules/
│       ├── organisms/
│       ├── templates/
│       └── pages/
│
├── .github/agents/                     # Agentes de gobernanza del proyecto
│   ├── agent-architecture.md
│   ├── agent-quality.md
│   └── agent-security.md
│
├── docker-compose.yml
└── README.md
```

---

## 🔐 Tipos de Usuario

### Administrador
- Crear, editar y eliminar empresas
- Registrar productos por empresa
- Gestionar el inventario
- Descargar inventario en PDF
- Enviar el PDF del inventario por correo

### Usuario Externo
- Visualizar empresas y productos (solo lectura)

La autenticación utiliza los mecanismos seguros de Django, con contraseñas encriptadas.

---

## 🌐 Endpoints Disponibles

### Autenticación
- `POST /api/auth/login/`  
  Autenticación con correo y contraseña.

---

### Empresas
- `GET /api/companies/`  
  Listar empresas (público).
- `POST /api/companies/`  
  Crear empresa (Administrador).
- `PUT /api/companies/{nit}/`  
  Actualizar empresa (Administrador).
- `DELETE /api/companies/{nit}/`  
  Eliminar empresa (Administrador).

---

### Productos
- `GET /api/products/`  
  Listar productos.
- `POST /api/products/`  
  Crear producto asociado a una empresa (Administrador).

---

### Inventario
- `GET /api/inventory/`  
  Ver inventario por empresa.
- `GET /api/inventory/pdf/`  
  Descargar inventario en PDF.
- `POST /api/inventory/send-pdf/`  
  Enviar el PDF del inventario por correo usando una API externa.

---

## 🤖 Funcionalidad Adicional con IA

El proyecto incluye una funcionalidad asistida por **Inteligencia Artificial** para generar descripciones enriquecidas de productos a partir de características básicas.

### Decisión de Diseño
- La IA se maneja como una **integración externa**
- Es invocada desde la capa de aplicación
- No afecta ni contamina la capa de dominio

Esto permite mantener reglas de negocio determinísticas y fácilmente testeables.

---

## 🧩 Gobernanza y Agentes

El proyecto utiliza **tres agentes principales** para garantizar calidad y coherencia:

- **Architecture Guardian Agent**
- **Quality & Testing Agent**
- **Security & Authentication Agent**
- **Expert backend Agent**
- **Expert frontend Agent**

Se limita intencionalmente el número de agentes para evitar complejidad artificial y fragmentación excesiva, un problema común en enfoques automatizados o guiados por IA.

---

## 🚀 Ejecución del Proyecto con Docker (Recomendado)
1) crear un archivo `.env` en la raíz del proyecto con las variables de entorno necesarias puedes basarte en el archivo `.env.example`
```
# =========================
# DATABASE
# =========================
POSTGRES_DB=lite_db
POSTGRES_USER=lite_user
POSTGRES_PASSWORD=super_password_segura
POSTGRES_HOST=db
POSTGRES_PORT=5432

DATABASE_URL=postgres://lite_user:super_password_segura@db:5432/lite_db

# =========================
# DJANGO
# =========================
DJANGO_SECRET_KEY=django-super-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# =========================
# BACKEND
# =========================
BACKEND_PORT=8000

# =========================
# FRONTEND
# =========================
REACT_APP_API_URL=http://localhost:8000
```

Docker y Docker Compose se utilizan para proporcionar un entorno de desarrollo **rápido, reproducible y consistente**, facilitando el trabajo local y la evaluación del proyecto.

### Requisitos Previos
- Docker
- Docker Compose

---

### Levantar los Servicios

```bash
docker compose up --build
```

Este comando inicia:
- Base de datos PostgreSQL
- Backend en Django
- Frontend en React

---

### Accesos

- Backend (API): `http://localhost:8000/api/`
- Frontend: `http://localhost:3000`

---

### Ejecutar Migraciones

```bash
docker compose exec backend python manage.py migrate
```

---

### Crear Superusuario

```bash
docker compose exec backend python manage.py createsuperuser
```

---

## 🧪 Filosofía de Pruebas

- El dominio se prueba con tests unitarios puros
- Los casos de uso se validan de forma independiente
- Las pruebas priorizan comportamiento, no implementación
- La cobertura es significativa, no forzada

---

## 📌 Notas Finales

- Docker se utiliza como herramienta de productividad, no como complejidad adicional
- Las decisiones arquitectónicas priorizan claridad y mantenibilidad
- La IA se usa como apoyo, no como dependencia central del negocio

> El objetivo del proyecto no es solo que funcione,  
> sino que sea fácil de entender, modificar y escalar.
