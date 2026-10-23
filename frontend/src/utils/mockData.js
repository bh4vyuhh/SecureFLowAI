/**
 * SecureFlow AI - Mock Data & Chart Definitions
 * ==============================================================================
 * All data shapes are aligned with Dashboard.jsx, AuditLogsView.jsx, and the
 * FastAPI /api/v1/soc/incidents response schema.
 */

// ── 24-Hour Timeline for Dashboard AreaChart (totalScanned vs blocked) ──────
export const timelineData = [
  { time: '00:00', totalScanned: 310, blocked: 4 },
  { time: '01:00', totalScanned: 280, blocked: 2 },
  { time: '02:00', totalScanned: 240, blocked: 1 },
  { time: '03:00', totalScanned: 195, blocked: 0 },
  { time: '04:00', totalScanned: 210, blocked: 1 },
  { time: '05:00', totalScanned: 290, blocked: 3 },
  { time: '06:00', totalScanned: 520, blocked: 7 },
  { time: '07:00', totalScanned: 840, blocked: 12 },
  { time: '08:00', totalScanned: 1240, blocked: 18 },
  { time: '09:00', totalScanned: 1580, blocked: 24 },
  { time: '10:00', totalScanned: 1820, blocked: 31 },
  { time: '11:00', totalScanned: 1950, blocked: 28 },
  { time: '12:00', totalScanned: 2100, blocked: 35 },
  { time: '13:00', totalScanned: 1980, blocked: 22 },
  { time: '14:00', totalScanned: 2210, blocked: 41 },
  { time: '15:00', totalScanned: 2050, blocked: 37 },
  { time: '16:00', totalScanned: 1890, blocked: 29 },
  { time: '17:00', totalScanned: 1640, blocked: 19 },
  { time: '18:00', totalScanned: 1320, blocked: 14 },
  { time: '19:00', totalScanned: 980, blocked: 9 },
  { time: '20:00', totalScanned: 760, blocked: 6 },
  { time: '21:00', totalScanned: 620, blocked: 5 },
  { time: '22:00', totalScanned: 490, blocked: 4 },
  { time: '23:00', totalScanned: 380, blocked: 3 },
];

// ── Departmental Risk Index for Dashboard BarChart ───────────────────────────
export const departmentRiskData = [
  { name: 'Investment Banking',   risk: 88 },
  { name: 'Treasury & Liquidity', risk: 76 },
  { name: 'Retail Banking',       risk: 62 },
  { name: 'Wealth Management',    risk: 54 },
  { name: 'Trade Finance',        risk: 43 },
  { name: 'Compliance & Legal',   risk: 31 },
  { name: 'IT & DevOps',          risk: 58 },
];

// ── Sensitive Entity Breakdown for Dashboard PieChart ────────────────────────
export const entityBreakdownData = [
  { name: 'Credit Cards',    count: 234, color: '#ef4444' },
  { name: 'IBAN / SWIFT',    count: 187, color: '#f59e0b' },
  { name: 'US SSN',          count: 142, color: '#8b5cf6' },
  { name: 'API Keys',        count: 98,  color: '#3b82f6' },
  { name: 'Private Keys',    count: 61,  color: '#ec4899' },
  { name: 'ABA Routing',     count: 53,  color: '#10b981' },
];

