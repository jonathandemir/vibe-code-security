// VibeGuard Dashboard v2 — with Scan History
import React, { useState, useEffect } from 'react';
import { Shield, ShieldAlert, ShieldCheck, Code2, Loader2, KeyRound } from 'lucide-react';
import ScanResults from './components/ScanResults';
import ScanHistory from './components/ScanHistory';

function App() {
  const [code, setCode] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [activeScanId, setActiveScanId] = useState(null);

  // Hardcode the local API URL for the MVP
  const API_BASE = 'http://localhost:8000';

  // Fetch scan history on mount
  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/scans`);
      if (res.ok) {
        const data = await res.json();
        setScanHistory(data);
      }
    } catch (err) {
      console.error("Failed to fetch scan history:", err);
    }
  };

  const handleScan = async () => {
    if (!code.trim()) {
      setError("Please paste some code to scan.");
      return;
    }

    setError(null);
    setIsScanning(true);
    setResults(null);
    setActiveScanId(null);

    try {
      const response = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code: code,
          language: 'python' // Hardcoded for MVP, could be dynamic
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      setResults(data);
      setActiveScanId(data.scan_id || null);

      // Refresh history after a new scan
      fetchHistory();
    } catch (err) {
      setError(err.message || "Failed to scan code. Is the API backend running?");
    } finally {
      setIsScanning(false);
    }
  };

  const handleSelectScan = async (scanId) => {
    try {
      const res = await fetch(`${API_BASE}/scans/${scanId}`);
      if (res.ok) {
        const data = await res.json();
        setResults(data);
        setActiveScanId(scanId);
        setError(null);
      }
    } catch (err) {
      console.error("Failed to load scan:", err);
    }
  };

  const handleDeleteScan = async (scanId) => {
    try {
      const res = await fetch(`${API_BASE}/scans/${scanId}`, { method: 'DELETE' });
      if (res.ok) {
        // If the deleted scan was active, clear results
        if (activeScanId === scanId) {
          setResults(null);
          setActiveScanId(null);
        }
        // Refresh history
        fetchHistory();
      }
    } catch (err) {
      console.error("Failed to delete scan:", err);
    }
  };

  return (
    <div className="min-h-screen bg-vibe-dark text-slate-200 selection:bg-vibe-accent selection:text-white font-sans">

      {/* Navigation Bar */}
      <nav className="border-b border-slate-800 bg-vibe-dark/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-vibe-accent to-purple-800 flex items-center justify-center shadow-lg shadow-vibe-accent/20">
              <Shield className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white">VibeGuard</span>
          </div>
          <div className="flex gap-4 items-center">
            <a href="#" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Docs</a>
            <a href="#" className="text-sm font-medium text-slate-400 hover:text-white transition-colors">Pricing</a>
            <button className="px-4 py-2 text-sm font-medium bg-slate-800 hover:bg-slate-700 text-white rounded-lg transition-colors border border-slate-700">
              Sign In
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-vibe-accent pb-2">
            The Stripe for App-Security.
          </h1>
          <p className="mt-4 text-xl text-slate-400 max-w-2xl mx-auto">
            Drop your code below. We'll automatically find the vulnerabilities other AI tools missed and show you exactly how to fix them.
          </p>
        </div>

        <div className="grid lg:grid-cols-[280px_1fr_1fr] gap-6 items-start">

          {/* Scan History Sidebar */}
          <div className="hidden lg:block">
            <ScanHistory
              scans={scanHistory}
              onSelect={handleSelectScan}
              onDelete={handleDeleteScan}
              activeScanId={activeScanId}
            />
          </div>

          {/* Input Section */}
          <div className="glass-panel p-6 flex flex-col h-[600px]">
            <div className="flex items-center gap-2 mb-4 text-slate-300">
              <Code2 className="w-5 h-5 text-vibe-accent" />
              <h2 className="text-lg font-semibold">Source Code</h2>
            </div>

            <textarea
              className="flex-1 w-full bg-slate-900 border border-slate-700 rounded-lg p-4 font-mono text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-vibe-accent focus:border-transparent resize-none"
              placeholder={"# Paste your Python/JS/TS code here to vibrate the security scanner...\n\ndef get_user(db, user_id):\n    # Vulnerable SQL Injection\n    query = 'SELECT * FROM users WHERE id = ' + str(user_id)\n    db.execute(query)"}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              spellCheck="false"
            />

            {error && (
              <div className="mt-4 p-3 bg-vibe-danger/10 border border-vibe-danger/20 rounded-lg text-vibe-danger text-sm flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" />
                {error}
              </div>
            )}

            <button
              onClick={handleScan}
              disabled={isScanning || !code.trim()}
              className="mt-4 w-full py-4 px-6 rounded-lg font-bold text-white bg-gradient-to-r from-vibe-accent to-purple-600 hover:from-purple-500 hover:to-fuchsia-600 transition-all shadow-[0_0_20px_rgba(139,92,246,0.3)] hover:shadow-[0_0_30px_rgba(139,92,246,0.5)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isScanning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running AI Scanner...
                </>
              ) : (
                <>
                  <ShieldCheck className="w-5 h-5" />
                  Scan Code Now
                </>
              )}
            </button>
          </div>

          {/* Results Section */}
          <div className="h-[600px]">
            {results ? (
              <ScanResults results={results} />
            ) : (
              <div className="glass-panel h-full flex flex-col items-center justify-center text-slate-500 border-dashed border-2 border-slate-700 bg-slate-800/30">
                <Shield className="w-16 h-16 text-slate-700 mb-4" />
                <h3 className="text-lg font-medium text-slate-400">No active scan</h3>
                <p className="text-sm mt-2 max-w-sm text-center">
                  Paste your code and hit scan to see your VibeGuard Security Score and AI-generated fixes.
                </p>
                <div className="mt-8 flex gap-4 text-xs">
                  <span className="flex items-center gap-1.5 bg-slate-800 px-3 py-1.5 rounded-full text-slate-400">
                    <ShieldCheck className="w-3.5 h-3.5 text-vibe-success" /> Static Analysis
                  </span>
                  <span className="flex items-center gap-1.5 bg-slate-800 px-3 py-1.5 rounded-full text-slate-400">
                    <KeyRound className="w-3.5 h-3.5 text-vibe-warning" /> Secrets Detection
                  </span>
                </div>
              </div>
            )}
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
