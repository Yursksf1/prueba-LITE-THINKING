import Navbar from '../organisms/Navbar';
import Footer from '../organisms/Footer';
import './MainLayout.css';

function MainLayout({ children }) {
  return (
    <div className="main-layout">
      <Navbar />
      <main className="main-content">
        <div className="content-container">
          {children}
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default MainLayout;
