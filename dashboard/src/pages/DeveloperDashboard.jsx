import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { Key, Copy, RefreshCw, CheckCircle, Shield, Zap, BarChart3, Eye, EyeOff, Github, ExternalLink } from 'lucide-react';
export default function DeveloperDashboard() {
    const { user } = useUser();
    const { getToken } = useAuth();
    const [apiKey, setApiKey] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [plan, setPlan] = useState('free');
    const [scanCount, setScanCount] = useState(0);
    const [credits, setCredits] = useState(0);
    const [showKey, setShowKey] = useState(true);
    const [loadingTier, setLoadingTier] = useState(null);
    const [githubConnected, setGithubConnected] = useState(false);
    const [installMessage, setInstallMessage] = useState(null);
    const [installationId, setInstallationId] = useState(null);

    const API_BASE = import.meta.env.VITE_API_BASE || 'https://vouch-api.onrender.com';
    // Provide a fallback GitHub App Name if not set in environment
    const GITHUB_APP_NAME = import.meta.env.VITE_GITHUB_APP_NAME || 'vouch-security';

    const handleCheckout = async (tier) => {
        setLoadingTier(tier);
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/developer/create-checkout-session`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tier })
            });
            const data = await res.json();
            if (data.url) {
                window.location.href = data.url;
            } else {
                alert("Checkout error: " + (data.detail || "Unknown error"));
            }
        } catch (err) {
            console.error("Failed to begin checkout", err);
        } finally {
            setLoadingTier(null);
        }
    };

    // Fetch the user's existing API key on mount
    useEffect(() => {
        async function fetchKey() {
            try {
                const token = await getToken();
                const res = await fetch(`${API_BASE}/developer/me`, {
                    headers: { 'Authorization': `Bearer ${token}` },
                });
                if (res.ok) {
                    const data = await res.json();
                    setApiKey(data.api_key);
                    setPlan(data.plan || 'free');
                    setScanCount(data.scan_count || 0);
                    setCredits(data.credits || 0);
                    if (data.github_installation_id) {
                        setGithubConnected(true);
                        setInstallationId(data.github_installation_id);
                    }
                }
            } catch (err) {
                console.log('No existing key found, user can generate one.');
            } finally {
                setLoading(false);
            }
        }
        
        async function handleMagicFlow(installationId, setupAction) {
            setInstallMessage({ type: 'info', text: 'Linking your GitHub account...' });
            try {
                const token = await getToken();
                const res = await fetch(`${API_BASE}/developer/link-github`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ installation_id: installationId, setup_action: setupAction })
                });

                if (res.ok) {
                    setInstallMessage({ type: 'success', text: 'GitHub App successfully connected and Free Tier activated!' });
                    setGithubConnected(true);
                    setInstallationId(installationId);
                    setPlan('free'); // Update local state
                } else {
                    const error = await res.json();
                    setInstallMessage({ type: 'error', text: `Linking failed: ${error.detail || 'Unknown error'}` });
                }
            } catch (err) {
                console.error("Magic Flow error:", err);
                setInstallMessage({ type: 'error', text: 'Connection error during GitHub linking.' });
            } finally {
                // Remove search params to clean the URL
                window.history.replaceState(null, '', window.location.pathname);
                // Refresh user data to be sure
                fetchKey();
            }
        }

        // Handle OAuth Callback messages
        const urlParams = new URLSearchParams(window.location.search);
        const instId = urlParams.get('installation_id');
        const setupAct = urlParams.get('setup_action');

        if (instId && setupAct) {
            handleMagicFlow(instId, setupAct);
        } else if (urlParams.get('installation') === 'success') {
            setInstallMessage({ type: 'success', text: 'GitHub App successfully connected!' });
            window.history.replaceState(null, '', window.location.pathname);
            fetchKey();
        } else if (urlParams.get('installation') === 'error') {
            setInstallMessage({ type: 'error', text: 'Failed to connect GitHub App. Please try again.' });
            window.history.replaceState(null, '', window.location.pathname);
            fetchKey();
        } else {
            fetchKey();
        }
    }, [getToken, API_BASE]);

    const handleGenerateKey = async () => {
        setGenerating(true);
        try {
            const token = await getToken();
            const res = await fetch(`${API_BASE}/developer/generate-key`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
            });
            if (res.ok) {
                const data = await res.json();
                setApiKey(data.api_key);
            } else {
                const errText = await res.text();
                console.error('API Key generation failed:', res.status, errText);
                alert(`Cannot generate key right now. If the backend is waking up, please try again in 30 seconds. (Error ${res.status})`);
            }
        } catch (err) {
            console.error('Failed to generate key (Connection error):', err);
            alert("Failed to connect to the backend server. It may be sleeping (Render Free Tier) or offline. Please wait 30-50 seconds and try again.");
        } finally {
            setGenerating(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(apiKey);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="animate-pulse text-neutral-400">Loading your dashboard...</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen pt-32 pb-20 px-6">
            <div className="max-w-4xl mx-auto space-y-8">
                {/* Header */}
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">
                        Welcome, <span className="text-[#7B61FF]">{user?.firstName || 'Developer'}</span>
                    </h1>
                    <p className="text-neutral-400">
                        Manage your API key, monitor usage, and upgrade your plan.
                    </p>
                </div>

                {/* Stats Row */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="glass-panel p-6 rounded-2xl border border-white/5">
                        <div className="flex items-center space-x-3 mb-2">
                            <Shield className="w-5 h-5 text-[#7B61FF]" />
                            <span className="text-sm text-neutral-400">Current Plan</span>
                        </div>
                        <p className="text-2xl font-bold capitalize">{plan}</p>
                    </div>
                    <div className="glass-panel p-6 rounded-2xl border border-white/5">
                        <div className="flex items-center space-x-3 mb-2">
                            <BarChart3 className="w-5 h-5 text-emerald-400" />
                            <span className="text-sm text-neutral-400">Scans Used</span>
                        </div>
                        <p className="text-2xl font-bold">{scanCount} <span className="text-sm text-neutral-500">/ {plan === 'pro' ? '∞' : '10'}</span></p>
                    </div>
                    <div className="glass-panel p-6 rounded-2xl border border-white/5">
                        <div className="flex items-center space-x-3 mb-2">
                            <Zap className="w-5 h-5 text-amber-400" />
                            <span className="text-sm text-neutral-400">Status</span>
                        </div>
                        <p className="text-2xl font-bold text-emerald-400">Active</p>
                    </div>
                </div>

                {/* API Key Section */}
                <div className="glass-panel p-8 rounded-2xl border border-white/5 space-y-6">
                    <div className="flex items-center space-x-3">
                        <Key className="w-6 h-6 text-[#7B61FF]" />
                        <h2 className="text-xl font-bold">Your API Key</h2>
                    </div>

                    {apiKey ? (
                        <div className="space-y-4">
                            <div className="flex items-center space-x-3">
                                <code className="flex-1 bg-[#0A0A14] border border-white/10 rounded-xl px-4 py-3 font-mono text-sm text-[#7B61FF] select-all overflow-x-auto">
                                    {showKey ? apiKey : 'vbg_' + '*'.repeat(24)}
                                </code>
                                <button
                                    onClick={() => setShowKey(!showKey)}
                                    className="p-3 rounded-xl border border-white/10 text-neutral-300 hover:text-[#7B61FF] hover:border-[#7B61FF]/40 hover:bg-[#7B61FF]/10 transition-all"
                                >
                                    {showKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                                </button>
                                <button
                                    onClick={copyToClipboard}
                                    className="flex items-center space-x-1.5 px-4 py-3 rounded-xl border border-white/10 text-sm text-neutral-300 hover:text-[#F0EFF4] hover:border-[#7B61FF]/40 hover:bg-[#7B61FF]/10 transition-all"
                                >
                                    {copied ? <CheckCircle className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                                    <span>{copied ? 'Copied!' : 'Copy'}</span>
                                </button>
                            </div>
                            <p className="text-sm text-neutral-500">
                                Use this key in your VS Code Extension settings or as the <code className="text-[#7B61FF]/70">X-API-Key</code> header.
                            </p>
                            <button
                                onClick={handleGenerateKey}
                                disabled={generating}
                                className="flex items-center space-x-2 px-4 py-2 rounded-xl border border-red-500/20 text-sm text-red-400 hover:bg-red-500/10 transition-all"
                            >
                                <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
                                <span>{generating ? 'Regenerating...' : 'Regenerate Key'}</span>
                            </button>
                        </div>
                    ) : (
                        <div className="text-center py-8 space-y-4">
                            <p className="text-neutral-400">You don't have an API key yet. Generate one to start scanning!</p>
                            <button
                                onClick={handleGenerateKey}
                                disabled={generating}
                                className="inline-flex items-center space-x-2 px-6 py-3 rounded-full bg-[#7B61FF] text-white font-semibold hover:bg-[#6A50E0] hover:shadow-[0_0_30px_rgba(123,97,255,0.5)] transition-all"
                            >
                                <Key className="w-5 h-5" />
                                <span>{generating ? 'Generating...' : 'Generate API Key'}</span>
                            </button>
                        </div>
                    )}
                </div>

                {/* Zero-Config GitHub Integration */}
                <div className="glass-panel p-8 rounded-2xl border border-white/5 space-y-6">
                    <div className="flex items-center space-x-3">
                        <Github className="w-6 h-6 text-white" />
                        <h2 className="text-xl font-bold">Zero-Config GitHub Integration</h2>
                    </div>
                    
                    {installMessage && (
                        <div className={`p-4 rounded-xl border text-sm font-medium ${installMessage.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
                            {installMessage.text}
                        </div>
                    )}

                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div className="flex-1 space-y-2">
                            <h3 className="text-lg font-semibold text-white">Automate Pull Request Security</h3>
                            <p className="text-neutral-400 text-sm leading-relaxed">
                                Install the Vouch native GitHub App to automatically scan every Pull Request for Vibe-Fails. 
                                We will post a detailed security review directly into the PR. 
                                <span className="text-[#7B61FF] font-medium ml-1">No API keys or code changes required.</span>
                            </p>
                        </div>

                        <div className="shrink-0">
                            {githubConnected ? (
                                <div className="inline-flex items-center space-x-2 px-6 py-3 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-semibold shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                                    <CheckCircle className="w-5 h-5" />
                                    <span>GitHub Connected</span>
                                </div>
                            ) : (
                                <a
                                    href={`https://github.com/apps/${GITHUB_APP_NAME}/installations/new?state=${user?.id}`}
                                    className="inline-flex items-center space-x-2 px-6 py-3 rounded-full bg-white text-black font-semibold hover:bg-neutral-200 transition-all shadow-[0_0_20px_rgba(255,255,255,0.2)] hover:shadow-[0_0_30px_rgba(255,255,255,0.4)]"
                                >
                                    <Github className="w-5 h-5" />
                                    <span>Install on GitHub</span>
                                    <ExternalLink className="w-4 h-4 ml-1 opacity-60" />
                                </a>
                            )}
                        </div>
                    </div>
                </div>

                {/* Viral Loop Badge (Only shown if connected) */}
                {githubConnected && installationId && (
                    <div className="glass-panel p-8 rounded-2xl border border-white/5 space-y-6">
                        <div className="flex items-center space-x-3">
                            <Shield className="w-6 h-6 text-[#7B61FF]" />
                            <h2 className="text-xl font-bold">Vouch Security Badge</h2>
                        </div>
                        <p className="text-neutral-400 text-sm">
                            Show off your repository's automated security posture in your <code>README.md</code>. We dynamically generate this SVG based on your latest PR scans.
                        </p>
                        
                        <div className="flex flex-col space-y-4">
                            <div className="p-4 bg-[#0A0A14] border border-white/5 rounded-xl flex items-center justify-center">
                                <img src={`${API_BASE}/badge/${installationId}`} alt="Vouch Security Badge" className="h-5" />
                            </div>
                            
                            <div className="flex items-center space-x-3 w-full">
                                <code className="flex-1 bg-[#0A0A14] border border-white/10 rounded-xl px-4 py-3 font-mono text-xs text-[#7B61FF] overflow-x-auto whitespace-nowrap">
                                    {`[![Vouch Score](${API_BASE}/badge/${installationId})](https://vouch-secure.com)`}
                                </code>
                                <button
                                    onClick={() => {
                                        navigator.clipboard.writeText(`[![Vouch Score](${API_BASE}/badge/${installationId})](https://vouch-secure.com)`);
                                    }}
                                    className="shrink-0 flex items-center space-x-1.5 px-4 py-3 rounded-xl border border-white/10 text-sm text-neutral-300 hover:text-[#F0EFF4] hover:border-[#7B61FF]/40 hover:bg-[#7B61FF]/10 transition-all"
                                >
                                    <Copy className="w-4 h-4" />
                                    <span>Copy Markdown</span>
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Upgrade CTA (only for free users) */}
                {plan === 'free' && (
                    <div className="glass-panel p-8 rounded-2xl border border-[#7B61FF]/20 bg-gradient-to-r from-[#7B61FF]/5 to-transparent space-y-6">
                        <div>
                            <h2 className="text-xl font-bold">Upgrade your Workflow</h2>
                            <p className="text-neutral-400 mt-2">
                                You are currently on the Free Tier (10 Scans / month, 0 Deep Auto Fixes).
                                Upgrade to unlock full developer velocity.
                            </p>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <button
                                onClick={() => handleCheckout('micro')}
                                disabled={loadingTier === 'micro'}
                                className="flex flex-col items-center justify-center p-4 rounded-xl border border-white/10 hover:border-[#7B61FF]/40 hover:bg-[#7B61FF]/5 transition-all text-left"
                            >
                                <div className="flex items-center space-x-2 text-[#7B61FF] mb-1">
                                    <Zap className="w-4 h-4" />
                                    <span className="font-bold">Micro Tier</span>
                                </div>
                                <span className="text-lg font-bold text-white">
                                    {loadingTier === 'micro' ? 'Loading...' : '$7 / mo'}
                                </span>
                                <span className="text-xs text-neutral-500 mt-1">100 Scans. Standard Speed.</span>
                            </button>

                            <button
                                onClick={() => handleCheckout('pro')}
                                disabled={loadingTier === 'pro'}
                                className="flex flex-col items-center justify-center p-4 rounded-xl border border-[#7B61FF]/40 bg-[#7B61FF]/10 hover:bg-[#7B61FF] hover:shadow-[0_0_30px_rgba(123,97,255,0.3)] transition-all group"
                            >
                                <div className="flex items-center space-x-2 text-white mb-1">
                                    <Shield className="w-4 h-4" />
                                    <span className="font-bold">Pro Tier</span>
                                </div>
                                <span className="text-lg font-bold text-white">
                                    {loadingTier === 'pro' ? 'Loading...' : '$15 / mo'}
                                </span>
                                <span className="text-xs text-white/50 mt-1 group-hover:text-white/80 transition-colors">300 Scans. Max API Speed.</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
