import React from 'react';
import { BrowserRouter, Routes, Route, useLocation } from 'react-router-dom';
import { AnimatePresence } from 'framer-motion';

// Layout & Effects
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import PageWrapper from './components/layout/PageWrapper';
import CursorGlow from './components/layout/CursorGlow';
import ScrollToTop from './components/layout/ScrollToTop';

// Pages
import Home from './pages/Home';
import Pricing from './pages/Pricing';
import Product from './pages/Product';
import Goal from './pages/Goal';
import Legal from './pages/Legal';
import DashboardApp from './pages/DashboardApp';

function AnimatedRoutes() {
    const location = useLocation();

    return (
        <AnimatePresence mode="wait">
            <Routes location={location} key={location.pathname}>
                <Route path="/" element={<PageWrapper><Home /></PageWrapper>} />
                <Route path="/pricing" element={<PageWrapper><Pricing /></PageWrapper>} />
                <Route path="/product" element={<PageWrapper><Product /></PageWrapper>} />
                <Route path="/goal" element={<PageWrapper><Goal /></PageWrapper>} />
                <Route path="/legal" element={<PageWrapper><Legal /></PageWrapper>} />
                <Route path="/dashboard" element={<PageWrapper><DashboardApp /></PageWrapper>} />
            </Routes>
        </AnimatePresence>
    );
}

function App() {
    return (
        <BrowserRouter>
            <ScrollToTop />
            {/* Main Layout Container */}
            <div className="min-h-screen bg-[#0A0A14] text-[#F0EFF4] font-sans flex flex-col selection:bg-[#7B61FF]/30 z-10 relative">
                {/* Dynamic Cursor Background */}
                <CursorGlow />

                <Navbar />

                <main className="flex-grow flex flex-col">
                    <AnimatedRoutes />
                </main>

                <Footer />
            </div>
        </BrowserRouter>
    );
}

export default App;
