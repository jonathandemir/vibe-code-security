import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, useMotionTemplate } from 'framer-motion';

export default function TiltCard({ children, className = '' }) {
    const ref = useRef(null);

    // Trail/Glow Parameters (The purple ribbon effect)
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    // We use a lower stiffness/damping here to create a trailing "Schleife" effect
    const smoothMouseX = useSpring(mouseX, { stiffness: 60, damping: 20 });
    const smoothMouseY = useSpring(mouseY, { stiffness: 60, damping: 20 });

    const handleMouseMove = (e) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();

        const currentMouseX = e.clientX - rect.left;
        const currentMouseY = e.clientY - rect.top;

        // Feed precise location for the trailing glow
        mouseX.set(currentMouseX);
        mouseY.set(currentMouseY);
    };

    const handleMouseLeave = () => {
        // Center the glow when leaving
        if (ref.current) {
            const rect = ref.current.getBoundingClientRect();
            mouseX.set(rect.width / 2);
            mouseY.set(rect.height / 2);
        }
    };

    return (
        <motion.div
            ref={ref}
            onMouseMove={handleMouseMove}
            onMouseLeave={handleMouseLeave}
            className={`relative rounded-[2rem] overflow-hidden ${className}`}
        >
            {/* The trailing purple ribbon/glow effect inside the card */}
            <motion.div
                className="pointer-events-none absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 mix-blend-screen z-0"
                style={{
                    background: useMotionTemplate`radial-gradient(400px circle at ${smoothMouseX}px ${smoothMouseY}px, rgba(123, 97, 255, 0.6), transparent 50%)`,
                }}
            />

            <div
                className="w-full h-full flex flex-col items-start justify-between relative z-10"
            >
                {children}
            </div>
        </motion.div>
    );
}
