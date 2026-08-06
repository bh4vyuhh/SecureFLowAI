import React, { useState } from 'react';
import { Save, Key, Radio, Server, Mail } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Settings() {
  const [modelType, setModelType] = useState('tfidf');
  const [tokenTtl, setTokenTtl] = useState(15);
  const [circuitBreaker, setCircuitBreaker] = useState(true);
  const [mailtrapToken, setMailtrapToken] = useState('••••••••••••512a');

  const handleSave = () => {
    toast.success('DLP Gateway security configurations updated successfully!');
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div>
        <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
          GATEWAY SETTINGS
        </h1>
        <p className="text-sm text-[#8e8f96]">Configure model pipelines, Spring Boot connection properties, and OAuth variables.</p>
      </div>

      <div className="grid grid-cols-12 gap-8">
        <div className="col-span-7 space-y-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Server className="w-4.5 h-4.5 text-[#8df85f]" />
              AI Model & Pipeline Rules
            </h3>

            <div className="space-y-2">
              <label className="text-xs text-[#8e8f96] block font-semibold">Active NLP Engine Model</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setModelType('tfidf')}
                  className={`p-4 rounded-2xl border text-left flex flex-col justify-between h-24 transition cursor-pointer ${
                    modelType === 'tfidf' 
                      ? 'border-[#8df85f] bg-[#8df85f]/5 text-white' 
                      : 'border-[#23252c] bg-[#121316] text-[#8e8f96] hover:border-white'
                  }`}
                >
                  <span className="text-xs font-bold text-white">TF-IDF + Logistic Regression</span>
                  <span className="text-[10px] text-[#8e8f96] leading-normal">Fast baseline. Recommended for local/demo runs to save resources.</span>
                </button>

                <button
                  onClick={() => setModelType('distilbert')}
                  className={`p-4 rounded-2xl border text-left flex flex-col justify-between h-24 transition cursor-pointer ${
                    modelType === 'distilbert' 
                      ? 'border-[#8df85f] bg-[#8df85f]/5 text-white' 
                      : 'border-[#23252c] bg-[#121316] text-[#8e8f96] hover:border-white'
                  }`}
                >
                  <span className="text-xs font-bold text-white">DistilBERT Model (Fine-tuned)</span>
                  <span className="text-[10px] text-[#8e8f96] leading-normal">Deep learning transformer. High semantic parsing accuracy (~500MB RAM).</span>
                </button>
              </div>
            </div>

            <div className="flex items-center justify-between border-t border-[#161619] pt-6">
              <div>
                <h4 className="text-xs font-bold text-white">Spring Boot Resilience4j Circuit Breaker</h4>
                <p className="text-[10px] text-[#8e8f96] mt-0.5">Toggle RestTemplate/WebClient fallback to local cache during FastAPI outage.</p>
              </div>
              <button
                onClick={() => setCircuitBreaker(!circuitBreaker)}
                className={`w-12 h-6.5 rounded-full p-1 transition-colors duration-300 focus:outline-none ${
                  circuitBreaker ? 'bg-[#8df85f]' : 'bg-[#23252c]'
                }`}
              >
                <div className={`bg-black w-4.5 h-4.5 rounded-full shadow-md transform duration-300 ${
                  circuitBreaker ? 'translate-x-5.5' : 'translate-x-0'
                }`} />
              </button>
            </div>
          </div>

          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Key className="w-4.5 h-4.5 text-[#8df85f]" />
              Authorization & Tokens (JJWT)
            </h3>

            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-1.5">
                <label className="text-xs text-[#8e8f96] font-semibold">Access Token TTL (Minutes)</label>
                <input
                  type="number"
                  value={tokenTtl}
                  onChange={e => setTokenTtl(Number(e.target.value))}
                  className="w-full h-11 bg-[#121316] border border-[#23252c] rounded-xl px-4 text-xs text-white focus:outline-none focus:border-white transition"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs text-[#8e8f96] font-semibold">Refresh Token Storage</label>
                <div className="h-11 bg-[#121316]/50 border border-[#23252c] rounded-xl px-4 flex items-center text-xs text-[#8df85f] font-bold font-mono">
                  HttpOnly Secure Cookies
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-span-5 space-y-6">
          <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-6">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Radio className="w-4.5 h-4.5 text-[#f38933]" />
              Integrations
            </h3>

            <div className="space-y-2">
              <label className="text-xs text-[#8e8f96] font-semibold">Slack Webhook Alert URL</label>
              <input
                type="text"
                value={slackWebhook}
                onChange={e => setSlackWebhook(e.target.value)}
                className="w-full h-11 bg-[#121316] border border-[#23252c] rounded-xl px-4 text-xs text-white focus:outline-none focus:border-white transition font-mono truncate"
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs text-[#8e8f96] font-semibold">Mailtrap Admin Email Token</label>
              <div className="relative">
                <input
                  type="password"
                  value={mailtrapToken}
                  onChange={e => setMailtrapToken(e.target.value)}
                  className="w-full h-11 bg-[#121316] border border-[#23252c] rounded-xl px-4 text-xs text-white focus:outline-none focus:border-white transition font-mono"
                />
                <Mail className="w-4.5 h-4.5 text-[#8e8f96] absolute right-4 top-3.5" />
              </div>
            </div>

            <button
              onClick={handleSave}
              className="w-full h-12 bg-white text-black font-bold text-xs rounded-xl flex items-center justify-center gap-2 hover:scale-[1.02] transition cursor-pointer"
            >
              <Save className="w-4.5 h-4.5" />
              Save Settings Profiles
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
