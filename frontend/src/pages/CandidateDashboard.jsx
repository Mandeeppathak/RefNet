// src/pages/CandidateDashboard.jsx
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import { Upload, Zap, TrendingUp, CheckCircle, Clock, XCircle } from 'lucide-react';

function MatchCard({ match, onAnalyze }) {
  const score = match.match_score;
  const color = score >= 60 ? 'var(--green)' : score >= 35 ? 'var(--yellow)' : 'var(--red)';
  return (
    <div className="card" style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
      <div className="score-ring" style={{ borderColor: color, color }}>
        {score > 0 ? `${Math.round(score)}%` : 'N/A'}
      </div>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontWeight: 700, fontSize: 16 }}>{match.job_title}</div>
        <div style={{ color: 'var(--ink-muted)', fontSize: 14, marginBottom: 10 }}>{match.company}</div>
        <button className="btn btn-outline" style={{ padding: '6px 14px', fontSize: 13 }}
          onClick={() => onAnalyze(match)}>
          <Zap size={14} /> Analyze Gap
        </button>
      </div>
    </div>
  );
}

function GapPanel({ analysis, message, onClose }) {
  if (!analysis) return null;
  const verdict = analysis.overall_verdict;
  const verdictColor = verdict === 'Strong Match' ? 'var(--green)' : verdict === 'Good Match' ? 'var(--accent)' : verdict === 'Partial Match' ? 'var(--yellow)' : 'var(--red)';

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      zIndex: 200, padding: 24,
    }} onClick={onClose}>
      <div className="card fade-up" style={{ maxWidth: 580, width: '100%', maxHeight: '90vh', overflowY: 'auto' }}
        onClick={e => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
          <h3 style={{ fontSize: 20 }}>Gap Analysis</h3>
          <button className="btn btn-ghost" style={{ padding: '4px 8px' }} onClick={onClose}>✕</button>
        </div>

        <div style={{ display: 'flex', gap: 12, alignItems: 'center', marginBottom: 20 }}>
          <div style={{
            background: verdictColor, color: 'white', padding: '6px 16px',
            borderRadius: 20, fontWeight: 700, fontSize: 14,
          }}>{verdict}</div>
          <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>
            AI Match: {analysis.match_percentage}%
          </div>
        </div>

        {analysis.strong_points?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8, color: 'var(--green)' }}>✅ Your Strengths</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {analysis.strong_points.map(s => (
                <span key={s} className="badge badge-green">{s}</span>
              ))}
            </div>
          </div>
        )}

        {analysis.missing_critical?.length > 0 && (
          <div style={{ marginBottom: 16 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8, color: 'var(--red)' }}>⚠️ Critical Gaps</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
              {analysis.missing_critical.map(s => (
                <span key={s} className="badge badge-red">{s}</span>
              ))}
            </div>
          </div>
        )}

        {analysis.action_plan?.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 10 }}>📋 Action Plan</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {analysis.action_plan.map((a, i) => (
                <div key={i} style={{
                  background: 'var(--surface-2)', borderRadius: 8, padding: '10px 14px',
                  display: 'flex', gap: 10, alignItems: 'flex-start',
                }}>
                  <span className={`badge badge-${a.priority === 'High' ? 'red' : a.priority === 'Medium' ? 'yellow' : 'green'}`}
                    style={{ flexShrink: 0 }}>{a.priority}</span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: 14 }}>{a.action}</div>
                    <div style={{ fontSize: 12, color: 'var(--ink-muted)', marginTop: 2 }}>
                      {a.timeline} · {a.resource}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {message && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 8 }}>✉️ Your Referral Message</div>
            <div style={{
              background: 'var(--surface-3)', borderLeft: '3px solid var(--accent)',
              borderRadius: '0 8px 8px 0', padding: 14,
              fontSize: 14, lineHeight: 1.7, color: 'var(--ink-soft)', fontStyle: 'italic',
            }}>{message}</div>
          </div>
        )}

        <div style={{
          background: 'var(--surface-2)', borderRadius: 8, padding: 12,
          fontSize: 13, color: 'var(--ink-soft)', textAlign: 'center',
        }}>
          🔒 {analysis.referral_readiness}
        </div>
      </div>
    </div>
  );
}

