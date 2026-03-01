import React from 'react';
import { motion } from 'framer-motion';

const pageVariants = {
    initial: {
        opacity: 0,
        y: 10,
        filter: 'blur(10px)',
    },
    in: {
        opacity: 1,
        y: 0,
        filter: 'blur(0px)',
    },
    out: {
        opacity: 0,
        y: -10,
        filter: 'blur(10px)',
    },
};

const pageTransition = {
    type: 'tween',
    ease: [0.16, 1, 0.3, 1], // Cinematic ease out
    duration: 0.5,
};

export default function PageWrapper({ children }) {
    return (
        <motion.div
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
            className="w-full flex-grow flex flex-col"
        >
            {children}
        </motion.div>
    );
}
