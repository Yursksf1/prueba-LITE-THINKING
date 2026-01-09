import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login/', { email, password });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
  
  getCurrentUser: () => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('access_token');
  }
};

export const companyService = {
  getAll: async () => {
    const response = await api.get('/companies/');
    return response.data;
  },
  
  getByNit: async (nit) => {
    const response = await api.get(`/companies/${nit}/`);
    return response.data;
  },
  
  create: async (companyData) => {
    const response = await api.post('/companies/', companyData);
    return response.data;
  },
  
  update: async (nit, companyData) => {
    const response = await api.put(`/companies/${nit}/`, companyData);
    return response.data;
  },
  
  delete: async (nit) => {
    const response = await api.delete(`/companies/${nit}/`);
    return response.data;
  }
};

export const productService = {
  getByCompany: async (nit) => {
    const response = await api.get(`/companies/${nit}/products/`);
    return response.data;
  },
  
  create: async (nit, productData) => {
    const response = await api.post(`/companies/${nit}/products/`, productData);
    return response.data;
  }
};

export const inventoryService = {
  getByCompany: async (nit) => {
    const response = await api.get(`/companies/${nit}/inventory/`);
    return response.data;
  },
  
  create: async (nit, inventoryData) => {
    const response = await api.post(`/companies/${nit}/inventory/`, inventoryData);
    return response.data;
  },
  
    downloadPdf: async (nit, includeAIRecommendations = false) => {
      const response = await api.get(`/companies/${nit}/inventory/pdf/`, {
        responseType: 'blob',
        params: { include_ai_recommendations: includeAIRecommendations }
      });
      return response.data;
    },
  
    sendEmail: async (nit, email, includeAIRecommendations = false) => {
      const response = await api.post(`/companies/${nit}/inventory/send-email/`, {
        email,
        company_nit: nit,
        include_ai_recommendations: includeAIRecommendations
      });
      return response.data;
    }
};

export default api;
