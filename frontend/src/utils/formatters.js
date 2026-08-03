export const formatRelativeTime = (iso) => {
  if (!iso) return 'just now';
  const now = new Date();
  const then = new Date(iso);
  const diff = Math.floor((now - then) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return then.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

export const formatDateTime = (iso) => {
  if (!iso) return '';
  return new Date(iso).toLocaleString('en-US', {
    month: 'short', day: 'numeric', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

export const formatNumber = (n) =>
  n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);

export const getRiskColor = (score) => {
  if (score >= 80) return 'var(--danger)';
  if (score >= 50) return 'var(--warning)';
  return 'var(--success)';
};

export const getRiskLabel = (score) => {
  if (score >= 80) return 'Critical';
  if (score >= 50) return 'Medium';
  return 'Safe';
};

export const getLabelClass = (label) => {
  const map = {
    'Public': 'success',
    'Internal': 'info',
    'Confidential': 'warning',
    'Highly Confidential': 'danger'
  };
  return map[label] || 'default';
};

export const getFileExtension = (name) => name?.split('.').pop()?.toLowerCase() || '';
