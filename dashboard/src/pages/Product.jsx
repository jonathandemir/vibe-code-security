import React from 'react';
import { motion } from 'framer-motion';
import { Shield, Zap, Lock, Activity, Sparkles, Terminal, FileCode, CheckCircle2, Plus } from 'lucide-react';

const Product = () => {
    // 1. Hero Section for the Product
    // 2. The VibeGuard Scan (SAST targeted at Vibe-Fails)
    // 3. Instant Remediation (One-Click Fix)
    // 4. Privacy-First Architecture (Data Minimization)
    // 5. The Trust Score (0-100)

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.2
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
    };

    return (
        <div className="min-h-screen bg-[#0A0A14] text-slate-200 selection:bg-[#7B61FF]/30 selection:text-[#F0EFF4] font-sans overflow-hidden">

            {/* Ambient Background Glows */}
            <div className="fixed top-0 left-0 w-full h-[500px] bg-gradient-to-b from-[#7B61FF]/10 via-transparent to-transparent pointer-events-none" />
            <div className="fixed top-1/4 right-0 w-[500px] h-[500px] bg-cyan-500/5 rounded-full blur-[120px] pointer-events-none mix-blend-screen" />
            <div className="fixed bottom-0 left-1/4 w-[600px] h-[600px] bg-[#7B61FF]/5 rounded-full blur-[150px] pointer-events-none mix-blend-screen" />

            {/* Hero Section */}
            <header className="relative pt-32 pb-20 px-6 max-w-7xl mx-auto text-center z-10">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 backdrop-blur-md mb-8 shadow-[0_0_20px_rgba(123,97,255,0.2)]">
                        <Sparkles className="w-4 h-4 text-[#7B61FF]" />
                        <span className="text-sm font-medium tracking-wide text-slate-300">The Anatomy of VibeGuard</span>
                    </div>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
                    className="text-5xl md:text-7xl font-sans font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-[#F0EFF4] via-[#F0EFF4]/90 to-[#7B61FF] pb-4 mb-6 leading-tight"
                >
                    Precision Engineering <br className="hidden md:block" />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-slate-400 to-slate-600 font-drama tracking-normal">for Gen-AI Development.</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="text-xl md:text-2xl text-slate-400 max-w-3xl mx-auto leading-relaxed"
                >
                    We didn't just build another scanner. We built the first defensive layer explicitly trained to catch the unique hallucinations, lazy auth, and critical mistakes made by modern LLMs.
                </motion.p>
            </header>

            {/* Features Staggered Grid */}
            <motion.main
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                className="max-w-7xl mx-auto px-6 py-20 z-10 relative space-y-32"
            >
                {/* Feature 1: The VibeGuard Scan */}
                <motion.section variants={itemVariants} className="grid md:grid-cols-2 gap-12 items-center">
                    <div>
                        <div className="text-xs font-mono text-[#7B61FF] mb-4 uppercase tracking-widest border border-[#7B61FF]/30 inline-flex px-2 py-1 rounded bg-[#7B61FF]/5 items-center gap-2 shadow-[0_0_15px_rgba(123,97,255,0.15)]">
                            <Shield className="w-3.5 h-3.5" /> Core Engine
                        </div>
                        <h2 className="text-4xl font-bold text-[#F0EFF4] mb-6 tracking-tight">The VibeGuard Scan</h2>

                        <div className="group cursor-pointer">
                            <div className="flex items-center gap-2 text-[#7B61FF] mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                <Plus className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
                                <span className="font-mono text-sm uppercase tracking-wider">Reveal Details</span>
                            </div>
                            <div className="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                                <div className="overflow-hidden">
                                    <p className="text-lg text-slate-400 leading-relaxed mb-6 pt-4">
                                        A calibrated SAST engine built for the AI era. Legacy tools hunt outdated enterprise flaws. We hunt <b className="text-[#F0EFF4]">"Vibe-Fails"</b>: Claude's injected API keys, ChatGPT's missing auth wrappers, and wide-open CORS policies.
                                    </p>
                                    <ul className="space-y-4 pb-4">
                                        {['Catches LLM Hallucinations', 'Detects Lazy Authentication', 'Identifies Hardcoded Secrets'].map((item, i) => (
                                            <li key={i} className="flex items-center gap-3 text-slate-300">
                                                <CheckCircle2 className="w-5 h-5 text-[#7B61FF]" />
                                                <span>{item}</span>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Visual 1 */}
                    <div className="glass-panel p-8 rounded-[2rem] border border-[#7B61FF]/20 bg-[#0A0A14]/80 shadow-[0_0_50px_rgba(123,97,255,0.15)] relative group transition-all duration-500 hover:shadow-[0_0_80px_rgba(123,97,255,0.3)] hover:-translate-y-2">
                        <div className="absolute inset-0 bg-gradient-to-br from-[#7B61FF]/10 to-transparent rounded-[2rem] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                        <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-4 relative z-10">
                            <div className="flex items-center gap-2 text-slate-400 font-mono text-sm">
                                <Terminal className="w-4 h-4" /> scanner.py
                            </div>
                            <span className="text-xs font-mono text-vibe-danger bg-vibe-danger/10 px-2 py-1 rounded border border-vibe-danger/20 animate-pulse shadow-[0_0_15px_rgba(239,68,68,0.3)]">
                                1 CRITICAL VIBE-FAIL DETECTED
                            </span>
                        </div>
                        <pre className="font-mono text-sm text-slate-300 overflow-x-auto relative z-10 p-2">
                            <code>
                                <span className="text-pink-400">@app.post</span><span className="text-yellow-300">("/admin/delete")</span>{'\n'}
                                <span className="text-emerald-400">def</span> <span className="text-blue-400">delete_user</span>(user_id: int):{'\n'}
                                {'    '}<span className="text-slate-500"># Generated by LLM - MISSING AUTH!</span>{'\n'}
                                {'    '}db.execute(<span className="text-yellow-300">f"DELETE FROM users WHERE id=`{`{user_id}`}`"</span>){'\n'}
                            </code>
                        </pre>
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5 }}
                            className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-xs font-mono relative z-10"
                        >
                            {'>'} ALERT: Missing authentication dependency on mutation endpoint.
                        </motion.div>
                    </div>
                </motion.section>

                {/* Feature 2: Instant Remediation */}
                <motion.section variants={itemVariants} className="grid md:grid-cols-2 gap-12 items-center">

                    {/* Visual 2 */}
                    <div className="order-2 md:order-1 glass-panel p-8 rounded-[2rem] border border-emerald-400/20 bg-[#0A0A14]/80 shadow-[0_0_50px_rgba(52,211,153,0.15)] relative group transition-all duration-500 hover:shadow-[0_0_80px_rgba(52,211,153,0.3)] hover:-translate-y-2">
                        <div className="absolute inset-0 bg-gradient-to-bl from-emerald-400/10 to-transparent rounded-[2rem] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                        <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-4 relative z-10">
                            <div className="flex items-center gap-2 text-slate-400 font-mono text-sm">
                                <FileCode className="w-4 h-4" /> patch_ready (Actor-Critic)
                            </div>
                            <span className="text-xs font-mono text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded border border-emerald-400/20 shadow-[0_0_15px_rgba(52,211,153,0.3)]">
                                VALIDIERT
                            </span>
                        </div>
                        <pre className="font-mono text-sm text-slate-300 overflow-x-auto relative z-10 p-2 leading-loose">
                            <code>
                                <span className="text-red-400 opacity-50">- @app.post("/admin/delete")</span>{'\n'}
                                <motion.span initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} transition={{ duration: 1 }} className="text-emerald-400 block bg-emerald-400/10 border-l border-emerald-400 pl-2 -ml-2">+ @app.post("/admin/delete", dependencies=[Depends(verify_admin)])</motion.span>
                                <span className="text-slate-400">  def delete_user(user_id: int):</span>{'\n'}
                            </code>
                        </pre>
                        <motion.button
                            whileHover={{ scale: 1.02, boxShadow: '0 0 30px rgba(52,211,153,0.4)' }}
                            whileTap={{ scale: 0.98 }}
                            className="mt-6 w-full py-4 bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/40 text-emerald-400 rounded-xl font-mono text-sm flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(52,211,153,0.15)] relative z-10"
                        >
                            <Zap className="w-5 h-5" /> Apply One-Click Fix
                        </motion.button>
                    </div>

                    <div className="order-1 md:order-2">
                        <div className="text-xs font-mono text-emerald-400 mb-4 uppercase tracking-widest border border-emerald-400/30 inline-flex px-2 py-1 rounded bg-emerald-400/5 items-center gap-2 shadow-[0_0_15px_rgba(52,211,153,0.15)]">
                            <Zap className="w-3.5 h-3.5" /> Premium Tooling
                        </div>
                        <h2 className="text-4xl font-bold text-[#F0EFF4] mb-6 tracking-tight">Instant Remediation</h2>

                        <div className="group cursor-pointer">
                            <div className="flex items-center gap-2 text-emerald-400 mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                <Plus className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
                                <span className="font-mono text-sm uppercase tracking-wider">Reveal Details</span>
                            </div>
                            <div className="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                                <div className="overflow-hidden">
                                    <p className="text-lg text-slate-400 leading-relaxed mb-6 pt-4">
                                        Knowing you have a vulnerability is only half the battle. Our <b>Actor-Critic AI</b> generates the exact, context-aware code patch needed to fix flaws instantly.
                                    </p>
                                    <p className="text-lg text-slate-400 leading-relaxed pb-4">
                                        Click a button, merge the PR. We translate cryptic CLI logs (H2H-Reporting) into clear, immediate remedies.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.section>

                {/* Feature 3: Privacy Architecture */}
                <motion.section variants={itemVariants} className="grid md:grid-cols-2 gap-12 items-center">
                    <div>
                        <div className="text-xs font-mono text-cyan-400 mb-4 uppercase tracking-widest border border-cyan-400/30 inline-flex px-2 py-1 rounded bg-cyan-400/5 items-center gap-2 shadow-[0_0_15px_rgba(34,211,238,0.15)]">
                            <Lock className="w-3.5 h-3.5" /> Core Value
                        </div>
                        <h2 className="text-4xl font-bold text-[#F0EFF4] mb-6 tracking-tight">Privacy-First Architecture</h2>

                        <div className="group cursor-pointer">
                            <div className="flex items-center gap-2 text-cyan-400 mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                <Plus className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
                                <span className="font-mono text-sm uppercase tracking-wider">Reveal Details</span>
                            </div>
                            <div className="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                                <div className="overflow-hidden">
                                    <p className="text-lg text-slate-400 leading-relaxed mb-6 pt-4">
                                        Your code is your moat. We built our architecture around strict data minimisation for modern AI development.
                                    </p>
                                    <p className="text-lg text-slate-400 leading-relaxed pb-4">
                                        Code snippets are processed in-memory and never persisted to long-term storage or used to train external models. Security that respects your IP.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Visual 3 */}
                    <div className="glass-panel p-10 h-80 rounded-[2rem] border border-cyan-400/20 bg-[#0A0A14]/80 shadow-[0_0_50px_rgba(34,211,238,0.15)] flex items-center justify-center relative overflow-hidden group transition-all duration-500 hover:shadow-[0_0_80px_rgba(34,211,238,0.3)] hover:-translate-y-2">
                        <div className="absolute inset-0 bg-gradient-to-tr from-cyan-400/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700 mix-blend-screen" />

                        {/* Abstract Privacy Graphic */}
                        <div className="relative w-48 h-48 flex items-center justify-center">
                            <motion.div
                                animate={{ rotate: 360 }}
                                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-0 border-2 border-dashed border-cyan-400/40 rounded-full"
                            />
                            <motion.div
                                animate={{ rotate: -360 }}
                                transition={{ duration: 15, repeat: Infinity, ease: "linear" }}
                                className="absolute inset-4 border border-cyan-400/20 rounded-full"
                            />
                            <div className="absolute flex flex-col items-center justify-center">
                                <Lock className="w-12 h-12 text-cyan-400 mb-2 drop-shadow-[0_0_15px_rgba(34,211,238,0.8)]" />
                                <span className="text-xs font-mono text-cyan-400 font-bold tracking-widest bg-cyan-400/10 px-2 py-0.5 rounded">ENCRYPTED</span>
                            </div>
                        </div>
                    </div>
                </motion.section>

                {/* Feature 4: Trust Score */}
                <motion.section variants={itemVariants} className="glass-panel p-12 md:p-20 rounded-[3rem] border border-[#7B61FF]/30 bg-gradient-to-b from-[#18181B]/90 to-[#0A0A14] text-center relative overflow-hidden shadow-[0_0_100px_rgba(123,97,255,0.15)]">
                    <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/stardust.png')] opacity-10 pointer-events-none" />
                    <div className="absolute inset-0 bg-gradient-radial from-[#7B61FF]/10 to-transparent pointer-events-none" />

                    <div className="relative z-10 max-w-3xl mx-auto">
                        <Activity className="w-16 h-16 text-[#7B61FF] mx-auto mb-6 drop-shadow-[0_0_20px_rgba(123,97,255,0.5)]" />
                        <h2 className="text-4xl md:text-5xl font-bold text-[#F0EFF4] mb-8 tracking-tight">The Trust Score</h2>
                        <p className="text-xl text-slate-400 leading-relaxed mb-16">
                            Stop guessing if your app is safe to deploy. Get a definitive, real-time security score from 0 to 100 on every commit, backed by an actionable priority list.
                        </p>

                        <div className="flex justify-center items-end gap-6 font-mono h-48 border-b border-slate-700 pb-0">
                            <motion.div
                                initial={{ height: 0 }}
                                whileInView={{ height: '40%' }}
                                transition={{ duration: 1, ease: "easeOut" }}
                                className="w-20 bg-red-500/20 rounded-t-xl relative flex items-start justify-center pt-4 border-x border-t border-red-500/40 shadow-[0_0_20px_rgba(239,68,68,0.2)]"
                            >
                                <span className="text-red-400 font-bold text-lg drop-shadow-[0_0_10px_rgba(239,68,68,0.8)]">34</span>
                            </motion.div>
                            <motion.div
                                initial={{ height: 0 }}
                                whileInView={{ height: '70%' }}
                                transition={{ duration: 1, delay: 0.2, ease: "easeOut" }}
                                className="w-20 bg-yellow-500/20 rounded-t-xl relative flex items-start justify-center pt-4 border-x border-t border-yellow-500/40 shadow-[0_0_20px_rgba(245,158,11,0.2)]"
                            >
                                <span className="text-yellow-400 font-bold text-lg drop-shadow-[0_0_10px_rgba(245,158,11,0.8)]">72</span>
                            </motion.div>
                            <motion.div
                                initial={{ height: 0 }}
                                whileInView={{ height: '100%' }}
                                transition={{ duration: 1, delay: 0.4, ease: "easeOut" }}
                                className="w-24 bg-emerald-500/20 rounded-t-xl relative flex items-start justify-center pt-6 border-x border-t border-emerald-500/50 shadow-[0_0_30px_rgba(52,211,153,0.3)]"
                            >
                                <motion.div
                                    animate={{ scale: [1, 1.1, 1] }}
                                    transition={{ repeat: Infinity, duration: 2 }}
                                    className="text-emerald-400 font-bold text-4xl drop-shadow-[0_0_20px_rgba(52,211,153,0.9)]"
                                >
                                    98
                                </motion.div>
                            </motion.div>
                        </div>
                    </div>
                </motion.section>

            </motion.main>
        </div>
    );
};

export default Product;
