// src/components/Navbar.jsx
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LogOut, User } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 100,
      background: 'rgba(255,255,255,0.92)', backdropFilter: 'blur(12px)',
      borderBottom: '1.5px solid var(--border)', padding: '0 24px',
    }}>
      <div style={{
        maxWidth: 1100, margin: '0 auto',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        height: 60,
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <div style={{
            width: 32, height: 32, background: 'var(--accent)',
            borderRadius: 8, display: 'flex', alignItems: 'center',
            justifyContent: 'center', color: 'white', fontWeight: 800,
            fontFamily: 'var(--font-display)', fontSize: 16,
          }}>R</div>
          <span style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 18 }}>
            RefNet
          </span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {user ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 32, height: 32, borderRadius: '50%',
                  background: 'var(--surface-3)', display: 'flex',
                  alignItems: 'center', justifyContent: 'center',
                }}>
                  <User size={16} color="var(--accent)" />
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600 }}>{user.full_name}</div>
                  <div style={{ fontSize: 11, color: 'var(--ink-muted)', textTransform: 'capitalize' }}>
                    {user.role}
                  </div>
                </div>
              </div>
              <button
                onClick={() => navigate(user.role === 'candidate' ? '/dashboard' : '/referrer')}
                className="btn btn-outline" style={{ padding: '6px 16px' }}
              >Dashboard</button>
              <button onClick={logout} className="btn btn-ghost" style={{ padding: '6px 10px' }}>
                <LogOut size={16} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-ghost">Sign in</Link>
              <Link to="/register" className="btn btn-primary">Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
