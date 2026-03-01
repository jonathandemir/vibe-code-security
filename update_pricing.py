import re

with open('dashboard/src/pages/Pricing.jsx', 'r') as f:
    content = f.read()

# I want to replace the FAQ part to add a question about Fast Scans vs Deep Fixes.
new_faq = """const QA = [
    { q: "What is the difference between a Fast Scan and a Deep Auto-Fix?", a: "A 'Fast Scan' uses highly optimized AI models (Gemini Flash) to quickly identify vulnerabilities in your code. A 'Deep Auto-Fix' uses deep reasoning models (Gemini Pro) to actually write and verify the exact code patch needed to fix the issue." },
    { q: "What is a 'Vibe-Fail'?", a: "A Vibe-Fail is a common security mistake made when rapidly prototyping with AI coding tools. This includes hardcoded secrets, open CORS rules, or missing authentication." },
    { q: "How does the GitHub Action work?", a: "You drop `uses: jonathandemir/vibe-code-security@main` into your `.github/workflows/` file. It automatically zips your code, scans it via our API, and posts plain-English fixes directly to the PR comment." },
    { q: "Can I upgrade or downgrade anytime?", a: "Yes, billing is managed via Stripe. You can cancel, upgrade, or downgrade your plan directly from the dashboard settings at any time." },
];"""

content = re.sub(r'const QA = \[\n.*?\];', new_faq, content, flags=re.DOTALL)

