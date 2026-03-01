import React, { useState, useEffect } from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { useNavigate, Link } from 'react-router-dom';
import { Terminal, Shield, Workflow, Lock, GitBranch, Search, CheckCircle, Zap, Code2, ArrowRight, ShieldCheck, Heart, Globe, Rocket } from 'lucide-react';
import TiltCard from '../components/ui/TiltCard';

export default function Home() {
    const navigate = useNavigate();
    const [inputValue, setInputValue] = useState('');
    const { scrollYProgress } = useScroll();

    // Hero Parallax
    const heroY = useTransform(scrollYProgress, [0, 1], ['0%', '50%']);
    const heroOpacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);

    const handleScan = (e) => {
        e.preventDefault();
        if (inputValue.trim()) navigate('/dashboard');
    };

    return (
        <div className="w-full bg-[#0A0A14] overflow-x-hidden selection:bg-[#7B61FF]/30">

            {/* =========================================
          SECTION A: HERO "The Opening Shot"
          ========================================= */}
            <section className="relative w-full h-[100dvh] flex items-end justify-start pb-24 md:pb-32 px-4 sm:px-8 lg:px-16 overflow-hidden">
                {/* Background Image & Gradient */}
                <motion.div
                    style={{ y: heroY, opacity: heroOpacity }}
                    className="absolute inset-0 z-0 pointer-events-none"
                >
                    {/* Unsplash abstract biotech/neon water image */}
                    <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1557672172-298e090bd0f1?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-screen opacity-40 grayscale" />
                    <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=2000&auto=format&fit=crop')] bg-cover bg-center mix-blend-color-dodge opacity-20" />
                    {/* Heavy gradient to dark */}
                    <div className="absolute inset-0 bg-gradient-to-t from-[#0A0A14] via-[#0A0A14]/80 to-transparent" />
                </motion.div>

                {/* Hero Content */}
                <div className="relative z-10 w-full max-w-7xl mx-auto flex flex-col md:flex-row items-end justify-between gap-12">

                    <div className="max-w-3xl">
                        <motion.div
                            initial={{ opacity: 0, y: 50, filter: 'blur(10px)' }}
                            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                            transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
                        >
                            <h1 className="flex flex-col mb-8">
                                <span className="text-4xl md:text-6xl font-sans font-semibold text-[#F0EFF4] tracking-tight">
                                    Security beyond
                                </span>
                                <span className="text-6xl md:text-8xl lg:text-9xl font-drama text-[#7B61FF] leading-[0.85] mt-2">
                                    human oversight.
                                </span>
                            </h1>
                        </motion.div>

                        <motion.p
                            initial={{ opacity: 0, y: 30, filter: 'blur(5px)' }}
                            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                            transition={{ duration: 1, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
                            className="text-lg md:text-xl text-neutral-400 font-sans max-w-xl mb-12"
                        >
                            The invisible security engine for Vibe-Coders. Ship AI-generated code 10x faster without the critical vulnerabilities.
                        </motion.p>
                    </div>

                    {/* Lead Magnet Interactive Box */}
                    <motion.div
                        initial={{ opacity: 0, x: 30, filter: 'blur(5px)' }}
                        animate={{ opacity: 1, x: 0, filter: 'blur(0px)' }}
                        transition={{ duration: 1, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
                        className="w-full md:w-auto relative group"
                    >
                        <div className="absolute -inset-1 bg-[#7B61FF] rounded-full blur-xl opacity-20 group-hover:opacity-40 transition duration-1000" />
                        <form onSubmit={handleScan} className="relative bg-[#18181B]/80 backdrop-blur-xl border border-white/10 rounded-full p-2 flex items-center shadow-2xl">
                            <div className="pl-4 pr-2 text-neutral-500">
                                <Terminal className="w-5 h-5 text-[#7B61FF]" />
                            </div>
                            <input
                                type="text"
                                placeholder="Paste repo URL..."
                                className="bg-transparent border-none text-[#F0EFF4] font-mono text-sm focus:outline-none placeholder-neutral-600 py-3 w-48 md:w-64"
                                value={inputValue}
                                onChange={(e) => setInputValue(e.target.value)}
                            />
                            <button
                                type="submit"
                                className="btn-magnetic bg-[#F0EFF4] text-[#0A0A14] hover:text-black px-6 py-3 rounded-full font-semibold font-sans tracking-tight flex items-center space-x-2"
                            >
                                <span>Initialize</span>
                            </button>
                        </form>
                    </motion.div>
                </div>
            </section>

            {/* =========================================
          SECTION B: THE MANIFESTO (Slide Technique)
          ========================================= */}
            <section className="relative w-full min-h-fit px-4 sm:px-8 lg:px-16 pt-24 md:pt-32 pb-8 border-t border-white/5">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-16 relative">

                    {/* Left Column (Sticky Problem Statement) */}
                    <div className="w-full md:w-5/12 md:sticky md:top-32 h-fit">
                        <motion.div
                            initial={{ opacity: 0, x: -30 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.8 }}
                        >
                            <div className="text-xs font-mono text-rose-400 mb-6 uppercase tracking-widest border border-rose-400/30 inline-block px-3 py-1.5 rounded bg-rose-400/5">
                                Our Manifesto
                            </div>
                            <h2 className="text-4xl md:text-5xl font-sans font-semibold text-[#F0EFF4] tracking-tight mb-6">
                                Security shouldn't be<br />
                                <span className="text-neutral-500">an enterprise luxury.</span>
                            </h2>
                            <p className="text-lg text-neutral-400 font-sans leading-relaxed mb-8">
                                Traditional security tools are built for massive DevOps teams. They cost thousands, require complex CI/CD tuning, and vomit false-positives that paralyze solo developers.
                                <br /><br />
                                Generative AI has killed the execution barrier, but the stigma remains: <span className="text-rose-400">"AI code is insecure."</span> We are here to change that.
                            </p>
                        </motion.div>
                    </div>

                    {/* Right Column (Scrolling Slide Cards) */}
                    <div className="w-full md:w-7/12 flex flex-col gap-8 md:pt-12 pb-4 z-10">

                        {/* Slide 1 */}
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.8 }}
                        >
                            <div className="glass-panel p-8 md:p-12 rounded-[2rem] border border-white/5 bg-[#0A0A14]/90 backdrop-blur-xl group hover:border-[#7B61FF]/80 hover:shadow-[0_0_80px_rgba(123,97,255,0.5)] transform hover:-translate-y-4 transition-all duration-500 relative">
                                {/* Inner Glow */}
                                <div className="absolute inset-0 rounded-[2rem] bg-[#7B61FF]/0 group-hover:bg-[#7B61FF]/10 transition-colors duration-500 pointer-events-none" />
                                <div className="text-[#7B61FF] font-mono text-sm mb-4 relative z-10">01 // The Solution</div>
                                <h3 className="text-3xl font-sans font-semibold text-[#F0EFF4] mb-4 relative z-10">Security for Everyone, <span className="text-neutral-500">Accessible to All.</span></h3>
                                <p className="text-neutral-400 font-sans relative z-10">
                                    We are the <strong>first affordable security model</strong> designed explicitly for the AI generation. Robust defense shouldn't require VC funding. Get enterprise-grade SAST scanning for the price of a Spotify subscription.
                                </p>
                            </div>
                        </motion.div>

                        {/* Slide 2 */}
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.8 }}
                        >
                            <div className="glass-panel p-8 md:p-12 rounded-[2rem] border border-white/5 bg-[#0A0A14]/90 backdrop-blur-xl group hover:border-cyan-400/80 hover:shadow-[0_0_80px_rgba(34,211,238,0.5)] transform hover:-translate-y-4 transition-all duration-500 relative">
                                {/* Inner Glow */}
                                <div className="absolute inset-0 rounded-[2rem] bg-cyan-400/0 group-hover:bg-cyan-400/10 transition-colors duration-500 pointer-events-none" />
                                <div className="text-cyan-400 font-mono text-sm mb-4 relative z-10">02 // The Execution</div>
                                <h3 className="text-3xl font-sans font-semibold text-[#F0EFF4] mb-4 relative z-10">Set it & <span className="text-neutral-500">Forget it.</span></h3>
                                <p className="text-neutral-400 font-sans relative z-10">
                                    Zero-configuration multi-layer systems. We provide clear, human-readable answers and exact code fixes. <strong>No CISO degree required.</strong> Drop in the proxy, hook up the GitHub Action, and VibeGuard handles the rest on autopilot.
                                </p>
                            </div>
                        </motion.div>

                        {/* Slide 3 */}
                        <motion.div
                            initial={{ opacity: 0, y: 50 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.8 }}
                        >
                            <div className="glass-panel p-8 md:p-12 rounded-[2rem] border border-white/5 bg-[#0A0A14]/90 backdrop-blur-xl group hover:border-emerald-400/80 hover:shadow-[0_0_80px_rgba(52,211,153,0.5)] transform hover:-translate-y-4 transition-all duration-500 relative">
                                {/* Inner Glow */}
                                <div className="absolute inset-0 rounded-[2rem] bg-emerald-400/0 group-hover:bg-emerald-400/10 transition-colors duration-500 mix-blend-screen pointer-events-none" />
                                <div className="text-emerald-400 font-mono text-sm mb-4 relative z-10">03 // The Vision</div>
                                <h3 className="text-3xl font-sans font-semibold text-[#F0EFF4] mb-4 relative z-10">Code without <span className="text-neutral-500">Handbrakes.</span></h3>
                                <p className="text-neutral-400 font-sans relative z-10">
                                    Deploy your generative apps confidently. It's time to kill the stigma against AI-written code. Utilize the full capabilities of modern LLMs—we provide the invisible guardrails to keep you safe.
                                </p>
                            </div>
                        </motion.div>

                    </div>
                </div>
            </section>

            {/* =========================================
          SECTION B.5: THE DEMO (Video / Terminal Placeholder)
          ========================================= */}
            <section className="relative w-full pt-4 pb-32 px-4 sm:px-8 lg:px-16 flex justify-center bg-[#0A0A14] overflow-hidden">
                {/* Background glow for this specific section */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] bg-cyan-400/5 rounded-[100%] blur-[120px] pointer-events-none" />

                <div className="max-w-6xl w-full relative z-10">
                    <div className="text-center mb-16">
                        <div className="text-xs font-mono text-[#7B61FF] mb-4 uppercase tracking-widest border border-[#7B61FF]/30 inline-block px-3 py-1.5 rounded bg-[#7B61FF]/5">
                            See It In Action
                        </div>
                        <h2 className="text-3xl md:text-5xl font-sans font-semibold text-[#F0EFF4] tracking-tight">
                            Watch VibeGuard <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">Secure Code</span>
                        </h2>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 40 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8 }}
                        className="relative rounded-3xl overflow-hidden glass-panel border border-white/10 aspect-video flex items-center justify-center bg-[#0A0A14] group cursor-pointer shadow-[0_0_80px_rgba(0,0,0,0.5)]"
                    >
                        {/* Shimmer sweep effect */}
                        <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none" />

                        {/* Play Button */}
                        <div className="absolute z-20 w-24 h-24 rounded-full bg-[#7B61FF]/20 border border-[#7B61FF]/50 flex items-center justify-center backdrop-blur-md group-hover:scale-110 group-hover:bg-[#7B61FF]/40 transition-all duration-500 shadow-[0_0_60px_rgba(123,97,255,0.4)]">
                            <div className="w-0 h-0 border-t-[12px] border-t-transparent border-l-[20px] border-l-[#F0EFF4] border-b-[12px] border-b-transparent ml-2" />
                        </div>

                        {/* Fake Code / Terminal Background Pattern */}
                        <div className="absolute inset-x-0 bottom-0 h-2/3 bg-gradient-to-t from-[#0A0A14] to-transparent z-10 pointer-events-none" />

                        <div className="absolute inset-0 p-8 md:p-12 font-mono text-sm md:text-base text-cyan-400/40 pointer-events-none select-none blur-[1px] group-hover:blur-0 transition-all duration-700">
                            <p className="mb-2">~ {">"} git push origin main</p>
                            <p className="mb-2 text-neutral-500">Enumerating objects: 5, done.</p>
                            <p className="mb-2 text-neutral-500">Counting objects: 100% (5/5), done.</p>
                            <p className="mb-2 text-neutral-500">Writing objects: 100% (3/3), 1.2 KiB | 1.2 MiB/s, done.</p>
                            <p className="mb-6 text-[#7B61FF]/60">Total 3 (delta 1), reused 0 (delta 0)</p>

                            <motion.div animate={{ opacity: [0.5, 1, 0.5] }} transition={{ repeat: Infinity, duration: 2 }}>
                                <p className="mb-2 text-rose-400/80">{"[VibeGuard]"} Intercepting push event...</p>
                            </motion.div>

                            <p className="mb-2">{"[VibeGuard]"} Scanning for logic flaws & AI-hallucinated secrets...</p>
                            <p className="mb-2">{"[VibeGuard]"} Analyzing diff...</p>
                            <p className="mt-4 text-emerald-400/80">{"[VibeGuard]"} 1 Issue found. Auto-generating secure patch via Gemini Pro...</p>
                        </div>
                    </motion.div>
                </div>
            </section>

            {/* =========================================
          SECTION C: FEATURES "Interactive Artifacts"
          ========================================= */}
            <section className="w-full py-32 px-4 sm:px-8 lg:px-16 border-t border-white/5 relative">
                <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-24 bg-gradient-to-b from-[#7B61FF]/50 to-transparent" />

                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6">

                    {/* Feature 1: The Scanner */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-50px" }}
                        transition={{ duration: 0.6 }}
                        className="h-full"
                    >
                        <TiltCard className="glass-panel p-8 h-full min-h-[26rem] flex flex-col justify-between group">
                            <div className="p-3 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-[#7B61FF] shadow-2xl w-max mb-6">
                                <Shield className="w-6 h-6" />
                            </div>
                            <div>
                                <div className="text-xs font-mono text-[#7B61FF] mb-3 uppercase tracking-widest border border-[#7B61FF]/30 inline-block px-2 py-1 rounded bg-[#7B61FF]/5">Zero-Config Security</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">300-Second Shield</h3>
                                <p className="text-neutral-400 font-sans text-sm">Send raw code or zip files. Get an instant security score with copy-paste fixes formatted for AI generation in under 5 minutes.</p>
                            </div>
                        </TiltCard>
                    </motion.div>

                    {/* Feature 2: Runtime SDK */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-50px" }}
                        transition={{ duration: 0.6, delay: 0.2 }}
                        className="h-full"
                    >
                        <TiltCard className="glass-panel p-8 h-full min-h-[26rem] flex flex-col justify-between group">
                            <div className="p-3 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-cyan-400 shadow-2xl w-max mb-6">
                                <Lock className="w-6 h-6" />
                            </div>
                            <div className="w-full">
                                <div className="bg-[#0A0A14] border border-white/5 rounded-lg p-4 font-mono text-[10px] text-cyan-400/80 mb-6 h-28 overflow-hidden relative shadow-inner">
                                    <div className="absolute inset-x-0 bottom-0 h-12 bg-gradient-to-t from-[#0A0A14] to-transparent z-10" />
                                    <motion.div
                                        animate={{ y: [-20, 0] }}
                                        transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
                                        className="pt-4"
                                    >
                                        <p className="mb-1">{">"} initializing secure proxy...</p>
                                        <p className="mb-1 text-neutral-500">{">"} block: missing auth header [401]</p>
                                        <p className="mb-1 text-emerald-400 bg-emerald-400/10 inline-block">{">"} traffic sanitized.</p>
                                        <p className="mb-1">{">"} heartbeat normal...</p>
                                        <p className="mb-1 text-neutral-500">{">"} drop: malformed jwt payload [400]</p>
                                    </motion.div>
                                </div>
                                <div className="text-xs font-mono text-cyan-400 mb-3 uppercase tracking-widest border border-cyan-400/30 inline-block px-2 py-1 rounded bg-cyan-400/5">Precision Engine</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">Actor-Critic Filter</h3>
                                <p className="text-neutral-400 font-sans text-sm">Beyond simple scanning. Our dual-model architecture evaluates and then rigorously critiques every generated fix before showing it to you.</p>
                            </div>
                        </TiltCard>
                    </motion.div>

                    {/* Feature 3: Action Protocol */}
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-50px" }}
                        transition={{ duration: 0.6, delay: 0.4 }}
                        className="h-full"
                    >
                        <TiltCard className="glass-panel p-8 h-full min-h-[26rem] flex flex-col justify-between group">
                            <div className="p-3 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-emerald-400 shadow-2xl w-max mb-6">
                                <Workflow className="w-6 h-6" />
                            </div>
                            <div className="w-full">
                                <div className="text-xs font-mono text-emerald-400 mb-3 uppercase tracking-widest border border-emerald-400/30 inline-block px-2 py-1 rounded bg-emerald-400/5">Clear Communication</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">H2H Reporting</h3>
                                <p className="text-neutral-400 font-sans text-sm">Human-to-Human reporting. We translate cryptic CLI output and CVE jargon into plain English and immediately actionable code patches.</p>
                            </div>
                        </TiltCard>
                    </motion.div>

                </div>
            </section>

            {/* =========================================
          SECTION D: ACTION PROTOCOL "How it works"
          ========================================= */}
            <section className="relative w-full py-32 px-4 sm:px-8 lg:px-16 border-t border-white/5 bg-[#0A0A14] flex flex-col items-center justify-center">
                <div className="max-w-4xl w-full mx-auto">
                    <div className="text-center mb-20">
                        <div className="text-xs font-mono text-[#7B61FF] mb-4 uppercase tracking-widest border border-[#7B61FF]/30 inline-block px-3 py-1.5 rounded bg-[#7B61FF]/5">
                            Action Protocol
                        </div>
                        <h2 className="text-4xl md:text-5xl font-sans font-semibold text-[#F0EFF4] tracking-tight">
                            Invisible Security.<br />
                            <span className="text-neutral-500">In three simple steps.</span>
                        </h2>
                    </div>

                    <div className="flex flex-col gap-6 relative">
                        {/* Connecting Line */}
                        <div className="absolute left-[3.25rem] top-10 bottom-10 w-px bg-gradient-to-b from-[#7B61FF]/50 via-cyan-400/50 to-emerald-400/50 hidden md:block" />

                        {/* Step 1 */}
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.6 }}
                            className="glass-panel p-8 rounded-[2rem] border border-white/5 bg-[#18181B]/40 group hover:bg-[#18181B]/80 hover:border-[#7B61FF]/40 hover:shadow-[0_0_40px_rgba(123,97,255,0.15)] transition-all duration-500 flex flex-col md:flex-row gap-8 items-start relative z-10"
                        >
                            <div className="w-16 h-16 shrink-0 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-neutral-500 group-hover:text-[#7B61FF] group-hover:shadow-[0_0_20px_rgba(123,97,255,0.3)] transition-all duration-500 flex items-center justify-center relative">
                                <GitBranch className="w-7 h-7 relative z-10" />
                            </div>
                            <div>
                                <div className="text-[#7B61FF] font-mono text-sm mb-2">Step 01</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">Commit Code</h3>
                                <p className="text-neutral-400 font-sans leading-relaxed">
                                    Write your Vibe-Code and push to GitHub as normal. There are no new CLI tools to learn and no dashboard required to trigger a scan.
                                </p>
                            </div>
                        </motion.div>

                        {/* Step 2 */}
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.6, delay: 0.2 }}
                            className="glass-panel p-8 rounded-[2rem] border border-white/5 bg-[#18181B]/40 group hover:bg-[#18181B]/80 hover:border-cyan-400/40 hover:shadow-[0_0_40px_rgba(34,211,238,0.15)] transition-all duration-500 flex flex-col md:flex-row gap-8 items-start relative z-10"
                        >
                            <div className="w-16 h-16 shrink-0 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-neutral-500 group-hover:text-cyan-400 group-hover:shadow-[0_0_20px_rgba(34,211,238,0.3)] transition-all duration-500 flex items-center justify-center relative">
                                <Search className="w-7 h-7 relative z-10" />
                            </div>
                            <div>
                                <div className="text-cyan-400 font-mono text-sm mb-2">Step 02</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">Silent Scan</h3>
                                <p className="text-neutral-400 font-sans leading-relaxed">
                                    Our GitHub Action catches your push and silently runs a highly-optimized SAST analysis in the background, specifically curated for LLM vulnerabilities.
                                </p>
                            </div>
                        </motion.div>

                        {/* Step 3 */}
                        <motion.div
                            initial={{ opacity: 0, x: -50 }}
                            whileInView={{ opacity: 1, x: 0 }}
                            viewport={{ once: true, margin: "-100px" }}
                            transition={{ duration: 0.6, delay: 0.4 }}
                            className="glass-panel p-8 rounded-[2rem] border border-white/5 bg-[#18181B]/40 group hover:bg-[#18181B]/80 hover:border-emerald-400/40 hover:shadow-[0_0_40px_rgba(52,211,153,0.15)] transition-all duration-500 flex flex-col md:flex-row gap-8 items-start relative z-10"
                        >
                            <div className="w-16 h-16 shrink-0 rounded-2xl bg-[#0A0A14] border border-white/5 border-b-white/10 text-neutral-500 group-hover:text-emerald-400 group-hover:shadow-[0_0_20px_rgba(52,211,153,0.3)] transition-all duration-500 flex items-center justify-center relative">
                                <CheckCircle className="w-7 h-7 relative z-10" />
                            </div>
                            <div>
                                <div className="text-emerald-400 font-mono text-sm mb-2">Step 03</div>
                                <h3 className="text-2xl font-sans font-semibold text-[#F0EFF4] mb-3">Auto-Fix PR</h3>
                                <p className="text-neutral-400 font-sans leading-relaxed">
                                    Instead of a vague report, VibeGuard comments directly on your Pull Request containing the exact, copy-pasteable code required to fix the vulnerability.
                                </p>
                            </div>
                        </motion.div>

                    </div>
                </div>
            </section>

            {/* =========================================
          SECTION E: FROM WEEKEND TO PRODUCTION (The Core Promise)
          ========================================= */}
            <section className="relative w-full py-32 px-4 sm:px-8 lg:px-16 border-t border-white/5 bg-[#0A0A14] overflow-hidden">
                {/* Background glow for this specific section */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[#7B61FF]/10 rounded-full blur-[120px] pointer-events-none" />

                <div className="max-w-6xl mx-auto relative z-10">
                    <motion.div
                        initial={{ opacity: 0, y: 30 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true, margin: "-100px" }}
                        transition={{ duration: 0.8 }}
                        className="glass-panel p-10 md:p-16 lg:p-24 rounded-[3rem] border border-[#7B61FF]/30 bg-[#18181B]/80 text-center relative shadow-[0_0_80px_rgba(123,97,255,0.15)] overflow-hidden group hover:border-[#7B61FF]/60 transition-colors duration-700"
                    >
                        {/* Shimmer sweep effect */}
                        <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_2s_infinite] bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none" />

                        <div className="inline-flex items-center justify-center p-4 bg-[#7B61FF]/10 border border-[#7B61FF]/30 rounded-2xl mb-8 group-hover:scale-110 transition-transform duration-500">
                            <Rocket className="w-8 h-8 text-[#7B61FF]" />
                        </div>

                        <h2 className="text-4xl md:text-6xl font-sans font-bold text-[#F0EFF4] tracking-tight mb-8 leading-tight">
                            Stop keeping your AI apps <br className="hidden md:block" />
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-rose-400 to-[#7B61FF]">stuck on localhost.</span>
                        </h2>

                        <p className="text-xl md:text-2xl text-slate-300 font-sans leading-relaxed max-w-3xl mx-auto mb-12">
                            Generative AI makes it incredibly fun to build projects in hours. But the fear of getting hacked keeps them hidden.
                            <strong> VibeGuard gives you the absolute confidence to actually publish.</strong> Turn your weekend side-projects into production-ready apps without the anxiety.
                        </p>

                        <div className="flex flex-col sm:flex-row items-center justify-center gap-6">
                            <Link to="/dashboard">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="btn-magnetic w-full sm:w-auto px-10 py-5 rounded-full bg-white text-black font-sans font-bold text-lg flex items-center justify-center gap-3 transition-colors hover:bg-neutral-200"
                                >
                                    <Globe className="w-6 h-6" /> Publish with Confidence
                                </motion.button>
                            </Link>
                            <Link to="/product">
                                <motion.button
                                    whileHover={{ scale: 1.05 }}
                                    whileTap={{ scale: 0.95 }}
                                    className="px-10 py-5 rounded-full bg-transparent border border-white/20 text-[#F0EFF4] font-sans font-semibold text-lg flex items-center justify-center gap-3 hover:bg-white/5 transition-colors"
                                >
                                    See How it Works
                                </motion.button>
                            </Link>
                        </div>
                    </motion.div>
                </div>
            </section>

        </div>
    );
}
