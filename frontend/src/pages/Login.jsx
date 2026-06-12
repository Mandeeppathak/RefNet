// src/pages/Login.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

export default function Login() {
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async e => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      // login uses form data format
      const params = new URLSearchParams();
      params.append('username', form.email);
      params.append('password', form.password);
      const { data } = await api.post('/auth/login', params, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      login({ full_name: data.full_name || form.email, email: form.email, role: data.role, user_id: data.user_id }, data.access_token);
      navigate(data.role === 'candidate' ? '/dashboard' : '/referrer');
    } catch (err) {
      setError('Invalid email or password');
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div className="card fade-up" style={{ width: '100%', maxWidth: 400 }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{
            width: 48, height: 48, background: 'var(--accent)', borderRadius: 12,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white', fontWeight: 800, fontSize: 22, margin: '0 auto 16px',
            fontFamily: 'var(--font-display)',
          }}>R</div>
          <h2 style={{ fontSize: 24, marginBottom: 6 }}>Welcome back</h2>
          <p style={{ color: 'var(--ink-muted)', fontSize: 14 }}>Sign in to your RefNet account</p>
        </div>

        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input name="email" type="email" placeholder="rahul@email.com" value={form.email} onChange={handle} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input name="password" type="password" placeholder="Your password" value={form.password} onChange={handle} required />
          </div>

          {error && <div className="form-error" style={{ marginBottom: 14, fontSize: 13 }}>⚠️ {error}</div>}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px 0' }} disabled={loading}>
            {loading ? <><div className="spinner" />Signing in...</> : 'Sign In'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: 'var(--ink-muted)' }}>
          No account? <Link to="/register" style={{ color: 'var(--accent)', fontWeight: 600 }}>Create one free</Link>
        </div>
      </div>
    </div>
  );
}
