import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform, useMotionTemplate } from 'framer-motion';

export default function TiltCard({ children, className = '' }) {
    const ref = useRef(null);

    // 3D Tilt Parameters
    const xPct = useMotionValue(0);
    const yPct = useMotionValue(0);

    // Trail/Glow Parameters (The purple ribbon effect)
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    // We use a lower stiffness/damping here to create a trailing "Schleife" effect
    const smoothMouseX = useSpring(mouseX, { stiffness: 60, damping: 20 });
    const smoothMouseY = useSpring(mouseY, { stiffness: 60, damping: 20 });

    const mouseXSpring = useSpring(xPct, { stiffness: 200, damping: 20 });
    const mouseYSpring = useSpring(yPct, { stiffness: 200, damping: 20 });

    // Subtle, premium 10 degree tilts
    const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ['10deg', '-10deg']);
    const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ['-10deg', '10deg']);

    const handleMouseMove = (e) => {
        if (!ref.current) return;
        const rect = ref.current.getBoundingClientRect();

        const currentMouseX = e.clientX - rect.left;
        const currentMouseY = e.clientY - rect.top;

        // Feed precise location for the trailing glow
        mouseX.set(currentMouseX);
        mouseY.set(currentMouseY);

        // Feed percentage location for 3D tilt
        const width = rect.width;
        const height = rect.height;
        xPct.set(currentMouseX / width - 0.5);
        yPct.set(currentMouseY / height - 0.5);
    };

    const handleMouseLeave = () => {
        xPct.set(0);
        yPct.set(0);
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
            style={{
                rotateX,
                rotateY,
                transformStyle: 'preserve-3d',
                perspective: 1200
            }}
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
                style={{ transform: 'translateZ(80px)', transformStyle: 'preserve-3d' }}
                className="w-full h-full flex flex-col items-start justify-between relative z-10"
            >
                {children}
            </div>
        </motion.div>
    );
}