# Replace the pricing cards inside <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 items-start mb-32 relative">
cards_new = """            {/* Pricing Cards */}
            <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 items-start mb-16 relative">

                {/* Tier 1: Hobby */}
                <motion.div
                    whileHover={{ y: -8 }}
                    className="glass-panel p-8 relative flex flex-col h-full bg-[#18181B]/40 transition-shadow hover:shadow-[0_0_40px_rgba(255,255,255,0.05)]"
                >
                    <div className="mb-8 border-b border-white/5 pb-8">
                        <h3 className="text-2xl font-sans font-bold text-[#F0EFF4]">Hobby</h3>
                        <p className="text-sm font-sans text-neutral-400 mt-2">Find the flaws. Fix them yourself.</p>
                        <div className="mt-6 flex items-baseline text-[#F0EFF4]">
                            <span className="text-6xl font-sans font-extrabold tracking-tight">$0</span>
                            <span className="ml-1 text-xl font-sans font-medium text-neutral-500">/mo</span>
                        </div>
                    </div>

                    <ul className="space-y-5 mb-12 flex-grow">
                        {['10 Fast Scans / month', '0 Deep Auto-Fixes', 'Community Discord support', 'Standard Dashboard Access'].map((feature, i) => (
                            <li key={i} className="flex items-start">
                                <div className="mt-1 flex-shrink-0 w-4 h-4 rounded-full border border-[#7B61FF]/30 flex items-center justify-center bg-[#7B61FF]/10 mr-4">
                                    <Check className="w-2.5 h-2.5 text-[#7B61FF]" />
                                </div>
                                <span className={feature.includes('0 Deep Auto-Fixes') ? "text-sm font-sans text-neutral-500 line-through leading-tight" : "text-sm font-sans text-neutral-300 leading-tight"}>{feature}</span>
                            </li>
                        ))}
                    </ul>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="btn-magnetic w-full py-4 px-4 rounded-full bg-white/5 border border-white/10 text-[#F0EFF4] font-sans font-semibold hover:bg-white/10 transition-colors"
                    >
                        Start for free
                    </motion.button>
                </motion.div>

                {/* Tier 2: Micro */}
                <motion.div
                    whileHover={{ y: -8 }}
                    className="glass-panel p-8 relative flex flex-col h-full bg-[#18181B]/60 border-white/10 transition-shadow hover:shadow-[0_0_40px_rgba(255,255,255,0.05)]"
                >
                    <div className="mb-8 border-b border-white/5 pb-8">
                        <h3 className="text-2xl font-sans font-bold text-[#F0EFF4]">Micro</h3>
                        <p className="text-sm font-sans text-neutral-400 mt-2">The Starbucks coffee for the Indie Hacker.</p>
                        <div className="mt-6 flex items-baseline text-[#F0EFF4]">
                            <span className="text-6xl font-sans font-extrabold tracking-tight">$5</span>
                            <span className="ml-1 text-xl font-sans font-medium text-neutral-500">/mo</span>
                        </div>
                    </div>

                    <ul className="space-y-5 mb-12 flex-grow">
                        {['50 Fast Scans / month', '10 Deep Auto-Fixes / month', 'GitHub PR Bot Integration', '+ Add-On Credits Available'].map((feature, i) => (
                            <li key={i} className="flex items-start">
                                <div className="mt-1 flex-shrink-0 w-4 h-4 rounded-full border border-[#7B61FF]/30 flex items-center justify-center bg-[#7B61FF]/10 mr-4">
                                    <Check className="w-2.5 h-2.5 text-[#7B61FF]" />
                                </div>
                                <span className="text-sm font-sans text-neutral-300 leading-tight">{feature}</span>
                            </li>
                        ))}
                    </ul>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="btn-magnetic w-full py-4 px-4 rounded-full bg-white/10 border border-white/10 text-white font-sans font-semibold shadow-[0_0_20px_rgba(255,255,255,0.05)] hover:shadow-[0_0_30px_rgba(255,255,255,0.1)] transition-shadow"
                    >
                        Subscribe to Micro
                    </motion.button>
                </motion.div>

                {/* Tier 3: Pro (Highlighted) */}
                <motion.div
                    whileHover={{ y: -8 }}
                    className="glass-panel p-8 relative flex flex-col h-full border-[#7B61FF]/30 shadow-[0_0_40px_rgba(123,97,255,0.1)] hover:shadow-[0_0_60px_rgba(123,97,255,0.25)] bg-[#18181B]/80 md:-translate-y-4 transition-shadow"
                >
                    <div className="absolute top-0 inset-x-0 h-1 bg-gradient-to-r from-[#7B61FF] to-cyan-400 rounded-t-[2rem]" />

                    <div className="mb-8 border-b border-white/5 pb-8">
                        <div className="flex justify-between items-center">
                            <h3 className="text-2xl font-sans font-bold text-[#F0EFF4]">Pro</h3>
                            <span className="px-3 py-1 rounded-full bg-[#7B61FF]/20 text-[#7B61FF] text-[10px] font-mono font-bold uppercase tracking-widest border border-[#7B61FF]/30">Most Popular</span>
                        </div>
                        <p className="text-sm font-sans text-neutral-400 mt-2">For the productive Vibe-Coder.</p>
                        <div className="mt-6 flex items-baseline text-[#F0EFF4]">
                            <span className="text-6xl font-sans font-extrabold tracking-tight">$15</span>
                            <span className="ml-1 text-xl font-sans font-medium text-neutral-500">/mo</span>
                        </div>
                    </div>

                    <ul className="space-y-5 mb-12 flex-grow">
                        {['300 Fast Scans / month', '50 Deep Auto-Fixes / month', 'Priority email support', '+ Add-On Credits Available'].map((feature, i) => (
                            <li key={i} className="flex items-start">
                                <div className="mt-1 flex-shrink-0 w-4 h-4 rounded-full border border-[#7B61FF]/30 flex items-center justify-center bg-[#7B61FF]/10 mr-4">
                                    <Check className="w-2.5 h-2.5 text-[#7B61FF]" />
                                </div>
                                <span className="text-sm font-sans text-neutral-300 leading-tight">{feature}</span>
                            </li>
                        ))}
                    </ul>

                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="btn-magnetic w-full py-4 px-4 rounded-full bg-[#7B61FF] text-white font-sans font-bold shadow-[0_0_20px_rgba(123,97,255,0.4)] hover:shadow-[0_0_30px_rgba(123,97,255,0.6)] transition-shadow"
                    >
                        Subscribe to Pro
                    </motion.button>
                </motion.div>
            </div>
            
            {/* Pay As You Go Banner */}
            <div className="max-w-4xl mx-auto mb-32 relative z-10">
                <div className="glass-panel p-8 md:p-10 rounded-[2rem] border border-cyan-400/20 bg-cyan-900/10 flex flex-col md:flex-row items-center justify-between gap-8 hover:shadow-[0_0_40px_rgba(34,211,238,0.15)] transition-shadow">
                    <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-cyan-400/5 to-transparent rounded-b-[2rem] pointer-events-none" />
                    <div className="flex-1">
                        <div className="text-xs font-mono text-cyan-400 mb-2 uppercase tracking-widest border border-cyan-400/30 inline-block px-2 py-1 rounded bg-cyan-400/5">
                            Need More Power?
                        </div>
                        <h3 className="text-2xl font-sans font-bold text-[#F0EFF4] mb-2">Expansion Credits (Pay-As-You-Go)</h3>
                        <p className="text-neutral-400 font-sans leading-relaxed text-sm">
                            Hitting your monthly limit? No problem. You can always top up your account with more tokens without changing your subscription tier. Perfect for intense prototyping weekends.
                        </p>
                    </div>
                    <div className="shrink-0 flex flex-col gap-3">
                        <div className="flex items-center gap-4 bg-[#0A0A14] p-4 rounded-xl border border-white/5">
                            <span className="text-3xl font-sans font-bold text-[#F0EFF4]">$10</span>
                            <div className="text-left text-sm text-neutral-400 font-sans leading-tight">
                                = <span className="text-[#F0EFF4] font-medium">50 Deep Fixes</span><br/>
                                or <span className="text-[#F0EFF4] font-medium">100 Fast Scans</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>"""

content = re.sub(r'\{\/\* Pricing Cards \*\/\}.*?<\/div>(\s*)\{\/\* FAQ Section \*\/\}', cards_new + r'\1{/* FAQ Section */}', content, flags=re.DOTALL)

with open('dashboard/src/pages/Pricing.jsx', 'w') as f:
    f.write(content)

print("Updated Pricing.jsx successfully")
