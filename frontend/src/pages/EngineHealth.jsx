import React, { useState } from 'react';
import { Cpu, HardDrive, ShieldCheck, Zap, RefreshCw, Activity, Server, Database, Radio } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '../services/api';

export default function EngineHealth({ healthData = null, onRefresh, wsStatus = 'DISCONNECTED' }) {
  const [benchmarking, setBenchmarking] = useState(false);
  const [benchmarkResults, setBenchmarkResults] = useState(null);

  const runLatencyBenchmark = async () => {
    setBenchmarking(true);
    const latencies = [];

    try {
      for (let i = 0; i < 5; i++) {
        const text = `SecureFlow SLA Latency Probe #${i + 1} at timestamp ${Date.now()}`;
        const t0 = performance.now();
        await api.scanDLP({ text, mode: 'mask' });
        const elapsed = performance.now() - t0;
        latencies.push(elapsed);
      }

      latencies.sort((a, b) => a - b);
      const p50 = latencies[Math.floor(latencies.length * 0.5)];
      const p95 = latencies[Math.floor(latencies.length * 0.95)] || latencies[latencies.length - 1];
      const avg = latencies.reduce((a, b) => a + b, 0) / latencies.length;

      setBenchmarkResults({
        samples: latencies.length,
        avg: avg.toFixed(1),
        p50: p50.toFixed(1),
        p95: p95.toFixed(1),
        passed: p95 < 35.0,
      });

      toast.success('Live SLA Benchmark probe completed successfully.');
    } catch (e) {
      toast.error('Benchmark probe failed. Ensure microservice is running.');
    } finally {
      setBenchmarking(false);
    }
  };

  return (
    <div className="flex-1 p-8 space-y-8 select-none">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight uppercase font-sans text-white">
            ENGINE HEALTH & CRYPTOGRAPHY
          </h1>
          <p className="text-sm text-[#8e8f96]">
            Real-time sliding-window ONNX INT8 profiler, hardware acceleration, memory footprint, and token vault envelope status.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={runLatencyBenchmark}
            disabled={benchmarking}
            className="bg-white text-black font-semibold text-xs px-4 py-2 rounded-xl flex items-center gap-2 hover:scale-105 transition cursor-pointer disabled:opacity-40"
          >
            <Zap className="w-3.5 h-3.5" />
            {benchmarking ? 'Probing Latency...' : 'Run Real SLA Benchmark (5x)'}
          </button>

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="bg-[#0c0c0e] border border-[#161619] rounded-xl px-3.5 py-2 text-xs font-semibold text-[#8e8f96] hover:text-white hover:border-white transition cursor-pointer flex items-center gap-1.5"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Sync
            </button>
          )}
        </div>
      </div>

      {/* Grid of 4 Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
            <span>Inference Runtime</span>
            <Cpu className="w-4 h-4 text-[#8df85f]" />
          </div>
          <div className="text-xl font-extrabold text-white font-mono truncate">
            {healthData?.active_model || 'Connecting...'}
          </div>
          <div className="text-[10px] text-[#8df85f] font-mono">
            {healthData ? 'INT8 Quantized ONNX + spaCy NER' : 'Querying /health...'}
          </div>
        </div>

        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
            <span>Memory Footprint</span>
            <HardDrive className="w-4 h-4 text-white" />
          </div>
          <div className="text-2xl font-extrabold text-white font-sans">
            {healthData?.memory_usage_mb ? `${healthData.memory_usage_mb} MB` : 'Measuring...'}
          </div>
          <div className="text-[10px] text-[#8df85f] font-mono">
            Real Process RSS Memory
          </div>
        </div>

        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
            <span>Execution Providers</span>
            <Server className="w-4 h-4 text-[#8df85f]" />
          </div>
          <div className="text-xl font-extrabold text-white font-mono truncate">
            {healthData?.active_providers?.join(', ') || 'Connecting...'}
          </div>
          <div className="text-[10px] text-white font-mono">
            Hardware Engine
          </div>
        </div>

        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-2">
          <div className="flex items-center justify-between text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
            <span>Threat Bus Stream</span>
            <Radio className="w-4 h-4 text-[#8df85f] animate-pulse" />
          </div>
          <div className="text-xl font-extrabold text-white font-mono">
            {wsStatus}
          </div>
          <div className="text-[10px] text-[#8df85f] font-mono">
            ws://localhost:8000/ws/live-threats
          </div>
        </div>
      </div>

      {/* SLA Benchmark Box */}
      {benchmarkResults && (
        <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
              Live CPU Latency SLA Probe Results
            </span>
            <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold font-mono uppercase ${
              benchmarkResults.passed 
                ? 'bg-[#8df85f]/15 text-[#8df85f] border border-[#8df85f]/30' 
                : 'bg-[#f38933]/15 text-[#f38933] border border-[#f38933]/30'
            }`}>
              {benchmarkResults.passed ? 'PASSED SLA' : 'BREACH'}
            </span>
          </div>

          <div className="grid grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl">
              <div className="text-2xl font-extrabold text-white font-mono">{benchmarkResults.avg}ms</div>
              <div className="text-[10px] text-[#8e8f96] uppercase mt-1">Mean Roundtrip</div>
            </div>
            <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl">
              <div className="text-2xl font-extrabold text-white font-mono">{benchmarkResults.p50}ms</div>
              <div className="text-[10px] text-[#8e8f96] uppercase mt-1">P50 Median</div>
            </div>
            <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl">
              <div className="text-2xl font-extrabold text-[#8df85f] font-mono">{benchmarkResults.p95}ms</div>
              <div className="text-[10px] text-[#8e8f96] uppercase mt-1">P95 SLA</div>
            </div>
            <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl">
              <div className="text-2xl font-extrabold text-white font-mono">{benchmarkResults.samples}</div>
              <div className="text-[10px] text-[#8e8f96] uppercase mt-1">Probes Executed</div>
            </div>
          </div>
        </div>
      )}

      {/* Cryptographic Vault & Architecture Spec */}
      <div className="bg-[#0c0c0e] border border-[#161619] rounded-[28px] p-6 space-y-4">
        <div className="text-[11px] font-bold tracking-wider text-[#8e8f96] uppercase">
          Zero-Egress Air-Gapped Architectural Guarantees
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl space-y-1.5">
            <div className="font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-[#8df85f]" />
              Local ONNX Model Engine
            </div>
            <p className="text-[#8e8f96] text-[11px] leading-relaxed">
              Sliding-window INT8 quantized neural network runs locally on CPU with zero cloud API dependencies.
            </p>
          </div>

          <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl space-y-1.5">
            <div className="font-bold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-[#8df85f]" />
              HMAC Envelope Tokenization
            </div>
            <p className="text-[#8e8f96] text-[11px] leading-relaxed">
              PII is replaced with deterministic tokens encrypted via AES-256-GCM. Plaintext never leaves the boundary.
            </p>
          </div>

          <div className="p-4 bg-[#121316] border border-[#21232a] rounded-2xl space-y-1.5">
            <div className="font-bold text-white flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#8df85f]" />
              Client Circuit Breakers
            </div>
            <p className="text-[#8e8f96] text-[11px] leading-relaxed">
              Browser extension and desktop daemons maintain offline fail-open queues with automatic half-open probes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
