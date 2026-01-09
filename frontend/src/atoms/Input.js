import './Input.css';

function Input({ 
  type = 'text', 
  name, 
  value, 
  onChange, 
  placeholder, 
  required = false,
  disabled = false,
  label
}) {
  return (
    <div className="input-wrapper">
      {label && <label htmlFor={name} className="input-label">{label}</label>}
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        className="input-field"
      />
    </div>
  );
}

export default Input;
