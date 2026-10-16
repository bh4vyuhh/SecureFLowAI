import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Terminal, Shield, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    {
      id: 'msg-init',
      sender: 'copilot',
      text: "SecureFlow AI Autonomous SOC Copilot active. Connected to local ONNX classifier telemetry and SQLite incident audit trail. Query any incident ID, hash, or security policy.",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const query = queryText || input;
    if (!query.trim()) return;

    const userMessage = {
      id: `usr-${Date.now()}`,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    if (!queryText) setInput('');
    setLoading(true);

    try {
      const response = await api.chatCopilot(query);
      const copilotMessage = {
        id: `ai-${Date.now()}`,
        sender: 'copilot',
        text: response.reply || response.answer || "Query processed by analyst copilot.",
        citations: response.citations || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, copilotMessage]);
    } catch (err) {
      console.error('Copilot chat error:', err);
      const errorMsg = {
        id: `ai-err-${Date.now()}`,
        sender: 'copilot',
        text: `Error connecting to Copilot service: ${err.message || 'Service unavailable'}. Please verify FastAPI backend on port 8000.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 flex flex-col h-[650px] shadow-2xl">
      {/* Copilot Header */}
      <div className="flex items-center justify-between border-b border-[#161619] pb-4 mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-black font-extrabold text-sm shadow-[0_0_12px_rgba(255,255,255,0.2)]">
            SF
          </div>
          <div>
            <div className="text-sm font-extrabold text-white uppercase tracking-tight flex items-center gap-2">
              Autonomous Analyst Copilot
              <span className="w-2 h-2 rounded-full bg-[#8df85f] inline-block" />
            </div>
            <div className="text-[11px] text-[#8e8f96] font-mono">
              Tier 5 Conversational SOC Assistant
            </div>
          </div>
        </div>

        <button
          onClick={() => setMessages([messages[0]])}
          className="text-xs text-[#8e8f96] hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-[#121316] border border-[#21232a] transition cursor-pointer"
        >
          <RefreshCw className="w-3 h-3" />
          Clear Chat
        </button>
      </div>

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2 select-text">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'copilot' && (
              <div className="w-8 h-8 rounded-full bg-[#121316] border border-[#21232a] flex items-center justify-center shrink-0 text-[#8df85f]">
                <Bot className="w-4 h-4" />
              </div>
            )}

            <div
              className={`max-w-[78%] rounded-2xl p-4 text-xs leading-relaxed ${
                msg.sender === 'user'
                  ? 'bg-white text-black font-medium'
                  : 'bg-[#121316] border border-[#21232a] text-slate-200'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.text}</div>
              <div className={`text-[10px] mt-2 font-mono ${msg.sender === 'user' ? 'text-black/60 text-right' : 'text-[#8e8f96]'}`}>
                {msg.timestamp}
              </div>
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-full bg-[#121316] border border-[#21232a] flex items-center justify-center shrink-0 text-white font-bold text-xs">
                SO
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center text-[#8e8f96] text-xs font-mono">
            <div className="w-8 h-8 rounded-full bg-[#121316] border border-[#21232a] flex items-center justify-center text-[#8df85f]">
              <RefreshCw className="w-4 h-4 animate-spin" />
            </div>
            <span>Copilot analyzing real-time audit records...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="flex gap-2 items-center pt-3 border-t border-[#161619]"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask Copilot about any incident ID, token, policy rule, or detection..."
          className="flex-1 bg-[#121316] border border-[#21232a] rounded-xl px-4 py-3 text-xs text-white placeholder-[#8e8f96] focus:outline-none focus:border-white font-sans"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="w-12 h-11 bg-white text-black rounded-xl flex items-center justify-center hover:scale-105 transition cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed shadow-md"
        >
          <Send className="w-4 h-4" />
        </button>
      </form>
    </div>
  );
}
