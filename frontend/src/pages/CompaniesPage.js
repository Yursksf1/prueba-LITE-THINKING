import MainLayout from '../templates/MainLayout';
import CompanyList from '../organisms/CompanyList';
import './CompaniesPage.css';

function CompaniesPage() {
  return (
    <MainLayout>
      <div className="companies-page">
        <h1 className="page-title">Empresas Registradas</h1>
        <p className="page-subtitle">Listado de empresas en el sistema</p>
        <CompanyList />
      </div>
    </MainLayout>
  );
}

export default CompaniesPage;
