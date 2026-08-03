const range = (len) => Array.from({ length: len }, (_, i) => i);
const secureRand = (max) => Math.floor(Math.random() * max);

const documentTypes = ['xlsx', 'pdf', 'docx', 'csv', 'zip', 'json', 'py'];
const userDirectory = [
  { user: 'm.vasquez', dept: 'FinOps' },
  { user: 'j.hargreaves', dept: 'Legal' },
  { user: 'a.patel', dept: 'HR' },
  { user: 's.obrien', dept: 'Engineering' },
  { user: 'k.tanaka', dept: 'Sales Ops' },
  { user: 'e.dubois', dept: 'R&D' }
];

const sampleDocuments = [
  'tax_return_draft_2024',
  'api_token_prod_backup',
  'employee_compensation_plan',
  'q3_merger_term_sheet',
  'db_dump_customer_records',
  'compliance_audit_log_v2',
  'confidential_contractor_NDA',
  'auth_handler_revised',
  'financial_projections_final',
  'onboarding_passwords_tmp'
];

const alertPatterns = [
  { title: 'API Key Exposure', severity: 'high', desc: 'Plaintext secret key matching AWS pattern detected in file.' },
  { title: 'PII Leakage Blocked', severity: 'high', desc: 'File contains SSN/Tax ID sequence.' },
  { title: 'Off-Hours Retrieval', severity: 'medium', desc: 'Authorized asset accessed outside scheduled operational hours.' },
  { title: 'High-Volume Sync', severity: 'medium', desc: 'Transfer rate of designated sensitive directory exceeded threshold.' },
  { title: 'Override Warning', severity: 'low', desc: 'Classification tier manually downgraded by authorization holder.' }
];

export const generateEvents = (limit = 80) => {
  return range(limit).map(idx => {
    const rawIndex = secureRand(sampleDocuments.length);
    const typeIndex = secureRand(documentTypes.length);
    const userMeta = userDirectory[secureRand(userDirectory.length)];
    const docName = `${sampleDocuments[rawIndex]}.${documentTypes[typeIndex]}`;
    
    let label = 'Public';
    let risk = secureRand(30) + 5;
    let action = 'log-only';

    if (rawIndex < 3) {
      label = 'Highly Confidential';
      risk = secureRand(20) + 80;
      action = 'auto-encrypt';
    } else if (rawIndex < 7) {
      label = 'Confidential';
      risk = secureRand(30) + 50;
      action = 'redact-pii';
    } else if (rawIndex < 9) {
      label = 'Internal';
      risk = secureRand(25) + 25;
      action = 'log-only';
    }

    const t = new Date();
    t.setHours(t.getHours() - idx * 4);

    return {
      id: `evt-${t.getTime()}-${idx}`,
      fileName: docName,
      label,
      labelColor: label === 'Highly Confidential' ? '#ef4444' : label === 'Confidential' ? '#f59e0b' : label === 'Internal' ? '#38bdf8' : '#10b981',
      riskScore: risk,
      confidence: parseFloat((0.75 + (Math.random() * 0.24)).toFixed(2)),
      source: idx % 3 === 0 ? 'Desktop Agent' : idx % 2 === 0 ? 'Browser Extension' : 'Ingestion Gateway',
      user: userMeta.user,
      department: userMeta.dept,
      timestamp: t.toISOString(),
      action,
      fileSize: `${secureRand(2400) + 50} KB`,
      piiDetected: risk > 45
    };
  });
};

export const EVENTS = generateEvents(80);

export const ALERTS = range(25).map(idx => {
  const pattern = alertPatterns[idx % alertPatterns.length];
  const userMeta = userDirectory[secureRand(userDirectory.length)];
  const docName = `${sampleDocuments[secureRand(sampleDocuments.length)]}.${documentTypes[secureRand(documentTypes.length)]}`;
  const t = new Date();
  t.setHours(t.getHours() - idx * 6);
  
  return {
    id: `alt-${t.getTime()}-${idx}`,
    title: pattern.title,
    severity: pattern.severity,
    desc: pattern.desc,
    riskScore: pattern.severity === 'high' ? secureRand(15) + 81 : pattern.severity === 'medium' ? secureRand(30) + 50 : secureRand(40) + 10,
    user: userMeta.user,
    department: userMeta.dept,
    fileName: docName,
    timestamp: t.toISOString(),
    read: idx > 3,
    resolved: idx > 10
  };
});

export const RISK_TREND = range(14).map(idx => {
  const t = new Date();
  t.setDate(t.getDate() - (13 - idx));
  return {
    date: t.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    avgRisk: secureRand(35) + 30,
    highRiskCount: secureRand(6) + 1,
    totalEvents: secureRand(30) + 15
  };
});

export const CLASSIFICATION_DIST = [
  { name: 'Public', value: 35, fill: '#22C55E' },
  { name: 'Internal', value: 40, fill: '#3B82F6' },
  { name: 'Confidential', value: 18, fill: '#F59E0B' },
  { name: 'Highly Confidential', value: 7, fill: '#EF4444' }
];

export const DEPT_RISK = userDirectory.map(d => ({
  department: d.dept,
  avgRisk: secureRand(45) + 35,
  totalFiles: secureRand(200) + 80,
  violations: secureRand(8)
})).sort((a, b) => b.avgRisk - a.avgRisk);