// ── Initial Audit Logs (matches /api/v1/soc/incidents schema) ────────────────
export const initialLogs = [
  {
    id: 'evt-9a1b2c3d',
    timestamp: new Date(Date.now() - 4 * 60000).toISOString(),
    client_id: 'CHROME_EXTENSION',
    user_id: 'j.smith@bankcorp.internal',
    department: 'Investment Banking',
    destination_domain: 'pastebin.com',
    source_action: 'browser_paste',
    classification_tier: 'RESTRICTED',
    risk_score: 96,
    enforcement_action: 'BLOCK',
    payload_sha256: 'a3f8c1d4e2b9074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8',
    entity_counts: { CREDIT_CARD: 1, US_SSN: 1 },
    status: 'OPEN',
  },
  {
    id: 'evt-4d5e6f7a',
    timestamp: new Date(Date.now() - 14 * 60000).toISOString(),
    client_id: 'DESKTOP_AGENT',
    user_id: 'treasury@bankcorp.internal',
    department: 'Treasury & Liquidity',
    destination_domain: 'clipboard://local',
    source_action: 'clipboard_copy',
    classification_tier: 'CONFIDENTIAL',
    risk_score: 72,
    enforcement_action: 'MASK',
    payload_sha256: 'b4c9d2e5f6a1074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f9b0',
    entity_counts: { IBAN: 1, ABA_ROUTING: 1 },
    status: 'RESOLVED',
  },
  {
    id: 'evt-8b9c0d1e',
    timestamp: new Date(Date.now() - 28 * 60000).toISOString(),
    client_id: 'EMAIL_GATEWAY',
    user_id: 'advisor@partner-bank.com',
    department: 'Retail Banking',
    destination_domain: 'external_contractor@gmail.com',
    source_action: 'email_inbound',
    classification_tier: 'RESTRICTED',
    risk_score: 88,
    enforcement_action: 'BLOCK',
    payload_sha256: 'c5d0e3f4a7b2074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f0c1',
    entity_counts: { US_SSN: 1, CREDIT_CARD: 1, PERSON: 2 },
    status: 'OPEN',
  },
  {
    id: 'evt-2e3f4a5b',
    timestamp: new Date(Date.now() - 45 * 60000).toISOString(),
    client_id: 'DESKTOP_AGENT',
    user_id: 'p.nguyen@bankcorp.internal',
    department: 'Wealth Management',
    destination_domain: 'portal.internal.bank.com',
    source_action: 'file_upload',
    classification_tier: 'SAFE',
    risk_score: 18,
    enforcement_action: 'ALLOW',
    payload_sha256: 'd6e1f2a3b4c5074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f1d2',
    entity_counts: { PERSON: 3 },
    status: 'RESOLVED',
  },
  {
    id: 'evt-6c7d8e9f',
    timestamp: new Date(Date.now() - 75 * 60000).toISOString(),
    client_id: 'DESKTOP_AGENT',
    user_id: 'devops@bankcorp.internal',
    department: 'IT & DevOps',
    destination_domain: 'downloads://local',
    source_action: 'filesystem_watch',
    classification_tier: 'RESTRICTED',
    risk_score: 94,
    enforcement_action: 'BLOCK',
    payload_sha256: 'e7f2a3b4c5d6074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f2e3',
    entity_counts: { API_KEY: 1, PRIVATE_KEY: 1 },
    status: 'OPEN',
  },
  {
    id: 'evt-0a1b2c3d',
    timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
    client_id: 'CHROME_EXTENSION',
    user_id: 'm.chen@bankcorp.internal',
    department: 'Compliance & Legal',
    destination_domain: 'teams.microsoft.com',
    source_action: 'browser_paste',
    classification_tier: 'SAFE',
    risk_score: 8,
    enforcement_action: 'ALLOW',
    payload_sha256: 'f8a3b4c5d6e7074f5c6a7d8e9f0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f3f4',
    entity_counts: {},
    status: 'RESOLVED',
  },
];

