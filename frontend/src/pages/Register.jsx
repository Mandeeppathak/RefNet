// src/pages/Register.jsx
import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

export default function Register() {
  const [params] = useSearchParams();
  const [form, setForm] = useState({
    full_name: '', email: '', password: '',
    role: params.get('role') || 'candidate',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = e => setForm(f => ({ ...f, [e.target.name]: e.target.value }));

  const submit = async e => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      const { data } = await api.post('/auth/register', form);
      login({ full_name: form.full_name, email: form.email, role: form.role, user_id: data.user_id }, data.access_token);
      navigate(form.role === 'candidate' ? '/dashboard' : '/referrer');
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally { setLoading(false); }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-2)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24 }}>
      <div className="card fade-up" style={{ width: '100%', maxWidth: 440 }}>
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{
            width: 48, height: 48, background: 'var(--accent)', borderRadius: 12,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            color: 'white', fontWeight: 800, fontSize: 22, margin: '0 auto 16px',
            fontFamily: 'var(--font-display)',
          }}>R</div>
          <h2 style={{ fontSize: 24, marginBottom: 6 }}>Create your account</h2>
          <p style={{ color: 'var(--ink-muted)', fontSize: 14 }}>Skills over connections — always</p>
        </div>

        {/* Role toggle */}
        <div style={{
          display: 'grid', gridTemplateColumns: '1fr 1fr',
          background: 'var(--surface-3)', borderRadius: 10, padding: 4, marginBottom: 24,
        }}>
          {['candidate', 'referrer'].map(r => (
            <button key={r} type="button"
              onClick={() => setForm(f => ({ ...f, role: r }))}
              style={{
                padding: '8px 0', borderRadius: 8, border: 'none', fontSize: 14, fontWeight: 600,
                background: form.role === r ? 'white' : 'transparent',
                color: form.role === r ? 'var(--accent)' : 'var(--ink-muted)',
                boxShadow: form.role === r ? 'var(--shadow)' : 'none',
                transition: 'all 0.2s', textTransform: 'capitalize',
              }}
            >{r}</button>
          ))}
        </div>

        <form onSubmit={submit}>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input name="full_name" placeholder="Rahul Sharma" value={form.full_name} onChange={handle} required />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input name="email" type="email" placeholder="rahul@email.com" value={form.email} onChange={handle} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input name="password" type="password" placeholder="Min 8 characters" value={form.password} onChange={handle} required minLength={8} />
          </div>

          {form.role === 'referrer' && (
            <div style={{
              background: 'var(--surface-2)', border: '1.5px solid var(--border)',
              borderRadius: 10, padding: 14, marginBottom: 18, fontSize: 13, color: 'var(--ink-soft)',
            }}>
              💼 As a referrer, you'll see anonymous skill profiles and can choose who to refer at your company.
            </div>
          )}

          {error && <div className="form-error" style={{ marginBottom: 14, fontSize: 13 }}>⚠️ {error}</div>}

          <button type="submit" className="btn btn-primary" style={{ width: '100%', justifyContent: 'center', padding: '12px 0' }} disabled={loading}>
            {loading ? <><div className="spinner" />Creating account...</> : 'Create Account'}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: 20, fontSize: 14, color: 'var(--ink-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent)', fontWeight: 600 }}>Sign in</Link>
        </div>
      </div>
    </div>
  );
}
