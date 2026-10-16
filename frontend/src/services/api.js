/**
 * SecureFlow AI - Admin Platform API & WebSocket Client
 * ==============================================================================
 * Connects the React Admin SOC Dashboard to the DLP Gateway & Copilot services.
 */

import axios from 'axios';

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const WS_URL = API_BASE_URL.replace(/^http/, 'ws') + '/ws/live-threats';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Health & Service Telemetry
  getHealth: async () => {
    const res = await client.get('/health');
    return res.data;
  },

  // Master DLP Scan Contract (Tier 1 & 2)
  scanDLP: async ({
    clientId = 'admin-soc-console',
    userId = 'analyst@bank.com',
    department = 'treasury',
    destinationDomain = 'api.openai.com',
    sourceAction = 'clipboard',
    text = '',
    fileBytesB64 = null,
    fileName = null,
    mode = 'mask',
  }) => {
    const res = await client.post('/api/v1/scan/dlp', {
      client_id: clientId,
      user_id: userId,
      department,
      destination_domain: destinationDomain,
      source_action: sourceAction,
      text,
      file_bytes_b64: fileBytesB64,
      file_name: fileName,
      mode,
    });
    return res.data;
  },

  // File Upload Inspection (.pdf, .docx, .xlsx, .zip, images)
  scanFileUpload: async (file, mode = 'mask') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('mode', mode);
    const res = await client.post('/api/v1/dlp/scan', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // SOC Analytics & Audit
  getIncidents: async (params = { limit: 50 }) => {
    const res = await client.get('/api/v1/soc/incidents', { params });
    return res.data;
  },

  getStats: async () => {
    const res = await client.get('/api/v1/soc/stats');
    return res.data;
  },

  // Analyst Copilot Conversational Assistant (Tier 5)
  chatCopilot: async (query, contextIncidentId = null) => {
    const res = await client.post('/api/v1/soc/copilot/chat', {
      query,
      context_incident_id: contextIncidentId,
    });
    return res.data;
  },

  // Cryptographic Detokenization (Tier 4)
  detokenize: async (token, authorizationKey) => {
    const res = await client.post('/api/v1/crypto/detokenize', {
      token,
      authorization_key: authorizationKey,
    });
    return res.data;
  },

  // Dynamic Bank Policy Management (Tier 3)
  getPolicy: async () => {
    const res = await client.get('/api/v1/policies');
    return res.data;
  },

  updatePolicy: async (policyData) => {
    const res = await client.post('/api/v1/policies', policyData);
    return res.data;
  },

  // WebSocket Live Threat Stream Listener
  connectLiveThreats: (onMessage, onStatusChange) => {
    let ws = null;
    let shouldReconnect = true;

    const connect = () => {
      try {
        onStatusChange?.('CONNECTING');
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
          onStatusChange?.('CONNECTED');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            onMessage?.(data);
          } catch (e) {
            console.warn('Failed parsing WS message:', event.data);
          }
        };

        ws.onerror = (err) => {
          console.warn('WebSocket error:', err);
          onStatusChange?.('ERROR');
        };

        ws.onclose = () => {
          onStatusChange?.('DISCONNECTED');
          if (shouldReconnect) {
            setTimeout(connect, 3000);
          }
        };
      } catch (e) {
        onStatusChange?.('DISCONNECTED');
        if (shouldReconnect) setTimeout(connect, 5000);
      }
    };

    connect();

    return {
      disconnect: () => {
        shouldReconnect = false;
        if (ws) ws.close();
      },
    };
  },
};
