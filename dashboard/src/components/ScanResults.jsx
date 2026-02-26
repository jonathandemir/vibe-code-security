import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, AlertOctagon, Info, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

const ScanResults = ({ results }) => {
    const { score, summary, issues = [] } = results;

    // Determine color based on score (Ampelsystem)
    const getScoreColor = (s) => {
        if (s >= 80) return 'text-vibe-success';
        if (s >= 50) return 'text-vibe-warning';
        return 'text-vibe-danger';
    };

    const getScoreBg = (s) => {
        if (s >= 80) return 'bg-vibe-success/10 border-vibe-success/20';
        if (s >= 50) return 'bg-vibe-warning/10 border-vibe-warning/20';
        return 'bg-vibe-danger/10 border-vibe-danger/20';
    };

    return (
        <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            {/* Header / Score Region */}
            <div className={`p-6 border-b flex items-center justify-between ${getScoreBg(score)}`}>
                <div>
                    <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-1">VibeGuard Score</h2>
                    <div className="flex items-baseline gap-2">
                        <span className={`text-5xl font-extrabold tracking-tight ${getScoreColor(score)}`}>{score}</span>
                        <span className="text-xl text-slate-500 font-medium">/ 100</span>
                    </div>
                </div>

                <div className="text-right max-w-[200px]">
                    {score >= 80 ? (
                        <CheckCircle className={`w-12 h-12 ml-auto mb-2 ${getScoreColor(score)}`} />
                    ) : score >= 50 ? (
                        <AlertTriangle className={`w-12 h-12 ml-auto mb-2 ${getScoreColor(score)}`} />
                    ) : (
                        <AlertOctagon className={`w-12 h-12 ml-auto mb-2 ${getScoreColor(score)}`} />
                    )}
                </div>
            </div>

            {/* Summary */}
            <div className="p-5 bg-slate-900 border-b border-slate-800">
                <p className="text-slate-300 font-medium leading-relaxed">
                    {summary || "Scan complete."}
                </p>
            </div>

            {/* Issues List */}
            <div className="p-4 flex-1 overflow-y-auto space-y-4">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider pl-1 mb-2">Detected Vulnerabilities ({issues.length})</h3>

                {issues.length === 0 ? (
                    <div className="p-8 text-center bg-slate-800/50 rounded-lg border border-slate-700/50">
                        <CheckCircle className="w-8 h-8 text-vibe-success mx-auto mb-3 opacity-80" />
                        <p className="text-slate-400">Your code is looking secure! No obvious vibe-fails found.</p>
                    </div>
                ) : (
                    issues.map((issue, idx) => (
                        <IssueCard key={idx} issue={issue} />
                    ))
                )}
            </div>
        </div>
    );
};

// Helper component for individual findings
const IssueCard = ({ issue }) => {
    const [expanded, setExpanded] = useState(false);
    const [copied, setCopied] = useState(false);

    const getSeverityIcon = (sev) => {
        switch (sev?.toUpperCase()) {
            case 'CRITICAL': return <AlertOctagon className="w-5 h-5 text-vibe-danger" />;
            case 'HIGH': return <AlertOctagon className="w-5 h-5 text-rose-400" />;
            case 'MEDIUM': return <AlertTriangle className="w-5 h-5 text-vibe-warning" />;
            default: return <Info className="w-5 h-5 text-blue-400" />;
        }
    };

    const getSeverityColor = (sev) => {
        switch (sev?.toUpperCase()) {
            case 'CRITICAL': return 'border-vibe-danger text-vibe-danger bg-vibe-danger/10';
            case 'HIGH': return 'border-rose-400 text-rose-400 bg-rose-400/10';
            case 'MEDIUM': return 'border-vibe-warning text-vibe-warning bg-vibe-warning/10';
            default: return 'border-blue-400 text-blue-400 bg-blue-400/10';
        }
    };

    const handleCopy = () => {
        if (issue.fixed_code_snippet) {
            navigator.clipboard.writeText(issue.fixed_code_snippet);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="border border-slate-700 bg-slate-800 rounded-lg overflow-hidden transition-all hover:border-slate-600">
            {/* Collapsed Header */}
            <button
                onClick={() => setExpanded(!expanded)}
                className="w-full text-left p-4 flex items-center justify-between hover:bg-slate-750 focus:outline-none"
            >
                <div className="flex items-center gap-3">
                    {getSeverityIcon(issue.severity)}
                    <div>
                        <h4 className="font-semibold text-slate-100">{issue.title || "Vulnerability found"}</h4>
                        <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded border ${getSeverityColor(issue.severity)} mt-1 inline-block`}>
                            {issue.severity || 'LOW'} SEVERITY
                        </span>
                    </div>
                </div>
                {expanded ? <ChevronUp className="text-slate-500 w-5 h-5" /> : <ChevronDown className="text-slate-500 w-5 h-5" />}
            </button>

            {/* Expanded Content */}
            {expanded && (
                <div className="p-4 pt-0 border-t border-slate-700 bg-slate-800/50">
                    <div className="mt-4 mb-3">
                        <p className="text-sm text-slate-300 leading-relaxed shadow-sm">
                            {issue.description}
                        </p>
                    </div>

                    <div className="mt-4 bg-slate-900 rounded-lg border border-slate-700/50 overflow-hidden">
                        <div className="bg-slate-950 px-4 py-2 flex items-center justify-between border-b border-slate-800">
                            <span className="text-xs font-semibold text-vibe-success uppercase tracking-wider flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5" /> How to fix</span>
                        </div>
                        <div className="p-4">
                            <p className="text-sm text-slate-400 mb-3">{issue.how_to_fix}</p>

                            {issue.fixed_code_snippet && (
                                <div className="relative mt-2 group">
                                    <div className="absolute right-2 top-2 z-10 transition-opacity">
                                        <button
                                            onClick={handleCopy}
                                            className="p-1.5 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded border border-slate-600 shadow-sm"
                                            title="Copy fix"
                                        >
                                            {copied ? <Check className="w-3.5 h-3.5 text-vibe-success" /> : <Copy className="w-3.5 h-3.5" />}
                                        </button>
                                    </div>
                                    <pre className="bg-[#0d1117] p-4 pt-8 rounded-md overflow-x-auto text-sm text-blue-300 border border-slate-800 font-mono">
                                        <code>{issue.fixed_code_snippet}</code>
                                    </pre>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ScanResults;
