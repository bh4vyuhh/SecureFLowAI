import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { chatAnswers } from '../utils/mockData';

export default function Chatbot() {
  const [messages, setMessages] = useState([
    { id: 1, sender: 'bot', text: 'Hello! I am SecureFlow AI, your Data Loss Prevention assistant. Ask me about encryption, Slack notifications, our TF-IDF model, or PII masking rules.' }
  ]);
  const [input, setInput] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), sender: 'user', text: input };
    setMessages(prev => [...prev, userMessage]);
    
    const query = input.toLowerCase();
    setInput('');

    setTimeout(() => {
      const matched = chatAnswers.find(answer => 
        answer.keywords.some(keyword => query.includes(keyword))
      );

      const botReply = matched 
        ? matched.response 
        : "I'm still learning that topic! Try asking about 'encryption', 'slack webhook', 'pii masking', or 'classifier model' properties.";

      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        sender: 'bot',
        text: botReply
      }]);
    }, 600);
  };

  return (
    <div className="flex flex-col bg-[#0c0c0e] border border-[#161619] rounded-3xl w-full h-[calc(100vh-14rem)] overflow-hidden shadow-2xl">
      <div className="bg-[#121316] border-b border-[#161619] px-6 py-4 flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center">
          <Bot className="w-5.5 h-5.5 text-black" />
        </div>
        <div>
          <h2 className="text-base font-bold text-white mb-0">SecureFlow AI Assistant</h2>
          <span className="text-xs text-[#8df85f] flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-[#8df85f] animate-ping" />
            Online & monitoring
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div 
            key={msg.id} 
            className={`flex items-start gap-3 max-w-[85%] ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
              msg.sender === 'user' ? 'bg-[#121316] border border-[#23252c]' : 'bg-white'
            }`}>
              {msg.sender === 'user' ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-black" />}
            </div>
            
            <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
              msg.sender === 'user' 
                ? 'bg-white text-black rounded-tr-none font-medium' 
                : 'bg-[#121316] text-[#8e8f96] border border-[#1d1f24] rounded-tl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div className="p-4 bg-[#121316] border-t border-[#161619] flex gap-3 items-center">
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question about the DLP gateway or models..."
          className="flex-1 bg-[#0c0c0e] border border-[#23252c] rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-white transition"
        />
        <button
          onClick={handleSend}
          className="h-11 w-11 rounded-xl bg-white text-black flex items-center justify-center hover:scale-105 transition-all cursor-pointer shadow-md"
        >
          <Send className="w-4.5 h-4.5" />
        </button>
      </div>
    </div>
  );
}
