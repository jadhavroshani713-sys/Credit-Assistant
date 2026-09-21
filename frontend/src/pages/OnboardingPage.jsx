import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api/client';

const INITIAL_FORM = {
  credit_score: '',
  credit_limit: '',
  credit_used: '',
  missed_payments: '0',
  active_loans: '0',
  monthly_salary: '',
  monthly_expenses: '',
};

export default function OnboardingPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL_FORM);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const userId = sessionStorage.getItem('userId');

  useEffect(() => {
    if (!userId) {
      navigate('/login');
    }
  }, [userId, navigate]);

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const validate = () => {
    const n = (val) => Number(val);

    if (!form.credit_score || isNaN(n(form.credit_score))) {
      return 'Credit score is required.';
    }
    const score = n(form.credit_score);
    if (score < 300 || score > 900) {
      return 'Credit score must be between 300 and 900.';
    }

    if (form.credit_limit === '' || isNaN(n(form.credit_limit)) || n(form.credit_limit) < 0) {
      return 'Credit limit must be 0 or a positive number.';
    }

    if (form.credit_used === '' || isNaN(n(form.credit_used)) || n(form.credit_used) < 0) {
      return 'Credit used must be 0 or a positive number.';
    }

    if (form.missed_payments === '' || isNaN(n(form.missed_payments)) || n(form.missed_payments) < 0) {
      return 'Missed payments must be 0 or a positive integer.';
    }

    if (form.active_loans === '' || isNaN(n(form.active_loans)) || n(form.active_loans) < 0) {
      return 'Active loans must be 0 or a positive integer.';
    }

    if (form.monthly_salary === '' || isNaN(n(form.monthly_salary)) || n(form.monthly_salary) < 0) {
      return 'Monthly salary must be 0 or a positive number.';
    }

    if (form.monthly_expenses === '' || isNaN(n(form.monthly_expenses)) || n(form.monthly_expenses) < 0) {
      return 'Monthly expenses must be 0 or a positive number.';
    }

    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const validationMsg = validate();
    if (validationMsg) {
      setError(validationMsg);
      return;
    }

    setLoading(true);
    try {
      await api.submitFinancial({
        user_id: Number(userId),
        credit_score: Math.round(Number(form.credit_score)),
        credit_limit: parseFloat(form.credit_limit),
        credit_used: parseFloat(form.credit_used),
        missed_payments: Math.round(Number(form.missed_payments)),
        active_loans: Math.round(Number(form.active_loans)),
        monthly_salary: parseFloat(form.monthly_salary),
        monthly_expenses: parseFloat(form.monthly_expenses),
      });

      navigate('/dashboard');
    } catch (err) {
      setError(err.detail || 'Failed to submit financial profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-center" style={{ alignItems: 'flex-start', paddingTop: 40, paddingBottom: 40 }}>
      <div className="card card-wide">
        <h1 className="page-title">Financial Profile</h1>
        <p className="page-subtitle">
          Submit your financial metrics so our AI can calculate utilization, DTI, and personalized credit guidance.
        </p>

        {error && <div className="error-box">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-grid-2">
            <div className="form-group">
              <label className="form-label">
                Credit Score * <span style={{ color: 'var(--text-muted)' }}>(300 – 900)</span>
              </label>
              <input
                className="form-input"
                name="credit_score"
                type="number"
                min="300"
                max="900"
                placeholder="e.g. 720"
                value={form.credit_score}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Monthly Salary * <span style={{ color: 'var(--text-muted)' }}>(₹)</span>
              </label>
              <input
                className="form-input"
                name="monthly_salary"
                type="number"
                min="0"
                placeholder="e.g. 60000"
                value={form.monthly_salary}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Sanctioned Credit Limit * <span style={{ color: 'var(--text-muted)' }}>(₹)</span>
              </label>
              <input
                className="form-input"
                name="credit_limit"
                type="number"
                min="0"
                placeholder="e.g. 100000"
                value={form.credit_limit}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Monthly Expenses * <span style={{ color: 'var(--text-muted)' }}>(₹)</span>
              </label>
              <input
                className="form-input"
                name="monthly_expenses"
                type="number"
                min="0"
                placeholder="e.g. 25000"
                value={form.monthly_expenses}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Total Credit Used * <span style={{ color: 'var(--text-muted)' }}>(₹)</span>
              </label>
              <input
                className="form-input"
                name="credit_used"
                type="number"
                min="0"
                placeholder="e.g. 35000"
                value={form.credit_used}
                onChange={handleChange}
                disabled={loading}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Missed / Overdue Payments <span style={{ color: 'var(--text-muted)' }}>(Count)</span>
              </label>
              <input
                className="form-input"
                name="missed_payments"
                type="number"
                min="0"
                placeholder="0"
                value={form.missed_payments}
                onChange={handleChange}
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label className="form-label">
                Active Loan Accounts <span style={{ color: 'var(--text-muted)' }}>(Count)</span>
              </label>
              <input
                className="form-input"
                name="active_loans"
                type="number"
                min="0"
                placeholder="0"
                value={form.active_loans}
                onChange={handleChange}
                disabled={loading}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: 12, marginTop: 12 }}>
            <button className="btn btn-primary" type="submit" disabled={loading}>
              {loading ? 'Submitting Financial Data...' : 'Save & View Dashboard'}
            </button>
            <button
              className="btn btn-secondary btn-sm"
              type="button"
              onClick={() => navigate('/dashboard')}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
