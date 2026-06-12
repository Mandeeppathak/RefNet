// src/pages/ReferrerDashboard.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Briefcase, Star, Users, CheckCircle, XCircle, Plus } from 'lucide-react';

export default function ReferrerDashboard() {
  const { user } = useAuth();
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState({ total: 0, accepted: 0, pending: 0 });
  const [jdForm, setJdForm] = useState({ jd_id: '', jd_text: '' });
  const [posting, setPosting] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [msg, setMsg] = useState('');

  const postJD = async e => {
    e.preventDefault();
    setPosting(true); setMsg('');
    try {
      await api.post('/jd', jdForm);
      setMsg('✅ Job posted successfully!');
      setJdForm({ jd_id: '', jd_text: '' });
      setShowForm(false);
    } catch (err) {
      setMsg('⚠️ ' + (err.response?.data?.detail || 'Failed to post job'));
    } finally { setPosting(false); }
  };

  const handleReferral = async (id, action) => {
    try {
      await api.get(`/referral/${action}/${id}`);
      setRequests(r => r.map(req =>
        req.id === id ? { ...req, status: action === 'accept' ? 'accepted' : 'rejected' } : req
      ));
    } catch { alert('Action failed'); }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-2)' }}>
      <div className="container" style={{ padding: '32px 24px' }}>

        <div style={{ marginBottom: 32, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <h1 style={{ fontSize: 28, marginBottom: 4 }}>Referrer Dashboard</h1>
            <p style={{ color: 'var(--ink-muted)' }}>Help candidates get opportunities — anonymously</p>
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm(s => !s)}>
            <Plus size={16} /> Post a Job
          </button>
        </div>

        {/* Stats */}
        <div className="grid-3" style={{ marginBottom: 28 }}>
          {[
            { icon: <Users size={20} />, label: 'Requests', value: stats.total, color: 'var(--accent)' },
            { icon: <CheckCircle size={20} />, label: 'Referred', value: stats.accepted, color: 'var(--green)' },
            { icon: <Star size={20} />, label: 'Reputation', value: '⭐ New', color: 'var(--yellow)' },
          ].map(s => (
            <div key={s.label} className="card" style={{ display: 'flex', gap: 14, alignItems: 'center' }}>
              <div style={{
                width: 44, height: 44, borderRadius: 10,
                background: 'var(--surface-3)', display: 'flex',
                alignItems: 'center', justifyContent: 'center', color: s.color,
              }}>{s.icon}</div>
              <div>
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 22, fontWeight: 700 }}>{s.value}</div>
                <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>{s.label}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Post JD form */}
        {showForm && (
          <div className="card fade-up" style={{ marginBottom: 28 }}>
            <h3 style={{ marginBottom: 20, display: 'flex', alignItems: 'center', gap: 8 }}>
              <Briefcase size={18} color="var(--accent)" /> Post a Job for Referrals
            </h3>
            <form onSubmit={postJD}>
              <div className="form-group">
                <label className="form-label">Job ID (unique slug)</label>
                <input placeholder="e.g. razorpay_backend_2026" value={jdForm.jd_id}
                  onChange={e => setJdForm(f => ({ ...f, jd_id: e.target.value }))} required />
              </div>
              <div className="form-group">
                <label className="form-label">Job Description</label>
                <textarea rows={6} placeholder="Paste the full job description here..."
                  value={jdForm.jd_text}
                  onChange={e => setJdForm(f => ({ ...f, jd_text: e.target.value }))}
                  required style={{ resize: 'vertical' }} />
              </div>
              {msg && <div style={{ fontSize: 13, marginBottom: 12, color: msg.startsWith('✅') ? 'var(--green)' : 'var(--red)' }}>{msg}</div>}
              <div style={{ display: 'flex', gap: 10 }}>
                <button type="submit" className="btn btn-primary" disabled={posting}>
                  {posting ? <><div className="spinner" />Posting...</> : 'Post Job'}
                </button>
                <button type="button" className="btn btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          </div>
        )}

        {/* Referral requests */}
        <div>
          <h2 style={{ fontSize: 20, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Users size={20} color="var(--accent)" /> Incoming Referral Requests
          </h2>

          {requests.length === 0 ? (
            <div className="card" style={{ textAlign: 'center', padding: 48 }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🤝</div>
              <h3 style={{ marginBottom: 8 }}>No requests yet</h3>
              <p style={{ color: 'var(--ink-muted)', fontSize: 14 }}>
                Post a job above and candidates will be automatically matched to you.
                You'll get an email when someone wants a referral.
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {requests.map(req => (
                <div key={req.id} className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', gap: 10, alignItems: 'center', marginBottom: 8 }}>
                        <div className="score-ring" style={{ width: 48, height: 48, fontSize: 13 }}>
                          {Math.round(req.match_score)}%
                        </div>
                        <div>
                          <div style={{ fontWeight: 700 }}>{req.job_title}</div>
                          <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>Anonymous Candidate</div>
                        </div>
                        <span className={`badge badge-${req.status === 'accepted' ? 'green' : req.status === 'rejected' ? 'red' : 'yellow'}`}>
                          {req.status}
                        </span>
                      </div>
                      <div style={{ fontSize: 13, color: 'var(--ink-soft)', marginBottom: 10 }}>
                        <strong>Skills:</strong> {req.candidate_skills}
                      </div>
                      {req.referral_message && (
                        <div style={{
                          background: 'var(--surface-2)', borderLeft: '3px solid var(--accent)',
                          padding: '10px 14px', borderRadius: '0 8px 8px 0',
                          fontSize: 13, color: 'var(--ink-soft)', fontStyle: 'italic',
                        }}>"{req.referral_message}"</div>
                      )}
                    </div>
                    {req.status === 'pending' && (
                      <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                        <button className="btn btn-success" style={{ padding: '8px 16px' }}
                          onClick={() => handleReferral(req.id, 'accept')}>
                          <CheckCircle size={14} /> Refer
                        </button>
                        <button className="btn btn-ghost" style={{ padding: '8px 16px' }}
                          onClick={() => handleReferral(req.id, 'decline')}>
                          <XCircle size={14} /> Pass
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
