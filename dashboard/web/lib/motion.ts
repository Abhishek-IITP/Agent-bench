/**
 * Motion utilities for AgentBench Intelligence Center
 * Spring-based animations using Framer Motion
 */

import { type Variants } from 'framer-motion';

/**
 * Spring animation preset for smooth, natural motion
 */
export const spring = {
  type: "spring" as const,
  stiffness: 300,
  damping: 30,
  mass: 0.8,
};

/**
 * Softer spring for delicate animations
 */
export const softSpring = {
  type: "spring" as const,
  stiffness: 200,
  damping: 25,
  mass: 0.5,
};

/**
 * Bouncy spring for playful interactions
 */
export const bouncySpring = {
  type: "spring" as const,
  stiffness: 400,
  damping: 20,
  mass: 0.6,
};

/**
 * Fade in from opacity 0 to 1
 */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: 0.4, ease: [0.16, 1, 0.3, 1] },
  },
};

/**
 * Slide up from below with fade
 */
export const slideUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: spring,
  },
};

/**
 * Slide in from right with fade
 */
export const slideRight: Variants = {
  hidden: { opacity: 0, x: -16 },
  visible: {
    opacity: 1,
    x: 0,
    transition: softSpring,
  },
};

/**
 * Slide in from left with fade
 */
export const slideLeft: Variants = {
  hidden: { opacity: 0, x: 16 },
  visible: {
    opacity: 1,
    x: 0,
    transition: softSpring,
  },
};

/**
 * Scale up from 0.95 to 1
 */
export const scaleIn: Variants = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: spring,
  },
};

/**
 * Grow from 0 to full height (for bars/charts)
 */
export const growHeight: Variants = {
  hidden: { height: 0, opacity: 0 },
  visible: {
    height: "auto",
    opacity: 1,
    transition: spring,
  },
};

/**
 * Expand from 0 to full width (for progress bars)
 */
export const expandWidth: Variants = {
  hidden: { width: 0 },
  visible: (width: string | number) => ({
    width,
    transition: { duration: 1, ease: [0.16, 1, 0.3, 1] },
  }),
};

/**
 * Stagger children animations
 * Supports both function invocation and direct variant object usage
 */
export const staggerContainer: any = (delayChildren = 0, staggerChildren = 0.06): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      delayChildren: typeof delayChildren === 'number' ? delayChildren : 0,
      staggerChildren: typeof staggerChildren === 'number' ? staggerChildren : 0.06,
    },
  },
});

/**
 * Hover lift effect for interactive cards
 */
export const hoverLift = {
  whileHover: {
    y: -2,
    transition: softSpring,
  },
  whileTap: {
    scale: 0.99,
    transition: { duration: 0.1 },
  },
};

/**
 * Pulse animation for live indicators
 */
export const pulse: Variants = {
  initial: { scale: 1, opacity: 1 },
  animate: {
    scale: [1, 1.1, 1],
    opacity: [1, 0.7, 1],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

/**
 * Breathing animation for background elements
 */
export const breathe: Variants = {
  initial: { scale: 1, opacity: 0.3 },
  animate: {
    scale: [1, 1.02, 1],
    opacity: [0.3, 0.5, 0.3],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
};

/**
 * Reveal from behind (for expandable sections)
 */
export const revealBehind: Variants = {
  collapsed: {
    height: 0,
    opacity: 0,
    transition: spring,
  },
  expanded: {
    height: "auto",
    opacity: 1,
    transition: spring,
  },
};

/**
 * Draw line animation (for SVG paths)
 */
export const drawLine = {
  hidden: {
    pathLength: 0,
    opacity: 0,
  },
  visible: {
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: { duration: 1.5, ease: "easeInOut" },
      opacity: { duration: 0.3 },
    },
  },
};

/**
 * Number count-up animation hook
 * @param end - Target number
 * @param duration - Animation duration in ms
 * @param start - Starting number (default 0)
 */
export function useCountUp(end: number, duration = 1400, start = 0) {
  // This is a utility type - actual implementation in components
  return { start, end, duration };
}

/**
 * Easing functions for custom animations
 */
export const easings = {
  // Smooth ease out (recommended for most UI)
  smooth: [0.16, 1, 0.3, 1] as [number, number, number, number],
  // Elastic bounce
  elastic: [0.68, -0.55, 0.265, 1.55] as [number, number, number, number],
  // Sharp ease out
  sharp: [0.4, 0, 0.2, 1] as [number, number, number, number],
  // Linear
  linear: [0, 0, 1, 1] as [number, number, number, number],
};

export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 120, damping: 20 } },
};

export const staggerFast: Variants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.04 } },
};

export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -32 },
  visible: { opacity: 1, x: 0, transition: { type: "spring" as const, stiffness: 100, damping: 18 } },
};

export const wordReveal: Variants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 150, damping: 25 } },
};

/**
 * Viewport reveal configuration for scroll-triggered animations
 */
export const viewportReveal = {
  once: true,
  amount: 0.3,
  margin: "0px 0px -100px 0px",
};
