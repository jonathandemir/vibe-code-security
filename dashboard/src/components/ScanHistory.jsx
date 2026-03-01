import React from 'react';
import { motion } from 'framer-motion';
import { Clock, Trash2, Shield, ShieldAlert, ShieldCheck, FileCode, FolderArchive } from 'lucide-react';

function getScoreColor(score) {
    if (score >= 95) return 'text-emerald-400';
    if (score >= 80) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    if (score >= 30) return 'text-red-400';
    return 'text-red-600';
}

function getScoreBg(score) {
    if (score >= 95) return 'bg-emerald-500/10 border-emerald-500/20';
    if (score >= 80) return 'bg-yellow-500/10 border-yellow-500/20';
    if (score >= 60) return 'bg-orange-500/10 border-orange-500/20';
    if (score >= 30) return 'bg-red-500/10 border-red-500/20';
    return 'bg-red-900/20 border-red-500/30';
}

function getScoreIcon(score) {
    if (score >= 80) return <ShieldCheck className="w-4 h-4" />;
    if (score >= 50) return <Shield className="w-4 h-4" />;
    return <ShieldAlert className="w-4 h-4" />;
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function ScanHistory({ scans, onSelect, onDelete, activeScanId }) {
    if (!scans || scans.length === 0) {
        return (
            <div className="glass-panel p-4 text-center text-slate-500">
                <Clock className="w-8 h-8 mx-auto mb-2 text-slate-600" />
                <p className="text-sm">No scans yet</p>
                <p className="text-xs mt-1 text-slate-600">Run your first scan to see it here.</p>
            </div>
        );
    }

    return (
        <div className="glass-panel p-3 space-y-1.5 max-h-[600px] overflow-y-auto">
            <div className="flex items-center gap-2 px-2 pb-2 border-b border-slate-700 mb-2">
                <Clock className="w-4 h-4 text-vibe-accent" />
                <h3 className="text-sm font-semibold text-slate-300">Scan History</h3>
                <span className="ml-auto text-xs text-slate-500">{scans.length}</span>
            </div>

            {scans.map((scan) => (
                <motion.div
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    key={scan.id}
                    onClick={() => onSelect(scan.id)}
                    className={`group flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-colors duration-150 ${activeScanId === scan.id
                        ? 'bg-vibe-accent/10 border border-vibe-accent/30'
                        : 'hover:bg-slate-800/60 border border-transparent'
                        }`}
                >
                    {/* Score Badge */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-lg border flex flex-col items-center justify-center ${getScoreBg(scan.score)}`}>
                        <span className={`text-xs font-bold ${getScoreColor(scan.score)}`}>
                            {scan.score}
                        </span>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-1.5">
                            {scan.scan_type === 'repo' ? (
                                <FolderArchive className="w-3 h-3 text-slate-400 flex-shrink-0" />
                            ) : (
                                <FileCode className="w-3 h-3 text-slate-400 flex-shrink-0" />
                            )}
                            <span className="text-xs font-medium text-slate-300 truncate">
                                {scan.scan_type === 'repo' ? 'Repo Scan' : 'Snippet Scan'}
                            </span>
                        </div>
                        <div className="flex items-center gap-1.5 mt-0.5">
                            <span className="text-[10px] text-slate-500 uppercase">{scan.language}</span>
                            <span className="text-[10px] text-slate-600">•</span>
                            <span className="text-[10px] text-slate-500">{formatTimestamp(scan.created_at)}</span>
                        </div>
                    </div>

                    {/* Delete button */}
                    <motion.button
                        whileHover={{ scale: 1.1 }}
                        whileTap={{ scale: 0.9 }}
                        onClick={(e) => {
                            e.stopPropagation();
                            onDelete(scan.id);
                        }}
                        className="flex-shrink-0 p-1.5 rounded-md text-slate-600 hover:text-red-400 hover:bg-red-500/10 opacity-0 group-hover:opacity-100 transition-colors"
                        title="Delete scan"
                    >
                        <Trash2 className="w-3.5 h-3.5" />
                    </motion.button>
                </motion.div>
            ))}
        </div>
    );
}

export default ScanHistory;
