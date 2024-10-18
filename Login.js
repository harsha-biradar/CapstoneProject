import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Login() {
  const [role, setRole] = useState('');
  const navigate = useNavigate();

  const handleLogin = () => {
    if (role === 'Doctor') navigate('/doctor');
    else if (role === 'Researcher') navigate('/researcher');
    else alert('Please select a valid role.');
  };

  return (
    <div className="login">
      <h2>Login</h2>
      <select onChange={(e) => setRole(e.target.value)}>
        <option value="">Select Role</option>
        <option value="Doctor">Doctor</option>
        <option value="Researcher">Researcher</option>
      </select>
      <button onClick={handleLogin}>Login</button>
    </div>
  );
}

export default Login;
