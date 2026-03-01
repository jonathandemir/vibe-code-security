import React from 'react';
import { Link } from 'react-router-dom';
import { Shield } from 'lucide-react';

export default function Footer() {
    return (
        <footer className="border-t border-white/5 bg-neutral-950/80 mt-auto">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
                    <div className="col-span-1 md:col-span-1">
                        <Link to="/" className="flex items-center space-x-2">
                            <Shield className="w-5 h-5 text-emerald-400" />
                            <span className="text-lg font-bold tracking-tight text-white">VibeGuard</span>
                        </Link>
                        <p className="mt-4 text-sm text-neutral-500">
                            The invisible security engine for Vibe-Coders and Solo Devs. Ship fast, stay secure.
                        </p>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase">Product</h3>
                        <ul className="mt-4 space-y-2">
                            <li><Link to="/product" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Features</Link></li>
                            <li><Link to="/pricing" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Pricing</Link></li>
                            <li><Link to="/dashboard" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Dashboard UI</Link></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase">Company</h3>
                        <ul className="mt-4 space-y-2">
                            <li><Link to="/goal" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Our Goal</Link></li>
                            <li><a href="https://github.com/jonathandemir" target="_blank" rel="noreferrer" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">GitHub</a></li>
                            <li><a href="#" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Twitter (X)</a></li>
                        </ul>
                    </div>

                    <div>
                        <h3 className="text-sm font-semibold text-white tracking-wider uppercase">Legal</h3>
                        <ul className="mt-4 space-y-2">
                            <li><Link to="/legal" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Privacy Policy</Link></li>
                            <li><Link to="/legal" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Terms of Service</Link></li>
                            <li><Link to="/legal" className="text-sm text-neutral-400 hover:text-emerald-400 transition-colors">Imprint</Link></li>
                        </ul>
                    </div>
                </div>
                <div className="mt-12 border-t border-white/5 pt-8 flex items-center justify-between">
                    <p className="text-sm text-neutral-500">
                        &copy; {new Date().getFullYear()} VibeGuard. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
}
