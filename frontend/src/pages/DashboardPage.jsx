import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from 'recharts';
import { api } from '../api/client';

const PIE_COLORS = ['#38bdf8', '#334155'];

function getScoreCategory(score) {
  if (!score) return { label: 'Unknown', className: 'score-fair', color: 'var(--text-muted)' };
  if (score >= 750) return { label: 'Excellent', className: 'score-good', color: 'var(--accent-green)' };
  if (score >= 680) return { label: 'Good', className: 'score-good', color: 'var(--accent-green)' };
  if (score >= 600) return { label: 'Fair', className: 'score-fair', color: 'var(--accent-yellow)' };
  return { label: 'Poor', className: 'score-poor', color: 'var(--accent-red)' };
}

function MetricCard({ label, value, unit }) {
  return (
    <div className="metric-card">
      <div className="metric-label">{label}</div>
      <div className="metric-value">
        {value !== null && value !== undefined ? value : '—'}
        {unit && <span className="metric-unit"> {unit}</span>}
      </div>
    </div>
  );
}

function renderRecommendations(data) {
  if (!data) return null;

  if (typeof data === 'string') {
    return <p className="ai-assessment">{data}</p>;
  }

  return (
    <div>
      {data.overall_assessment && (
        <div className="ai-block">
          <div className="ai-block-title">Overall Credit Assessment</div>
          <p className="ai-assessment">{data.overall_assessment}</p>
        </div>
      )}

      {Array.isArray(data.critical_issues) && data.critical_issues.length > 0 && (
        <div className="ai-block">
          <div className="ai-block-title">Key Risk Factors & Observations</div>
          <ul className="ai-list ai-list-issues">
            {data.critical_issues.map((issue, idx) => (
              <li key={idx}>{issue}</li>
            ))}
          </ul>
        </div>
      )}

      {Array.isArray(data.recommendations) && data.recommendations.length > 0 && (
        <div className="ai-block">
          <div className="ai-block-title">Actionable Steps to Improve</div>
          <ul className="ai-list">
            {data.recommendations.map((rec, idx) => (
              <li key={idx}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {data.improvement_guidance && (
        <div className="ai-block">
          <div className="ai-block-title">Expected Timeline & Improvement Path</div>
          <p className="ai-assessment">{data.improvement_guidance}</p>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const navigate = useNavigate();
  const userId = sessionStorage.getItem('userId');
  const userName = sessionStorage.getItem('userName');

  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [aiData, setAiData] = useState(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState('');

  const fetchDashboard = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    setError('');
    try {
      const data = await api.getDashboard(userId);
      setDashboard(data);
    } catch (err) {
      setError(err.detail || 'Failed to load dashboard data. Please verify the server is running.');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (!userId) {
      navigate('/login');
      return;
    }
    let isMounted = true;
    api.getDashboard(userId)
      .then((data) => {
        if (isMounted) {
          setDashboard(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        if (isMounted) {
          setError(err.detail || 'Failed to load dashboard data. Please verify the server is running.');
          setLoading(false);
        }
      });
    return () => {
      isMounted = false;
    };
  }, [userId, navigate]);

  const handleGetRecommendations = async () => {
    setAiLoading(true);
    setAiError('');
    try {
      const res = await api.getRecommendations(userId);
      setAiData(res);
    } catch (err) {
      setAiError(err.detail || 'Unable to fetch AI recommendations right now.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleLogout = () => {
    sessionStorage.clear();
    navigate('/');
  };

  if (loading) {
    return (
      <>
        <Navbar userName={userName} onLogout={handleLogout} />
        <div className="loading-center">
          <div className="spinner" />
          <p>Retrieving your financial dashboard...</p>
        </div>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar userName={userName} onLogout={handleLogout} />
        <div className="dashboard-layout">
          <div className="error-box" style={{ maxWidth: 540, margin: '40px auto' }}>
            {error}
            <div style={{ marginTop: 16 }}>
              <button className="btn btn-secondary btn-sm" onClick={fetchDashboard}>
                Retry
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  const profile = dashboard?.profile;
  const history = dashboard?.score_history || [];
  const scoreCat = getScoreCategory(profile?.credit_score);

  // Pie chart calculation
  const limit = profile?.credit_limit || 0;
  const used = profile?.credit_used || 0;
  const available = Math.max(0, limit - used);

  const pieData = limit > 0 ? [
    { name: 'Credit Used', value: used },
    { name: 'Available Credit', value: available },
  ] : [];

  // Line chart calculation (score history)
  const lineData = history.map((item, index) => ({
    label: `Check #${index + 1}`,
    score: item.new_score,
  }));

  return (
    <>
      <Navbar userName={userName} onLogout={handleLogout} />

      <div className="dashboard-layout">
        <div className="section-header">
          <div>
            <h1 style={{ fontSize: '1.6rem', fontWeight: 800 }}>Financial Health Dashboard</h1>
            <p style={{ color: 'var(--text-secondary)', marginTop: 4 }}>
              Account: {dashboard?.user?.name} ({dashboard?.user?.email})
            </p>
          </div>

          <div style={{ display: 'flex', gap: 10 }}>
            <button className="btn btn-secondary btn-sm" onClick={() => navigate('/onboarding')}>
              {dashboard?.has_financial_data ? 'Update Financial Data' : 'Submit Financial Data'}
            </button>
          </div>
        </div>

        {/* Empty state if user has no profile */}
        {!dashboard?.has_financial_data && (
          <div className="card" style={{ maxWidth: '100%', textAlign: 'center', padding: '56px 24px', marginBottom: 32 }}>
            <div style={{ fontSize: '3rem', marginBottom: 12 }}>💳</div>
            <h2 style={{ marginBottom: 8 }}>No Financial Profile Recorded</h2>
            <p style={{ color: 'var(--text-secondary)', marginBottom: 24, maxWidth: 500, margin: '0 auto 24px' }}>
              Submit your income, debt, and credit metrics to unlock complete analytics and AI credit counseling.
            </p>
            <button className="btn btn-primary" style={{ width: 'auto', margin: '0 auto' }} onClick={() => navigate('/onboarding')}>
              Enter Financial Metrics
            </button>
          </div>
        )}

        {/* Metrics Grid */}
        {profile && (
          <>
            <div className="metrics-grid">
              <div className="metric-card" style={{ flexDirection: 'row', alignItems: 'center', gap: 16 }}>
                <div className={`score-badge ${scoreCat.className}`}>
                  {profile.credit_score}
                </div>
                <div>
                  <div className="metric-label">Credit Score</div>
                  <div style={{ color: scoreCat.color, fontWeight: 700, fontSize: '1.1rem' }}>
                    {scoreCat.label}
                  </div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.78rem', marginTop: 2 }}>
                    Out of 900
                  </div>
                </div>
              </div>

              <MetricCard
                label="Credit Utilization"
                value={profile.utilization !== null ? profile.utilization.toFixed(1) : '—'}
                unit="%"
              />

              <MetricCard
                label="Debt-to-Income (DTI)"
                value={profile.debt_to_income !== null ? profile.debt_to_income.toFixed(1) : '—'}
                unit="%"
              />

              <MetricCard
                label="Missed Payments"
                value={profile.missed_payments}
              />

              <MetricCard
                label="Active Loans"
                value={profile.active_loans}
              />

              <MetricCard
                label="Monthly Income"
                value={profile.monthly_salary ? `₹${profile.monthly_salary.toLocaleString('en-IN')}` : '—'}
              />

              <MetricCard
                label="Monthly Expenses"
                value={profile.monthly_expenses ? `₹${profile.monthly_expenses.toLocaleString('en-IN')}` : '—'}
              />
            </div>

            {/* Charts Grid */}
            <div className="charts-grid">
              <div className="chart-card">
                <div className="chart-title">Credit Limit vs. Utilization</div>
                {pieData.length === 0 ? (
                  <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                    No credit limit recorded.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={230}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={85}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {pieData.map((_, index) => (
                          <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(val) => `₹${Number(val).toLocaleString('en-IN')}`}
                        contentStyle={{
                          backgroundColor: 'var(--bg-card)',
                          borderColor: 'var(--border)',
                          borderRadius: 8,
                          color: 'var(--text-primary)',
                        }}
                      />
                      <Legend
                        wrapperStyle={{ paddingTop: 10, fontSize: '0.85rem' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>

              <div className="chart-card">
                <div className="chart-title">Credit Score Trend</div>
                {lineData.length === 0 ? (
                  <div style={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                    No score history records yet.
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={230}>
                    <LineChart data={lineData} margin={{ top: 10, right: 20, left: -10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="label" tick={{ fill: 'var(--text-muted)', fontSize: 12 }} />
                      <YAxis
                        domain={[300, 900]}
                        tick={{ fill: 'var(--text-muted)', fontSize: 12 }}
                      />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'var(--bg-card)',
                          borderColor: 'var(--border)',
                          borderRadius: 8,
                          color: 'var(--text-primary)',
                        }}
                      />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#38bdf8"
                        strokeWidth={3}
                        dot={{ fill: '#38bdf8', r: 5 }}
                        activeDot={{ r: 7 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                )}
              </div>
            </div>
          </>
        )}

        {/* AI Recommendations Section */}
        {dashboard?.has_financial_data && (
          <div className="ai-section">
            <div className="ai-title">
              <span>🤖</span> Gemini AI Credit Recommendations
            </div>
            <p className="ai-subtitle">
              Personalized credit counseling and actionable guidance based on your financial metrics and RBI credit guidelines.
            </p>

            {!aiData && !aiLoading && (
              <button
                className="btn btn-primary"
                style={{ width: 'auto' }}
                onClick={handleGetRecommendations}
                disabled={aiLoading}
              >
                Get AI Recommendations
              </button>
            )}

            {aiLoading && (
              <div className="loading-center" style={{ padding: '36px 0' }}>
                <div className="spinner" />
                <p style={{ marginTop: 8 }}>Analyzing financial indicators with Google Gemini...</p>
              </div>
            )}

            {aiError && (
              <div style={{ marginTop: 16 }}>
                <div className="error-box">{aiError}</div>
                <button className="btn btn-secondary btn-sm" onClick={handleGetRecommendations}>
                  Retry AI Analysis
                </button>
              </div>
            )}

            {aiData && (
              <div style={{ marginTop: 24 }}>
                {renderRecommendations(aiData)}
                <div style={{ marginTop: 24, display: 'flex', gap: 12 }}>
                  <button className="btn btn-secondary btn-sm" onClick={handleGetRecommendations} disabled={aiLoading}>
                    Refresh AI Insights
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}

function Navbar({ userName, onLogout }) {
  const navigate = useNavigate();

  return (
    <header className="navbar">
      <div
        className="navbar-brand"
        onClick={() => navigate('/dashboard')}
        style={{ cursor: 'pointer' }}
      >
        <span>CREDIT ASSISTANT</span>
      </div>

      <div className="navbar-actions">
        {userName && (
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 500 }}>
            {userName}
          </span>
        )}
        <button className="btn btn-secondary btn-sm" onClick={onLogout}>
          Sign Out
        </button>
      </div>
    </header>
  );
}
