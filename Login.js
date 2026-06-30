import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const mockUsers = [
  { username: 'doctor1', password: 'pass123', role: 'doctor' },
  { username: 'researcher1', password: 'pass456', role: 'researcher' },
];

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();

    // Check if the user exists with the correct role and credentials
    const user = mockUsers.find(
      (u) => u.username === username && u.password === password
    );

    if (user) {
      console.log(`Login successful! Role: ${user.role}`);
      // Redirect based on user role
      if (user.role === 'doctor') {
        navigate('/doctor-dashboard');
      } else if (user.role === 'researcher') {
        navigate('/researcher-dashboard');
      } else {
        setError('Invalid user role. Please contact support.');
      }
    } else {
      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        /><br></br>
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        /><br></br>
        <button type="submit">Login</button>
      </form>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
};

export default Login;

