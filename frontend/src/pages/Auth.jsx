import React, { useState } from 'react';
import { Mail, Lock, User, ArrowRight } from 'lucide-react';
import toast from 'react-hot-toast';

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!email || !password || (!isLogin && !name)) {
      toast.error('Please fill in all fields.');
      return;
    }
    
    toast.success(isLogin ? 'Login successful!' : 'Account registered successfully!');
    onLogin({ name: isLogin ? 'Security Officer' : name, email });
  };

  return (
    <div className="min-h-screen bg-black flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-1/4 left-1/4 w-80 h-80 rounded-full bg-[#8df85f]/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full bg-[#f38933]/5 blur-[120px] pointer-events-none" />

      <div className="w-full max-w-md bg-[#0c0c0e] border border-[#161619] rounded-[36px] p-10 space-y-8 relative z-10 shadow-2xl">
        <div className="text-center space-y-3">
          <div className="w-14 h-14 rounded-full bg-white flex items-center justify-center mx-auto shadow-[0_0_20px_rgba(255,255,255,0.1)]">
            <span className="text-black font-extrabold text-xl font-mono">SF</span>
          </div>
          <div>
            <h2 className="text-2xl font-extrabold tracking-tight text-white uppercase">SecureFlow AI</h2>
            <p className="text-xs text-[#8e8f96] mt-1">Data Loss Prevention & Automated Encryptions Gateway</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div className="space-y-1.5">
              <label className="text-[10px] font-bold text-[#8e8f96] uppercase tracking-wider">Full Name</label>
              <div className="relative">
                <User className="w-4.5 h-4.5 text-[#8e8f96] absolute left-4 top-3.5" />
                <input
                  type="text"
                  placeholder="Bogdan Nikitin"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full h-12 bg-[#121316] border border-[#23252c] rounded-xl pl-11 pr-4 text-sm text-white placeholder-[#8e8f96] focus:outline-none focus:border-white transition"
                />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-[#8e8f96] uppercase tracking-wider">Work Email</label>
            <div className="relative">
              <Mail className="w-4.5 h-4.5 text-[#8e8f96] absolute left-4 top-3.5" />
              <input
                type="email"
                placeholder="officer@company.com"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full h-12 bg-[#121316] border border-[#23252c] rounded-xl pl-11 pr-4 text-sm text-white placeholder-[#8e8f96] focus:outline-none focus:border-white transition"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-[10px] font-bold text-[#8e8f96] uppercase tracking-wider">Password</label>
            <div className="relative">
              <Lock className="w-4.5 h-4.5 text-[#8e8f96] absolute left-4 top-3.5" />
              <input
                type="password"
                placeholder="••••••••••••"
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full h-12 bg-[#121316] border border-[#23252c] rounded-xl pl-11 pr-4 text-sm text-white placeholder-[#8e8f96] focus:outline-none focus:border-white transition"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full h-12 bg-white text-black font-bold text-sm rounded-xl flex items-center justify-center gap-2 hover:scale-[1.01] transition-all duration-300 cursor-pointer shadow-md mt-6"
          >
            Authenticate Access
            <ArrowRight className="w-4.5 h-4.5" />
          </button>
        </form>

        <div className="text-center pt-2">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-xs text-[#8df85f] hover:underline font-semibold"
          >
            {isLogin ? "Need a new security credential? Sign Up" : "Already have access permissions? Log In"}
          </button>
        </div>
      </div>
    </div>
  );
}
