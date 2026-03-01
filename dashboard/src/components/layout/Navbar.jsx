import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Shield, ChevronRight } from 'lucide-react';

export default function Navbar() {
    const location = useLocation();
    const isDashboard = location.pathname === '/dashboard';
    const [scrolled, setScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => {
            setScrolled(window.scrollY > 50);
        };
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    return (
        <nav className={`fixed top-0 w-full z-50 transition-all duration-500 flex justify-center py-4 px-4 ${scrolled ? 'mt-0' : 'mt-4'}`}>
            <div
                className={`flex justify-between items-center w-full max-w-5xl rounded-full px-6 transition-all duration-500 overflow-hidden relative ${scrolled
                    ? 'h-16 bg-[#0A0A14]/70 backdrop-blur-xl border border-white/10 shadow-2xl'
                    : 'h-20 bg-transparent border-transparent'
                    }`}
            >
                <Link to="/" className="flex items-center space-x-2 group z-10">
                    <div className="p-1.5 rounded-full bg-[#7B61FF]/10 border border-[#7B61FF]/20 group-hover:bg-[#7B61FF]/30 transition-colors">
                        <Shield className="w-5 h-5 text-[#7B61FF]" />
                    </div>
                    <span className="text-lg font-sans font-bold tracking-tight text-[#F0EFF4] group-hover:text-[#7B61FF] transition-colors">
                        VibeGuard
                    </span>
                </Link>

                <div className="hidden md:flex space-x-8 z-10">
                    <Link to="/product" className="text-sm font-sans font-medium text-neutral-400 hover:text-[#F0EFF4] transition-colors">Product</Link>
                    <Link to="/goal" className="text-sm font-sans font-medium text-neutral-400 hover:text-[#F0EFF4] transition-colors">Goal</Link>
                    <Link to="/pricing" className="text-sm font-sans font-medium text-neutral-400 hover:text-[#F0EFF4] transition-colors">Pricing</Link>
                </div>

                <div className="flex items-center space-x-4 z-10">
                    {!isDashboard && (
                        <Link
                            to="/dashboard"
                            className="btn-magnetic flex items-center space-x-1 px-5 py-2 rounded-full bg-[#7B61FF]/10 text-[#7B61FF] border border-[#7B61FF]/20 hover:bg-[#7B61FF]/20 hover:shadow-[0_0_20px_rgba(123,97,255,0.4)] transition-all text-sm font-sans font-semibold tracking-tight"
                        >
                            <span>Initialize App</span>
                            <ChevronRight className="w-4 h-4" />
                        </Link>
                    )}
                    {isDashboard && (
                        <a href="https://github.com/vibeguard-hq/vibe-code-security" target="_blank" rel="noreferrer" className="text-sm font-sans font-medium text-neutral-400 hover:text-[#F0EFF4] transition-colors">
                            GitHub
                        </a>
                    )}
                </div>
            </div>
        </nav>
    );
}
