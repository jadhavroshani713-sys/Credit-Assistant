import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="hero-section">
      <div className="hero-title">
        <span>CREDIT </span>
        <span className="hero-accent">ASSISTANT</span>
      </div>
      <p className="hero-sub">
        AI-powered financial health analytics. Track your credit score, calculate
        utilization & DTI, and receive actionable insights powered by Google Gemini.
      </p>
      <div className="hero-btns">
        <Link to="/register" className="hero-btn hero-btn-primary">
          Get Started Free
        </Link>
        <Link to="/login" className="hero-btn hero-btn-outline">
          Sign In
        </Link>
      </div>
      <div className="hero-features">
        {[
          { icon: '📊', label: 'Credit Analytics' },
          { icon: '🤖', label: 'Gemini AI Insights' },
          { icon: '📈', label: 'Score History' },
          { icon: '🔒', label: 'Secure & Private' },
        ].map((item) => (
          <div key={item.label} className="hero-feature">
            <div className="hero-feature-icon">{item.icon}</div>
            <div className="hero-feature-label">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
