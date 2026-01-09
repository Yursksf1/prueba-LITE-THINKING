import './Footer.css';

function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-container">
        <p>&copy; {currentYear} Lite Thinking. Todos los derechos reservados.</p>
      </div>
    </footer>
  );
}

export default Footer;
