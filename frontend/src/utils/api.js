const API_BASE = import.meta.env.VITE_API_URL || '/api';

async function request(path, options = {}) {
  const url = `${API_BASE}${path}`;
  const config = {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  };

  if (config.body && typeof config.body === 'object' && !(config.body instanceof FormData)) {
    config.body = JSON.stringify(config.body);
  }

  if (config.body instanceof FormData) {
    delete config.headers['Content-Type'];
  }

  const response = await fetch(url, config);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

export const api = {
  upload: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/upload/', { method: 'POST', body: formData });
  },

  getSession: (sessionId) => request(`/upload/session/${sessionId}`),
  deleteSession: (sessionId) => request(`/upload/session/${sessionId}`, { method: 'DELETE' }),

  getSummary: (sessionId) => request(`/analytics/summary/${sessionId}`),
  cleanData: (sessionId) => request(`/analytics/clean/${sessionId}`, { method: 'POST' }),
  describeData: (sessionId) => request(`/analytics/describe/${sessionId}`),
  getColumns: (sessionId) => request(`/analytics/columns/${sessionId}`),
  getGpuStatus: () => request('/analytics/gpu-status'),

  getInsights: (sessionId) => request(`/insights/${sessionId}`),
  getTrends: (sessionId) => request(`/insights/trends/${sessionId}`),

  askQuestion: (sessionId, message, history = []) =>
    request(`/chat/ask/${sessionId}`, {
      method: 'POST',
      body: { message, conversation_history: history },
    }),

  trainModel: (sessionId, target) => request(`/predictions/train/${sessionId}?target=${encodeURIComponent(target)}`),
  forecast: (sessionId, target, periods = 5) =>
    request(`/predictions/forecast/${sessionId}?target=${encodeURIComponent(target)}&periods=${periods}`),
  detectAnomalies: (sessionId, column, threshold = 2.0) =>
    request(`/predictions/anomalies/${sessionId}?column=${encodeURIComponent(column)}&threshold=${threshold}`),

  getDashboard: (sessionId) => request(`/dashboard/${sessionId}`),
  getChart: (sessionId, chartType, xCol, yCol) => {
    let url = `/dashboard/chart/${sessionId}?chart_type=${chartType}&x_col=${encodeURIComponent(xCol)}`;
    if (yCol) url += `&y_col=${encodeURIComponent(yCol)}`;
    return request(url);
  },
  getKpis: (sessionId) => request(`/dashboard/kpis/${sessionId}`),

  getAlerts: (sessionId) => request(`/alerts/${sessionId}`),
  getRankings: (sessionId) => request(`/alerts/rankings/${sessionId}`),

  getReport: (sessionId) => request(`/reports/summary/${sessionId}`),
  getTextReport: (sessionId) => request(`/reports/text/${sessionId}`),
  getQuality: (sessionId) => request(`/reports/quality/${sessionId}`),
};
