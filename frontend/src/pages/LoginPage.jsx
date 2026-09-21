import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api/client';

export default function LoginPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!form.email.trim() || !form.password.trim()) {
      setError('Please enter both email and password.');
      return;
    }

    setLoading(true);
    try {
      const res = await api.login({
        email: form.email.trim(),
        password: form.password,
      });

      sessionStorage.setItem('userId', res.user_id);
      sessionStorage.setItem('userName', res.name);
      sessionStorage.setItem('userEmail', res.email);

      navigate('/dashboard');
    } catch (err) {
      if (err.status === 401) {
        setError('Invalid email or password. Please try again.');
      } else {
        setError(err.detail || 'Sign-in failed. Please verify your connection.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center">
      <div className="card">
        <h1 className="page-title">Welcome Back</h1>
        <p className="page-subtitle">Sign in to your Credit Assistant dashboard</p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              className="form-input"
              name="email"
              type="email"
              placeholder="roshani@example.com"
              value={form.email}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              className="form-input"
              name="password"
              type="password"
              placeholder="Your password"
              value={form.password}
              onChange={handleChange}
              disabled={loading}
              required
            />
          </div>

          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <p className="link-text">
          Don&apos;t have an account yet? <Link to="/register">Create one here</Link>
        </p>
      </div>
    </div>
  );
}
