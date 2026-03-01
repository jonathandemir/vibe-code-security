import React from 'react';
import { motion, useScroll, useTransform } from 'framer-motion';
import { Target, Rocket, Layers, ArrowRight, ShieldCheck, Database, Zap, Plus } from 'lucide-react';

const Goal = () => {
    // Scroll setup for the sticky 'Infrastructure' visualization
    const { scrollYProgress } = useScroll();
    const layer1Y = useTransform(scrollYProgress, [0, 1], [0, 150]);
    const layer2Y = useTransform(scrollYProgress, [0, 1], [0, 50]);

    const containerVariants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.15
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 30 },
        visible: { opacity: 1, y: 0, transition: { duration: 0.7, ease: "easeOut" } }
    };

    return (
        <div className="min-h-screen bg-[#0A0A14] text-slate-200 selection:bg-[#7B61FF]/30 selection:text-[#F0EFF4] font-sans pb-32">

            {/* Dark abstract overlay */}
            <div className="fixed inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI0IiBoZWlnaHQ9IjQiPgo8cmVjdCB3aWR0aD0iNCIgaGVpZ2h0PSI0IiBmaWxsPSIjZmZmIiBmaWxsLW9wYWNpdHk9IjAuMDUiLz4KPC9zdmc+')] opacity-[0.03] pointer-events-none" />
            <div className="fixed top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

            {/* Header: The "Why" */}
            <header className="relative pt-40 pb-20 px-6 max-w-5xl mx-auto text-center z-10">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                >
                    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-orange-500/20 bg-orange-500/5 mb-8">
                        <Target className="w-4 h-4 text-orange-400" />
                        <span className="text-sm font-medium tracking-wide text-orange-400">The Purpose</span>
                    </div>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.1, ease: "easeOut" }}
                    className="text-5xl md:text-7xl font-sans font-extrabold tracking-tight text-[#F0EFF4] pb-2 mb-6"
                >
                    Secure by <span className="text-transparent bg-clip-text bg-gradient-to-br from-orange-400 to-rose-500">Default.</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
                    className="text-xl md:text-2xl text-slate-400 max-w-2xl mx-auto leading-relaxed"
                >
                    We exist because traditional security tools were built for DevOps engineers, not Solo Founders. We are here to change that.
                </motion.p>
            </header>

            <motion.main
                variants={containerVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                className="max-w-6xl mx-auto px-6 relative z-10 space-y-32"
            >
                {/* Section 1: Move Fast, Stay Safe */}
                <motion.section variants={itemVariants} className="glass-panel p-10 md:p-16 rounded-[2rem] border border-white/5 bg-[#18181B]/60 shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden group">
                    <div className="absolute top-0 right-0 w-96 h-96 bg-rose-500/10 rounded-full blur-[100px] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        <div>
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                                    <Rocket className="w-6 h-6 text-rose-400" />
                                </div>
                                <h2 className="text-3xl font-bold text-[#F0EFF4]">Move Fast, <span className="text-rose-400 text-shadow-sm shadow-rose-500/20">Stay Safe.</span></h2>
                            </div>

                            <div className="group cursor-pointer">
                                <div className="flex items-center gap-2 text-rose-400 mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                    <Plus className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
                                    <span className="font-mono text-sm uppercase tracking-wider">Reveal Details</span>
                                </div>
                                <div className="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                                    <div className="overflow-hidden">
                                        <p className="text-lg text-slate-400 leading-relaxed mb-6 pt-4">
                                            AI generative tools let Solo Developers ship features at blistering speeds. Yet, retrofitting security often brings velocity to a halt.
                                        </p>
                                        <p className="text-lg text-slate-400 leading-relaxed pb-4">
                                            Don't choose between speed and safety. VibeGuard operates silently in the background, providing zero-friction protection so you can keep shipping.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="relative h-64 border border-white/10 rounded-2xl bg-[#0A0A14] overflow-hidden flex items-center justify-center group-hover:border-rose-500/30 transition-colors">
                            <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyMCIgaGVpZ2h0PSI0MCI+CjxwYXRoIGQ9Ik0wIDIwaDIwIiBzdHJva2U9IiNmZmYiIHN0cm9rZS1vcGFjaXR5PSIwLjA1IiBmaWxsPSJub25lIi8+Cjwvc3ZnPg==')] opacity-20 pointer-events-none" />
                            <motion.div
                                className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-[0_0_40px_rgba(255,255,255,0.3)] z-10 relative"
                                animate={{ x: [-100, 100, -100] }}
                                transition={{ duration: 4, ease: "easeInOut", repeat: Infinity }}
                            >
                                <Rocket className="w-8 h-8 text-black" />
                            </motion.div>
                            <div className="absolute bottom-4 left-4 right-4 flex justify-between text-xs font-mono text-slate-600">
                                <span>Speed</span>
                                <span>Safety</span>
                            </div>
                        </div>
                    </div>
                </motion.section>

                {/* Section 2: Infrastructure, not Tooling */}
                <motion.section variants={itemVariants} className="relative">
                    <div className="text-center mb-16">
                        <h2 className="text-3xl md:text-5xl font-bold text-[#F0EFF4] mb-6">Infrastructure, <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">not Tooling.</span></h2>
                        <p className="text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
                            Security shouldn't be a dashboard you manage. It should be an invisible layer you trust. We're doing for Code Security what <b className="text-slate-200">Stripe</b> did for Payments.
                        </p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-6 text-center">
                        {[
                            { icon: Database, title: "The Old Way", desc: "Clunky CLI tools, hours of configuration, and noisy CVE dashboards that require a CISO to decipher.", color: "text-slate-500", border: "border-slate-800" },
                            { icon: ArrowRight, title: "The Transition", desc: "Removing the friction. Moving from proactive hunting to reactive, automated defense.", color: "text-[#7B61FF]", border: "border-transparent" },
                            { icon: Layers, title: "The VibeGuard Way", desc: "A silent proxy. A GitHub Action. You push code, we fix the vulnerabilities before the merge. No dashboards unless you want them.", color: "text-indigo-400", border: "border-indigo-500/30" }
                        ].map((card, i) => (
                            <motion.div
                                key={i}
                                whileHover={{ scale: 1.02, y: -5 }}
                                className={`glass-panel p-8 rounded-2xl border ${card.border} bg-[#0A0A14]/50 flex flex-col items-center transition-all`}
                            >
                                <card.icon className={`w-8 h-8 mb-4 ${card.color}`} />
                                <h3 className="text-lg font-bold text-slate-200 mb-2">{card.title}</h3>
                                <p className="text-sm text-slate-400 leading-relaxed">{card.desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </motion.section>

                {/* Section 3: Sustainable AI-Scale */}
                <motion.section variants={itemVariants} className="glass-panel p-10 md:p-16 rounded-[2rem] border border-white/5 bg-[#18181B]/60 shadow-[0_0_50px_rgba(0,0,0,0.5)] relative overflow-hidden group">
                    <div className="absolute bottom-0 left-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] opacity-0 group-hover:opacity-100 transition-opacity duration-700 pointer-events-none" />
                    <div className="grid md:grid-cols-2 gap-12 items-center">
                        <div className="order-2 md:order-1 relative h-64 border border-white/10 rounded-2xl bg-[#0A0A14] overflow-hidden flex flex-col items-center justify-center p-6 group-hover:border-emerald-500/30 transition-colors">
                            <Zap className="w-12 h-12 text-emerald-400 mb-4 opacity-80" />
                            <div className="flex w-full items-center justify-between text-xs font-mono text-slate-500 mb-2">
                                <span>Flash Router</span>
                                <span>250 RPD</span>
                            </div>
                            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden mb-6">
                                <motion.div
                                    className="h-full bg-emerald-500"
                                    initial={{ width: "0%" }}
                                    whileInView={{ width: "80%" }}
                                    transition={{ duration: 1.5, ease: "easeOut", delay: 0.5 }}
                                />
                            </div>

                            <div className="flex w-full items-center justify-between text-xs font-mono text-slate-500 mb-2">
                                <span>Pro Router</span>
                                <span>100 RPD</span>
                            </div>
                            <div className="w-full h-1.5 bg-slate-800 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-[#7B61FF]"
                                    initial={{ width: "0%" }}
                                    whileInView={{ width: "40%" }}
                                    transition={{ duration: 1.5, ease: "easeOut", delay: 0.7 }}
                                />
                            </div>
                        </div>
                        <div className="order-1 md:order-2">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                                    <Zap className="w-6 h-6 text-emerald-400" />
                                </div>
                                <h2 className="text-3xl font-bold text-[#F0EFF4]">Sustainable <span className="text-emerald-400 text-shadow-sm shadow-emerald-500/20">AI-Scale.</span></h2>
                            </div>

                            <div className="group cursor-pointer">
                                <div className="flex items-center gap-2 text-emerald-400 mb-2 opacity-80 group-hover:opacity-100 transition-opacity">
                                    <Plus className="w-4 h-4 group-hover:rotate-45 transition-transform duration-300" />
                                    <span className="font-mono text-sm uppercase tracking-wider">Reveal Details</span>
                                </div>
                                <div className="grid grid-rows-[0fr] group-hover:grid-rows-[1fr] transition-[grid-template-rows] duration-500 ease-out">
                                    <div className="overflow-hidden">
                                        <p className="text-lg text-slate-400 leading-relaxed mb-6 pt-4">
                                            Our "Tiered Routing" architecture ensures VibeGuard handles massive volume effortlessly.
                                        </p>
                                        <p className="text-lg text-slate-400 leading-relaxed pb-4">
                                            We load-balance API requests between fast and deep-reasoning models, maximizing power and speed without hitting rate limits or exploding costs.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </motion.section>

            </motion.main>
        </div>
    );
};

export default Goal;