export const ANOMALY_EVENTS = range(9).map(idx => {
  const severities = ['high', 'medium', 'low'];
  const labels = ['System Secret Leak', 'Bulk Document Sync', 'Unusual Auth Location'];
  return {
    id: `an-${idx}`,
    label: labels[idx % labels.length],
    severity: severities[idx % severities.length],
    dayOffset: parseFloat((0.1 + (idx * 0.09)).toFixed(2))
  };
});

export const STATS = {
  totalDocuments: 2490,
  activeAlerts: ALERTS.filter(a => !a.resolved).length,
  highRiskFiles: EVENTS.filter(e => e.riskScore > 80).length,
  classifiedToday: secureRand(30) + 20,
  encryptedFiles: secureRand(40) + 60,
  avgRiskScore: 38
};

export const AUDIT_LOG = EVENTS.slice(0, 50).map((e, idx) => ({
  id: `aud-${idx}`,
  action: idx % 3 === 0 ? 'Tier Match' : idx % 2 === 0 ? 'Crypto Lock' : 'Gateway Auth',
  actor: e.user,
  resource: e.fileName,
  result: 'SUCCESS',
  ipAddress: `10.150.12.${secureRand(250) + 2}`,
  timestamp: e.timestamp
}));

export const MOCK_USER = {
  id: 'usr-0988',
  name: 'Amy Chen',
  email: 'a.chen@secureflow.corp',
  role: 'Ops Lead',
  department: 'SecOps',
  phone: '+1 (555) 019-2834',
  location: 'Chicago, US',
  joinDate: '2025-10-01T00:00:00.000Z',
  avatarInitials: 'AC',
  permissions: ['read', 'write', 'super-user'],
  lastLogin: new Date().toISOString(),
  twoFactorEnabled: true
};

export const RECENT_DOCUMENTS = [
  { id: 'doc-1', name: 'Q4_Financial_Report.pdf', ext: 'pdf', label: 'Highly Confidential', riskScore: 91, size: '2.4 MB', uploadedBy: 'm.vasquez', uploadedAt: new Date(Date.now() - 1000 * 60 * 15).toISOString() },
  { id: 'doc-2', name: 'employee_roster_oct2025.xlsx', ext: 'xlsx', label: 'Confidential', riskScore: 73, size: '848 KB', uploadedBy: 'a.patel', uploadedAt: new Date(Date.now() - 1000 * 60 * 42).toISOString() },
  { id: 'doc-3', name: 'merger_term_sheet_draft.docx', ext: 'docx', label: 'Highly Confidential', riskScore: 88, size: '1.1 MB', uploadedBy: 'j.hargreaves', uploadedAt: new Date(Date.now() - 1000 * 60 * 90).toISOString() },
  { id: 'doc-4', name: 'api_credentials_prod.json', ext: 'json', label: 'Confidential', riskScore: 82, size: '14 KB', uploadedBy: 's.obrien', uploadedAt: new Date(Date.now() - 1000 * 60 * 135).toISOString() },
  { id: 'doc-5', name: 'sales_pipeline_CRM_export.csv', ext: 'csv', label: 'Internal', riskScore: 44, size: '3.9 MB', uploadedBy: 'k.tanaka', uploadedAt: new Date(Date.now() - 1000 * 60 * 200).toISOString() },
  { id: 'doc-6', name: 'compliance_audit_results.pdf', ext: 'pdf', label: 'Internal', riskScore: 36, size: '560 KB', uploadedBy: 'e.dubois', uploadedAt: new Date(Date.now() - 1000 * 60 * 310).toISOString() },
];

export const AI_RECOMMENDATIONS = [
  {
    id: 'rec-1',
    severity: 'high',
    icon: 'shield-alert',
    title: 'Auto-encrypt 3 unprotected high-risk files',
    description: 'Q4_Financial_Report.pdf, merger_term_sheet_draft.docx, and api_credentials_prod.json are classified Confidential+ but lack AES-256 encryption.',
    actionLabel: 'Encrypt Now',
  },
  {
    id: 'rec-2',
    severity: 'medium',
    icon: 'eye',
    title: 'Review clipboard intercepts from m.vasquez',
    description: '14 clipboard copy events detected in the last 2 hours involving financial document content.',
    actionLabel: 'Review Events',
  },
  {
    id: 'rec-3',
    severity: 'medium',
    icon: 'cpu',
    title: 'Retrain classifier on new document type',
    description: 'Model confidence dropped below 80% for JSON credential files. Retraining with 12 new samples recommended.',
    actionLabel: 'Retrain Model',
  }
];

export const ENCRYPTION_STATS = {
  encrypted: 847,
  unencrypted: 93,
  total: 940,
  lastEncrypted: new Date(Date.now() - 1000 * 60 * 4).toISOString(),
  algorithm: 'AES-256-GCM',
  autoEncryptOn: true,
};

export const BROWSER_EXT_STATS = {
  status: 'connected',
  activeUsers: 24,
  clipboardIntercepts: 187,
  blockedUploads: 12,
  lastEventAt: new Date(Date.now() - 1000 * 33).toISOString(),
  version: '2.4.1',
};

export const SECURITY_SCORE = {
  score: 72,
  trend: '+4 vs last week',
  trendUp: true,
  breakdown: [
    { label: 'Encryption Coverage', value: 90 },
    { label: 'Policy Compliance', value: 84 },
    { label: 'Access Control', value: 76 },
    { label: 'Incident Response', value: 61 },
    { label: 'Data Classification', value: 68 },
  ],
};
