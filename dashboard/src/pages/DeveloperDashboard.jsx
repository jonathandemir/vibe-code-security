import React, { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/clerk-react';
import { Key, Copy, RefreshCw, CheckCircle, Shield, Zap, BarChart3, Eye, EyeOff } from 'lucide-react';

export default function DeveloperDashboard() {
    const { user } = useUser();
    const { getToken } = useAuth();
    const [apiKey, setApiKey] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [copied, setCopied] = useState(false);
    const [plan, setPlan] = useState('free');
    const [scanCount, setScanCount] = useState(0);
    const [showKey, setShowKey] = useState(false);

    const API_BASE = import.meta.env.VITE_API_BASE || 'https://vibeguard-api.onrender.com';

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
                }
            } catch (err) {
                console.log('No existing key found, user can generate one.');
            } finally {
                setLoading(false);
            }
        }
        fetchKey();
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
            }
        } catch (err) {
            console.error('Failed to generate key:', err);
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
                                className="flex flex-col items-center justify-center p-4 rounded-xl border border-white/10 hover:border-[#7B61FF]/40 hover:bg-[#7B61FF]/5 transition-all text-left"
                            >
                                <div className="flex items-center space-x-2 text-[#7B61FF] mb-1">
                                    <Zap className="w-4 h-4" />
                                    <span className="font-bold">Micro Tier</span>
                                </div>
                                <span className="text-lg font-bold text-white">$7 / mo</span>
                                <span className="text-xs text-neutral-500 mt-1">100 Scans. Standard Speed.</span>
                            </button>

                            <button
                                className="flex flex-col items-center justify-center p-4 rounded-xl border border-[#7B61FF]/40 bg-[#7B61FF]/10 hover:bg-[#7B61FF] hover:shadow-[0_0_30px_rgba(123,97,255,0.3)] transition-all group"
                            >
                                <div className="flex items-center space-x-2 text-white mb-1">
                                    <Shield className="w-4 h-4" />
                                    <span className="font-bold">Pro Tier</span>
                                </div>
                                <span className="text-lg font-bold text-white">$15 / mo</span>
                                <span className="text-xs text-white/50 mt-1 group-hover:text-white/80 transition-colors">Unlimited Scans. Max API Speed.</span>
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
