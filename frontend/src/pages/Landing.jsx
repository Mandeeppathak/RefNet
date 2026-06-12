// src/pages/Landing.jsx
import { Link } from 'react-router-dom';
import { ShieldCheck, Zap, Users, TrendingUp, ArrowRight, Star } from 'lucide-react';

const STATS = [
  { value: '100+', label: 'Jobs Scraped Daily' },
  { value: '0', label: 'Cold DMs Required' },
  { value: '100%', label: 'Skill-Based Matching' },
];

const HOW = [
  { icon: '📄', title: 'Upload Your Resume', desc: 'Our AI parses your skills, experience, and education into a verified profile.' },
  { icon: '🎯', title: 'Get Matched', desc: 'Semantic AI matches you to real jobs based on meaning — not just keywords.' },
  { icon: '🔍', title: 'See Your Gaps', desc: 'Know exactly what\'s missing and get a specific action plan to fix it.' },
  { icon: '🤝', title: 'Anonymous Referral', desc: 'Referrers see only your skills. No name, no photo, no bias. Just merit.' },
];

const PROBLEMS = [
  { emoji: '😤', problem: 'Sending 100 applications with zero replies', solution: 'Get matched to jobs where your skills actually fit' },
  { emoji: '😰', problem: 'Awkward cold DMs to strangers for referrals', solution: 'Anonymous skill-based matching — no cold messaging' },
  { emoji: '😔', problem: 'Rejected without knowing why', solution: 'Exact gap analysis and actionable improvement plan' },
  { emoji: '😡', problem: 'Referral requests leading to harassment', solution: 'Identity hidden until referral is accepted' },
];

