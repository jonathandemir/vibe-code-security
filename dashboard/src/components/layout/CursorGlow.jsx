import React, { useEffect, useRef } from 'react';

export default function CursorGlow() {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationFrameId;

        // Configuration for the "Neon Laser" effect
        const config = {
            thickness: 3,             // Base width of the laser core
            glowSize: 15,             // The neon bloom size
            glowColor: '#9370FF',     // VibeGuard Purple Neon
            fadeSpeed: 0.05           // How fast the trail vanishes (higher = faster)
        };

        const history = [];

        // Handle window resize for full screen canvas
        const resize = () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        };

        const updateMousePosition = (e) => {
            history.push({
                x: e.clientX,
                y: e.clientY,
                life: 1.0 // Start full opacity
            });
        };

        // Render loop
        const draw = () => {
            // Clear canvas completely each frame
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Update life of all points and remove dead ones
            for (let i = 0; i < history.length; i++) {
                history[i].life -= config.fadeSpeed;
            }
            while (history.length > 0 && history[0].life <= 0) {
                history.shift();
            }

            if (history.length > 1) {
                // Setup the neon glow effect
                ctx.shadowBlur = config.glowSize;
                ctx.shadowColor = config.glowColor;
                ctx.lineCap = 'round';
                ctx.lineJoin = 'round';

                // We draw the path segment by segment to fade it out towards the end
                for (let i = 1; i < history.length; i++) {
                    const point = history[i];
                    const prevPoint = history[i - 1];

                    ctx.beginPath();
                    ctx.moveTo(prevPoint.x, prevPoint.y);
                    ctx.lineTo(point.x, point.y);

                    // Fade the line width and opacity towards the tail based on remaining life
                    const lifeRatio = Math.max(0, point.life);

                    // Draw a thicker colored stroke underneath for intense bloom
                    ctx.lineWidth = (config.thickness + 4) * lifeRatio;
                    ctx.strokeStyle = `rgba(147, 112, 255, ${lifeRatio * 0.8})`;
                    ctx.stroke();

                    // Draw the core glowing stroke (white hot center)
                    ctx.lineWidth = config.thickness * lifeRatio;
                    ctx.strokeStyle = `rgba(255, 255, 255, ${lifeRatio})`;
                    ctx.stroke();
                }
            }

            animationFrameId = requestAnimationFrame(draw);
        };

        // Initialize setup
        resize();
        window.addEventListener('resize', resize);
        window.addEventListener('mousemove', updateMousePosition);

        // Start animation loop
        draw();

        return () => {
            window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', updateMousePosition);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="pointer-events-none fixed inset-0 z-40 w-full h-full mix-blend-screen"
        />
    );
}
