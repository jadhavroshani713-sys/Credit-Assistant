const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request(method, path, body = null) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body) {
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch {
    throw { status: 0, detail: 'Unable to connect to the backend server. Please verify the backend is running.' };
  }

  let data;
  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    let detail = 'An unexpected error occurred';
    if (typeof data.detail === 'string') {
      detail = data.detail;
    } else if (Array.isArray(data.detail) && data.detail.length > 0) {
      detail = data.detail.map(d => d.msg || d).join(', ');
    }
    throw { status: response.status, detail };
  }

  return data;
}

export const api = {
  health: () => request('GET', '/health'),
  register: (payload) => request('POST', '/register', payload),
  login: (payload) => request('POST', '/login', payload),
  submitFinancial: (payload) => request('POST', '/financial-data', payload),
  getDashboard: (userId) => request('GET', `/dashboard/${userId}`),
  getRecommendations: (userId) => request('GET', `/recommendations/${userId}`),
  getFinancialReport: (userId) => request('GET', `/report/${userId}`),
  getPdfReportUrl: (userId) => `${BASE_URL}/report/pdf/${userId}`,
};