// ── Copilot Chat Knowledge Base ──────────────────────────────────────────────
export const chatAnswers = [
  {
    keywords: ['credit card', 'pci', 'luhn', 'visa'],
    response:
      'SecureFlow AI implements ISO/IEC 7812 Luhn (MOD-10) checksum evaluation for credit/debit cards. When sensitive PANs are intercepted on unauthorized web domains or clipboards, transfer is blocked and flagged in real-time.',
  },
  {
    keywords: ['encryption', 'aes', 'cipher'],
    response:
      'Data flagged as Confidential or Highly Confidential is protected using AES-256-GCM envelope encryption. Reversible HMAC-SHA256 tokens replace original plaintext entities.',
  },
  {
    keywords: ['slack', 'webhook', 'notifications'],
    response:
      'DLP violations can trigger automated Slack webhook notifications and browser system notifications whenever an incident score exceeds the configured risk threshold (e.g. > 75).',
  },
  {
    keywords: ['pii masking', 'mask', 'redact'],
    response:
      'PII masking uses reverse-offset interval replacement. Customer names, emails, cards, and SSNs are replaced with sanitized placeholders such as [CARD_****9182] or [REDACTED SSN].',
  },
  {
    keywords: ['classifier model', 'tfidf', 'distilbert', 'transformer'],
    response:
      'The classification layer utilizes a hybrid pipeline: deterministic mathematical checksums (Cards, IBAN, SSN), contextual NER, and an INT8 quantized Transformer model with 256-token sliding window.',
  },
  {
    keywords: ['iban', 'swift', 'bank', 'routing'],
    response:
      'IBAN detection follows ISO 13616 structure validation (country code + check digits + BBAN). ABA routing numbers are validated using the MOD-10 9-digit checksum to avoid false positives.',
  },
  {
    keywords: ['block', 'policy', 'threshold', 'action'],
    response:
      'Enforcement actions: BLOCK (risk ≥ 80 or critical PII detected), MASK/ENCRYPT (45 ≤ risk < 80), ALLOW (risk < 45, no critical entities). All thresholds are configurable in the Policy Manager.',
  },
];

// ── Legacy sparkline/dot data (kept for backward compat) ────────────────────
export const sparklineDataCustomer = [
  { name: '1', line1: 20, line2: 12 },
  { name: '2', line1: 24, line2: 18 },
  { name: '3', line1: 35, line2: 15 },
  { name: '4', line1: 28, line2: 24 },
  { name: '5', line1: 42, line2: 20 },
  { name: '6', line1: 38, line2: 28 },
  { name: '7', line1: 50, line2: 22 },
  { name: '8', line1: 45, line2: 30 },
  { name: '9', line1: 58, line2: 25 },
  { name: '10', line1: 64, line2: 32 },
];

export const dotGridData = Array.from({ length: 70 }, (_, i) => ({
  id: `dot-${i}`,
  status: i % 11 === 0 ? 'alert' : i % 5 === 0 ? 'high' : i % 2 === 0 ? 'low' : 'idle',
}));

export const resourcePillData = [
  { id: 'p1', labelVal: '24%', resources: 45, valid: 35 },
  { id: 'p2', labelVal: '68%', resources: 82, valid: 70 },
  { id: 'p3', labelVal: '41%', resources: 55, valid: 40 },
  { id: 'p4', labelVal: '89%', resources: 94, valid: 85 },
  { id: 'p5', labelVal: '33%', resources: 40, valid: 25 },
  { id: 'p6', labelVal: '76%', resources: 88, valid: 65 },
  { id: 'p7', labelVal: '52%', resources: 60, valid: 50 },
  { id: 'p8', labelVal: '95%', resources: 98, valid: 90 },
  { id: 'p9', labelVal: '18%', resources: 28, valid: 20 },
  { id: 'p10', labelVal: '81%', resources: 90, valid: 75 },
];

export const timelineTracksData = [
  {
    date: 'Mon, 18',
    items: [
      { id: 1, platform: 'Chrome Extension', count: '14 hits', start: 3, end: 12, color: '#8df85f' },
      { id: 2, platform: 'Desktop Clipboard', count: '6 alerts', start: 16, end: 26, color: '#f38933' }
    ]
  },
  {
    date: 'Tue, 19',
    items: [
      { id: 3, platform: 'Web Ingestion', count: '29 cleared', start: 1, end: 18, color: '#ffffff' },
      { id: 4, platform: 'Local File Agent', count: '8 hits', start: 21, end: 29, color: '#8df85f' }
    ]
  },
  {
    date: 'Wed, 20',
    items: [
      { id: 5, platform: 'Clipboard Copy', count: '12 alerts', start: 8, end: 22, color: '#f38933' }
    ]
  },
  {
    date: 'Today',
    items: [
      { id: 6, platform: 'Active Gateway', count: 'Live', start: 12, end: 28, color: '#8df85f' }
    ]
  }
];