export default function CandidateDashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [gapData, setGapData] = useState(null);
  const [error, setError] = useState('');

  const uploadResume = async e => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true); setError('');
    try {
      const fd = new FormData();
      fd.append('file', file);
      const { data } = await api.post('/resume', fd);
      setProfile(data.parsed_profile);
      // fetch matches
      const m = await api.get(`/match/${data.profile_id}`);
      setMatches(m.data.matches || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally { setUploading(false); }
  };

  const analyzeGap = async match => {
    setAnalyzing(true);
    try {
      const { data } = await api.post('/analyze', {
        candidate_id: match.jd_id,
        jd_id: match.jd_id,
      });
      setGapData({ analysis: data.gap_analysis, message: data.referral_message });
    } catch {
      setError('Analysis failed — try again');
    } finally { setAnalyzing(false); }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--surface-2)' }}>
      <div className="container" style={{ padding: '32px 24px' }}>

        {/* Header */}
        <div style={{ marginBottom: 32 }}>
          <h1 style={{ fontSize: 28, marginBottom: 4 }}>
            Hey {user?.full_name?.split(' ')[0]} 👋
          </h1>
          <p style={{ color: 'var(--ink-muted)' }}>Your skill-based job matching dashboard</p>
        </div>

        {/* Upload */}
        {!profile && (
          <div className="card fade-up" style={{
            textAlign: 'center', padding: 48,
            border: '2px dashed var(--border)', background: 'var(--surface)',
            marginBottom: 28,
          }}>
            <Upload size={40} color="var(--accent)" style={{ marginBottom: 16 }} />
            <h3 style={{ marginBottom: 8 }}>Upload your resume to get started</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: 14, marginBottom: 20 }}>
              PDF only · Our AI parses your skills instantly
            </p>
            <label className="btn btn-primary" style={{ cursor: 'pointer' }}>
              {uploading ? <><div className="spinner" />Parsing resume...</> : '📄 Upload Resume (PDF)'}
              <input type="file" accept=".pdf" onChange={uploadResume} style={{ display: 'none' }} disabled={uploading} />
            </label>
            {error && <div className="form-error" style={{ marginTop: 12 }}>{error}</div>}
          </div>
        )}

        {/* Profile summary */}
        {profile && (
          <div className="card fade-up" style={{ marginBottom: 28 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                  <h3 style={{ fontSize: 20 }}>{profile.name}</h3>
                  <span className="badge badge-green">✅ Profile Active</span>
                </div>
                <div style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 12 }}>
                  {profile.total_years_experience} years exp · {profile.education?.[0]?.degree}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                  {profile.skills?.slice(0, 8).map(s => (
                    <span key={s} className="badge badge-purple">{s}</span>
                  ))}
                  {profile.skills?.length > 8 && (
                    <span className="badge badge-purple">+{profile.skills.length - 8} more</span>
                  )}
                </div>
              </div>
              <label className="btn btn-outline" style={{ cursor: 'pointer', flexShrink: 0 }}>
                <Upload size={14} /> Update Resume
                <input type="file" accept=".pdf" onChange={uploadResume} style={{ display: 'none' }} />
              </label>
            </div>
          </div>
        )}

        {/* Matches */}
        {matches.length > 0 && (
          <div className="fade-up">
            <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16 }}>
              <TrendingUp size={20} color="var(--accent)" />
              <h2 style={{ fontSize: 20 }}>Your Top Matches</h2>
              <span className="badge badge-purple">{matches.length} jobs</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px,1fr))', gap: 16 }}>
              {matches.map(m => (
                <MatchCard key={m.jd_id} match={m} onAnalyze={analyzeGap} />
              ))}
            </div>
          </div>
        )}

        {/* Empty matches */}
        {profile && matches.length === 0 && (
          <div className="card" style={{ textAlign: 'center', padding: 40 }}>
            <Clock size={32} color="var(--ink-muted)" style={{ marginBottom: 12 }} />
            <h3 style={{ marginBottom: 8 }}>Finding your matches...</h3>
            <p style={{ color: 'var(--ink-muted)', fontSize: 14 }}>
              Our scraper adds new jobs every 24 hours. Check back soon.
            </p>
          </div>
        )}

        {analyzing && (
          <div style={{
            position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 200,
          }}>
            <div className="card" style={{ textAlign: 'center', padding: 32 }}>
              <div className="spinner" style={{ width: 32, height: 32, margin: '0 auto 16px' }} />
              <p style={{ fontWeight: 600 }}>Analyzing your gap...</p>
            </div>
          </div>
        )}

        {gapData && (
          <GapPanel
            analysis={gapData.analysis}
            message={gapData.message}
            onClose={() => setGapData(null)}
          />
        )}
      </div>
    </div>
  );
}