export default function Landing() {
  return (
    <div className="page">

      {/* Hero */}
      <section style={{
        background: 'linear-gradient(135deg, #F5F4FF 0%, #EEEDFF 50%, #F0EEFF 100%)',
        padding: '80px 24px 100px',
        textAlign: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: -100, left: '50%', transform: 'translateX(-50%)',
          width: 600, height: 600, borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(91,79,232,0.08) 0%, transparent 70%)',
          pointerEvents: 'none',
        }} />

        <div className="container" style={{ position: 'relative' }}>
          <div className="badge badge-purple fade-up" style={{ marginBottom: 20, fontSize: 13 }}>
            <Star size={12} /> The referral system is broken. We fixed it.
          </div>

          <h1 className="fade-up" style={{
            fontSize: 'clamp(36px, 6vw, 68px)',
            letterSpacing: '-1.5px', marginBottom: 20,
            animationDelay: '0.1s',
          }}>
            Get referred on<br />
            <span style={{ color: 'var(--accent)' }}>skills, not connections</span>
          </h1>

          <p className="fade-up" style={{
            fontSize: 18, color: 'var(--ink-soft)', maxWidth: 560,
            margin: '0 auto 36px', lineHeight: 1.7,
            animationDelay: '0.2s',
          }}>
            RefNet matches candidates to referrers anonymously — your name and photo stay
            hidden until a referral is accepted. No cold DMs. No bias. Just your work.
          </p>

          <div className="fade-up" style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap', animationDelay: '0.3s' }}>
            <Link to="/register" className="btn btn-primary btn-lg">
              Find Referrals Free <ArrowRight size={18} />
            </Link>
            <Link to="/register?role=referrer" className="btn btn-outline btn-lg">
              Become a Referrer
            </Link>
          </div>

          {/* Stats */}
          <div style={{
            display: 'flex', gap: 40, justifyContent: 'center',
            marginTop: 56, flexWrap: 'wrap',
          }}>
            {STATS.map(s => (
              <div key={s.label} className="fade-up">
                <div style={{ fontFamily: 'var(--font-display)', fontSize: 32, fontWeight: 800, color: 'var(--accent)' }}>
                  {s.value}
                </div>
                <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problem → Solution */}
      <section style={{ padding: '80px 24px', background: 'var(--surface)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div className="badge badge-red" style={{ marginBottom: 12 }}>The Problem</div>
            <h2 style={{ fontSize: 'clamp(24px,4vw,40px)', letterSpacing: '-0.5px' }}>
              Job hunting is broken for most people
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
            {PROBLEMS.map(p => (
              <div key={p.problem} className="card" style={{ borderLeft: '3px solid var(--accent)' }}>
                <div style={{ fontSize: 28, marginBottom: 12 }}>{p.emoji}</div>
                <div style={{ fontSize: 14, color: 'var(--red)', marginBottom: 8, fontWeight: 600 }}>
                  ✗ {p.problem}
                </div>
                <div style={{ fontSize: 14, color: 'var(--green)', fontWeight: 500 }}>
                  ✓ {p.solution}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section style={{ padding: '80px 24px', background: 'var(--surface-2)' }}>
        <div className="container">
          <div style={{ textAlign: 'center', marginBottom: 48 }}>
            <div className="badge badge-purple" style={{ marginBottom: 12 }}>How It Works</div>
            <h2 style={{ fontSize: 'clamp(24px,4vw,40px)', letterSpacing: '-0.5px' }}>
              Four steps to your next job
            </h2>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px,1fr))', gap: 24 }}>
            {HOW.map((h, i) => (
              <div key={h.title} className="card" style={{ textAlign: 'center', position: 'relative' }}>
                <div style={{
                  position: 'absolute', top: -1, left: -1,
                  width: 28, height: 28, background: 'var(--accent)',
                  borderRadius: '12px 0 8px 0', color: 'white',
                  fontSize: 12, fontWeight: 700,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: 'var(--font-display)',
                }}>{i + 1}</div>
                <div style={{ fontSize: 36, marginBottom: 12 }}>{h.icon}</div>
                <h3 style={{ fontSize: 16, marginBottom: 8 }}>{h.title}</h3>
                <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6 }}>{h.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Why different */}
      <section style={{ padding: '80px 24px' }}>
        <div className="container">
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 48, alignItems: 'center' }}>
            <div>
              <div className="badge badge-purple" style={{ marginBottom: 16 }}>Why RefNet</div>
              <h2 style={{ fontSize: 'clamp(24px,4vw,36px)', marginBottom: 20, letterSpacing: '-0.5px' }}>
                LinkedIn rewards popularity.<br />
                <span style={{ color: 'var(--accent)' }}>We reward skill.</span>
              </h2>
              <p style={{ color: 'var(--ink-soft)', lineHeight: 1.8, marginBottom: 24 }}>
                If you went to a tier-2 college, switched careers, or just don't have 5,000
                LinkedIn connections — the referral system was never built for you. RefNet was.
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {[
                  { icon: <ShieldCheck size={18} />, text: 'Anonymous until referral is accepted' },
                  { icon: <Zap size={18} />, text: 'AI gap analysis with specific action plan' },
                  { icon: <Users size={18} />, text: 'Real referrers at real companies' },
                  { icon: <TrendingUp size={18} />, text: 'Referrer reputation scores — accountability built in' },
                ].map(f => (
                  <div key={f.text} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{
                      width: 36, height: 36, borderRadius: 10,
                      background: 'var(--surface-3)', display: 'flex',
                      alignItems: 'center', justifyContent: 'center',
                      color: 'var(--accent)', flexShrink: 0,
                    }}>{f.icon}</div>
                    <span style={{ fontSize: 15 }}>{f.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div style={{
              background: 'linear-gradient(135deg, var(--surface-2), var(--surface-3))',
              borderRadius: 24, padding: 32,
              border: '1.5px solid var(--border)',
            }}>
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 13, color: 'var(--ink-muted)', marginBottom: 8 }}>
                  REFERRER SEES THIS — NOT YOUR NAME
                </div>
                <div className="card" style={{ padding: 16 }}>
                  <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                    <div className="score-ring" style={{ width: 48, height: 48, fontSize: 13 }}>78%</div>
                    <div>
                      <div style={{ fontWeight: 600, fontSize: 15 }}>Backend Engineer — Razorpay</div>
                      <div style={{ fontSize: 13, color: 'var(--ink-muted)', marginTop: 4 }}>
                        Python • FastAPI • PostgreSQL • Docker
                      </div>
                    </div>
                  </div>
                  <div style={{
                    marginTop: 12, padding: '10px 14px',
                    background: 'var(--surface-2)', borderRadius: 8,
                    fontSize: 13, color: 'var(--ink-soft)', fontStyle: 'italic',
                  }}>
                    "I've built production REST APIs and managed PostgreSQL at scale — would love a chance to contribute to Razorpay's payment infrastructure."
                  </div>
                  <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                    <button className="btn btn-success" style={{ flex: 1, padding: '8px 0', fontSize: 13 }}>✅ Refer</button>
                    <button className="btn btn-ghost" style={{ flex: 1, padding: '8px 0', fontSize: 13 }}>Pass</button>
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 12, color: 'var(--ink-muted)', textAlign: 'center' }}>
                🔒 Name, photo, and gender revealed only after referral is accepted
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{
        padding: '80px 24px', textAlign: 'center',
        background: 'var(--accent)',
      }}>
        <div className="container">
          <h2 style={{ fontSize: 'clamp(24px,4vw,40px)', color: 'white', marginBottom: 16 }}>
            Your next job shouldn't depend on who you know
          </h2>
          <p style={{ color: 'rgba(255,255,255,0.8)', marginBottom: 32, fontSize: 18 }}>
            Join thousands getting referred on merit.
          </p>
          <Link to="/register" className="btn btn-lg" style={{
            background: 'white', color: 'var(--accent)',
          }}>
            Start for Free <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ padding: '32px 24px', borderTop: '1.5px solid var(--border)', textAlign: 'center' }}>
        <div style={{ fontSize: 13, color: 'var(--ink-muted)' }}>
          © 2026 RefNet — Skills over connections, always.
        </div>
      </footer>
    </div>
  );
}
