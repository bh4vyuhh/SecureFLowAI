/**
 * SecureFlow AI - Banking SOC Mock Data & Initial State
 * ==============================================================================
 * Comprehensive realistic banking DLP dataset for offline and development mode.
 */

export const initialLogs = [
  {
    id: 'inc-9842',
    timestamp: new Date(Date.now() - 4 * 60000).toISOString(),
    client_id: 'desktop-daemon-lon-04',
    user_id: 'alice.vance@bankcorp.com',
    department: 'Investment Banking',
    destination_domain: 'pastebin.com',
    source_action: 'clipboard',
    classification_tier: 'RESTRICTED',
    risk_score: 96,
    enforcement_action: 'BLOCK',
    payload_sha256: '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08',
    entity_counts: { CREDIT_CARD: 2, US_SSN: 1 },
    status: 'OPEN',
    details: 'Attempted exfiltration of unencrypted card credentials and customer SSN to public paste repository.',
  },
  {
    id: 'inc-9841',
    timestamp: new Date(Date.now() - 14 * 60000).toISOString(),
    client_id: 'chrome-ext-ny-12',
    user_id: 'david.chen@bankcorp.com',
    department: 'Treasury & Liquidity',
    destination_domain: 'api.openai.com',
    source_action: 'prompt_injection',
    classification_tier: 'CONFIDENTIAL',
    risk_score: 68,
    enforcement_action: 'MASK',
    payload_sha256: '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8',
    entity_counts: { IBAN: 2 },
    status: 'RESOLVED',
    details: 'Treasury transaction memo containing internal EU IBANs submitted to public LLM endpoint; auto-masked with HMAC tokens.',
  },
  {
    id: 'inc-9840',
    timestamp: new Date(Date.now() - 32 * 60000).toISOString(),
    client_id: 'desktop-daemon-sg-08',
    user_id: 'priya.sharma@bankcorp.com',
    department: 'Wealth Management',
    destination_domain: 'drive.google.com',
    source_action: 'file_upload',
    classification_tier: 'RESTRICTED',
    risk_score: 91,
    enforcement_action: 'BLOCK',
    payload_sha256: '4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a',
    entity_counts: { CREDIT_CARD: 4, ABA_ROUTING: 2 },
    status: 'OPEN',
    details: 'Unencrypted client account portfolio spreadsheet upload blocked per PCI-DSS policy.',
  },
  {
    id: 'inc-9839',
    timestamp: new Date(Date.now() - 58 * 60000).toISOString(),
    client_id: 'email-connector-ch-01',
    user_id: 'lucas.meier@bankcorp.com',
    department: 'Commercial Lending',
    destination_domain: 'partner.auditors.com',
    source_action: 'email',
    classification_tier: 'CONFIDENTIAL',
    risk_score: 52,
    enforcement_action: 'MASK',
    payload_sha256: 'ef2d127de37b942baad06145e54b0c619a1f22327b2ebbcfbec78f5564afe39d',
    entity_counts: { PERSON: 3, ORG: 2 },
    status: 'RESOLVED',
    details: 'Quarterly syndicated loan agreements routed through gateway; customer personal identities masked.',
  },
  {
    id: 'inc-9838',
    timestamp: new Date(Date.now() - 110 * 60000).toISOString(),
    client_id: 'desktop-daemon-lon-02',
    user_id: 'sarah.jenkins@bankcorp.com',
    department: 'Retail Banking',
    destination_domain: 'portal.internal.bank.com',
    source_action: 'clipboard',
    classification_tier: 'SAFE',
    risk_score: 8,
    enforcement_action: 'ALLOW',
    payload_sha256: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    entity_counts: {},
    status: 'RESOLVED',
    details: 'Internal staff training announcement copied to authorized internal intranet portal.',
  },
];

export const timelineData = [
  { time: '00:00', totalScanned: 1420, blocked: 12, masked: 45 },
  { time: '04:00', totalScanned: 980, blocked: 4, masked: 22 },
  { time: '08:00', totalScanned: 4320, blocked: 38, masked: 120 },
  { time: '12:00', totalScanned: 6890, blocked: 64, masked: 210 },
  { time: '16:00', totalScanned: 7450, blocked: 82, masked: 245 },
  { time: '20:00', totalScanned: 3120, blocked: 26, masked: 88 },
];

export const departmentRiskData = [
  { name: 'Investment Banking', risk: 84, incidents: 42, score: 'High' },
  { name: 'Treasury & FX', risk: 72, incidents: 31, score: 'Moderate' },
  { name: 'Wealth Management', risk: 65, incidents: 27, score: 'Moderate' },
  { name: 'Retail Banking', risk: 38, incidents: 14, score: 'Low' },
  { name: 'IT Infrastructure', risk: 24, incidents: 8, score: 'Low' },
];

export const entityBreakdownData = [
  { name: 'PCI Credit Cards', count: 184, color: '#ef4444' },
  { name: 'IBAN / Routing', count: 142, color: '#f59e0b' },
  { name: 'US SSN', count: 96, color: '#dc2626' },
  { name: 'API / Private Keys', count: 68, color: '#8b5cf6' },
  { name: 'Names & PII', count: 320, color: '#3b82f6' },
];

export const chatAnswers = [
  {
    keywords: ['credit card', 'pci', 'luhn', 'visa'],
    response:
      'SecureFlow AI applies zero-false-positive mathematical validation (ISO/IEC 7812 Luhn Algorithm) to distinguish valid customer credit cards from arbitrary 16-digit invoice numbers. When detected on untrusted domains, a strict BLOCK policy is enforced.',
  },
  {
    keywords: ['iban', 'mod-97', 'sepa'],
    response:
      'IBAN detection utilizes ISO 7064 MOD-97-10 check digit verification across 70+ national banking formats. Transits to authorized counterparties are pseudonymized via reversible HMAC tokens.',
  },
  {
    keywords: ['copilot', 'explain', 'summary'],
    response:
      'The Analyst Copilot provides automated explainability for SOC alerts, evaluating sender role, destination trust, and entity sensitivity to recommend appropriate containment actions.',
  },
];
