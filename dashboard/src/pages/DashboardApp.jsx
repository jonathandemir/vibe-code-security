// VibeGuard Dashboard v2 — with Scan History
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Shield, ShieldAlert, ShieldCheck, Code2, Loader2, KeyRound, UploadCloud, FolderSync, FileArchive } from 'lucide-react';
import ScanResults from '../components/ScanResults';
import ScanHistory from '../components/ScanHistory';

function App() {
  const [code, setCode] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [scanHistory, setScanHistory] = useState([]);
  const [activeScanId, setActiveScanId] = useState(null);
  const [pendingUpload, setPendingUpload] = useState(null);

  // Drag & Drop specific state
  const [isDragOver, setIsDragOver] = useState(false);
  const [isZipping, setIsZipping] = useState(false);

  // Drag handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setIsDragOver(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    setIsDragOver(false);

    const items = e.dataTransfer.items;
    if (!items || items.length === 0) return;

    if (!window.JSZip) {
      setError("JSZip library not loaded. Please refresh the page.");
      return;
    }

    setIsZipping(true);
    setError(null);
    setResults(null);
    setActiveScanId(null);

    try {
      const zip = new window.JSZip();

      const processEntry = async (entry, path = '') => {
        if (entry.isFile) {
          const file = await new Promise((resolve) => entry.file(resolve));
          zip.file(path + file.name, file);
        } else if (entry.isDirectory) {
          const dirReader = entry.createReader();
          const entries = await new Promise((resolve) => {
            dirReader.readEntries(resolve);
          });
          for (const child of entries) {
            await processEntry(child, path + entry.name + '/');
          }
        }
      };

      for (let i = 0; i < items.length; i++) {
        const item = items[i];
        if (item.webkitGetAsEntry) {
          const entry = item.webkitGetAsEntry();
          if (entry) {
            await processEntry(entry);
          }
        }
      }

      const content = await zip.generateAsync({ type: "blob" });
      setPendingUpload({ blob: content, name: "repo.zip" });
      setIsZipping(false);
    } catch (err) {
      setError(err.message || "Failed to zip folder.");
    } finally {
      setIsZipping(false);
    }
  };

  const handleFolderSelect = async (e) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    if (!window.JSZip) {
      setError("JSZip library not loaded. Please refresh the page.");
      return;
    }

    setIsZipping(true);
    setError(null);
    setResults(null);
    setActiveScanId(null);

    try {
      const zip = new window.JSZip();
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        // file.webkitRelativePath contains the full path including the root folder name
        zip.file(file.webkitRelativePath || file.name, file);
      }

      const content = await zip.generateAsync({ type: "blob" });
      setPendingUpload({ blob: content, name: "repo.zip" });
      setIsZipping(false);
    } catch (err) {
      setError(err.message || "Failed to zip folder.");
      setIsZipping(false);
    }
  };

  // API Config — configurable for deployment
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';
  const API_KEY = import.meta.env.VITE_API_KEY || '';

  // Shared headers for authenticated API calls
  const authHeaders = API_KEY ? { 'X-API-Key': API_KEY } : {};

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
    if (!code.trim() && !pendingUpload) {
      setError("Please paste some code or drop a folder to scan.");
      return;
    }

    setError(null);
    setIsScanning(true);
    setResults(null);
    setActiveScanId(null);

    try {
      let response;
      if (pendingUpload) {
        const formData = new FormData();
        formData.append("file", pendingUpload.blob, pendingUpload.name);
        formData.append("language", "python");

        response = await fetch(`${API_BASE}/scan-repo`, {
          method: 'POST',
          headers: authHeaders,
          body: formData,
        });

        setPendingUpload(null);
      } else {
        response = await fetch(`${API_BASE}/scan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders,
          },
          body: JSON.stringify({
            code: code,
            language: 'python' // Hardcoded for MVP, could be dynamic
          }),
        });
      }

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
      const res = await fetch(`${API_BASE}/scans/${scanId}`, { headers: authHeaders });
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
      const res = await fetch(`${API_BASE}/scans/${scanId}`, { method: 'DELETE', headers: authHeaders });
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
    <div className="min-h-screen bg-[#0A0A14] text-slate-200 selection:bg-[#7B61FF]/30 selection:text-[#F0EFF4] font-sans">



      <main className="max-w-7xl mx-auto px-6 pt-32 pb-12">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-sans font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-[#F0EFF4] via-[#F0EFF4]/80 to-[#7B61FF] pb-2">
            The Stripe for App-Security.
          </h1>
          <p className="mt-4 text-xl text-slate-400 max-w-2xl mx-auto">
            Drop your code below. We'll automatically find the vulnerabilities other AI tools missed and show you exactly how to fix them.
          </p>
        </div>

        <div className={`grid gap-6 items-start ${scanHistory.length > 0 || results ? 'lg:grid-cols-[250px_1fr_1.5fr]' : 'max-w-3xl mx-auto'}`}>

          {/* Scan History Sidebar */}
          {(scanHistory.length > 0 || results) && (
            <div className="hidden lg:block">
              <ScanHistory
                scans={scanHistory}
                onSelect={handleSelectScan}
                onDelete={handleDeleteScan}
                activeScanId={activeScanId}
              />
            </div>
          )}

          {/* Input Section */}
          <div
            className={`glass-panel p-6 flex flex-col h-[600px] lg:h-[700px] border-2 transition-all duration-300 relative cursor-pointer ${isDragOver ? "border-[#7B61FF] bg-[#18181B]/80 shadow-[0_0_50px_rgba(123,97,255,0.2)] scale-[1.02]" : "border-white/5"}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById('folder-upload').click()}
          >
            <input
              type="file"
              id="folder-upload"
              className="hidden"
              webkitdirectory="true"
              directory="true"
              multiple
              onChange={handleFolderSelect}
            />

            {/* Drag Overlay */}
            {isDragOver ? (
              <div className="absolute inset-0 z-50 flex flex-col items-center justify-center bg-[#0A0A14]/80 backdrop-blur-sm rounded-2xl border-2 border-[#7B61FF] border-dashed">
                <FolderSync className="w-16 h-16 text-[#7B61FF] mb-4 animate-bounce" />
                <h3 className="text-2xl font-bold font-sans text-white">Drop to Scan</h3>
                <p className="text-[#F0EFF4] mt-2 font-mono text-sm">Automated local zipping & upload</p>
              </div>
            ) : null}

            {!code && !isScanning && !isZipping && !results && !activeScanId && !isDragOver && !pendingUpload && (
              <div className="absolute inset-0 z-40 flex flex-col items-center justify-center pointer-events-none opacity-60">
                <FolderSync className="w-12 h-12 text-[#7B61FF] mb-4 opacity-50" />
                <h3 className="text-xl font-bold font-sans text-white">Drag & Drop a Folder</h3>
                <p className="text-neutral-400 mt-2 font-sans text-sm">or click anywhere to select</p>
              </div>
            )}

            <div className="flex items-center justify-between mb-4 text-slate-300">
              <div className="flex items-center gap-2">
                <Code2 className="w-5 h-5 text-[#7B61FF]" />
                <h2 className="text-lg font-sans font-semibold">Source Code</h2>
              </div>
              <div className="flex items-center gap-2 text-xs font-mono text-neutral-500 bg-[#0A0A14] px-3 py-1.5 rounded-full border border-white/5">
                <UploadCloud className="w-3.5 h-3.5" /> Drop Folder to Scan
              </div>
            </div>

            {pendingUpload ? (
              <div className="flex-1 w-full bg-[#18181B] border border-[#7B61FF]/30 border-dashed rounded-lg p-6 flex flex-col items-center justify-center text-center shadow-inner relative z-20">
                <FileArchive className="w-12 h-12 text-[#7B61FF] mb-3" />
                <h3 className="text-xl font-bold font-sans text-[#F0EFF4]">Repository Zipped successfully!</h3>
                <p className="text-slate-400 mt-2 text-sm italic">Your folder has been packaged safely on your machine.</p>
                <button
                  onClick={(e) => { e.stopPropagation(); setPendingUpload(null); }}
                  className="mt-6 px-4 py-2 text-sm bg-slate-800 hover:bg-slate-700 text-slate-300 rounded border border-slate-700 hover:text-white transition-all pointer-events-auto"
                >
                  Cancel and use text input instead
                </button>
              </div>
            ) : (
              <textarea
                className="flex-1 w-full bg-[#0A0A14] border border-white/5 rounded-lg p-4 font-mono text-sm text-[#F0EFF4] focus:outline-none focus:ring-1 focus:ring-[#7B61FF] focus:border-transparent resize-none relative z-20"
                placeholder={"# Paste your Python/JS/TS code here to vibrate the security scanner...\n\ndef get_user(db, user_id):\n    # Vulnerable SQL Injection\n    query = 'SELECT * FROM users WHERE id = ' + str(user_id)\n    db.execute(query)"}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onClick={(e) => e.stopPropagation()}
                spellCheck="false"
              />
            )}

            {error && (
              <div className="mt-4 p-3 bg-vibe-danger/10 border border-vibe-danger/20 rounded-lg text-vibe-danger text-sm flex items-center gap-2">
                <ShieldAlert className="w-4 h-4" />
                {error}
              </div>
            )}

            <button
              onClick={handleScan}
              disabled={isScanning || isZipping || (!code.trim() && !pendingUpload)}
              className="btn-magnetic mt-4 w-full py-4 px-6 rounded-lg font-sans font-bold text-white bg-gradient-to-r from-[#7B61FF] to-[#4529a6] hover:from-[#654ad6] hover:to-[#7B61FF] transition-all shadow-[0_0_20px_rgba(123,97,255,0.3)] hover:shadow-[0_0_30px_rgba(123,97,255,0.5)] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isZipping ? (
                <>
                  <FileArchive className="w-5 h-5 animate-pulse" />
                  Zipping Repository...
                </>
              ) : isScanning ? (
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

          {/* Results Section - Only show if we have history or results */}
          {(scanHistory.length > 0 || results) && (
            <div className="h-[600px] lg:h-[700px]">
              {results ? (
                <ScanResults results={results} />
              ) : (
                <div className="glass-panel h-full flex flex-col items-center justify-center text-slate-500 border-dashed border border-white/10 bg-[#18181B]/40">
                  <Shield className="w-16 h-16 text-neutral-800 mb-4" />
                  <h3 className="text-lg font-sans font-medium text-neutral-400">System Ready</h3>
                  <p className="text-sm font-sans mt-2 max-w-sm text-center">
                    Paste your code and initialize scan to see your VibeGuard Security Score.
                  </p>
                  <div className="mt-8 flex gap-4 text-xs font-mono">
                    <span className="flex items-center gap-1.5 bg-[#0A0A14] px-3 py-1.5 rounded-full text-neutral-400 border border-white/5">
                      <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> Static Analysis
                    </span>
                    <span className="flex items-center gap-1.5 bg-[#0A0A14] px-3 py-1.5 rounded-full text-neutral-400 border border-white/5">
                      <KeyRound className="w-3.5 h-3.5 text-amber-400" /> Secrets Detection
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}

        </div>
      </main>
    </div>
  );
}

export default App;
