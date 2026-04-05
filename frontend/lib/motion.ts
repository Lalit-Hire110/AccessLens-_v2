/**
 * AccessLens v2 — Motion Presets
 * Single source of truth for all Framer Motion animations.
 * Import from here instead of defining inline variants.
 */

import type { Variants, Transition } from "framer-motion";

// ── Transitions ──────────────────────────────────────────────────────────────

export const springSnappy: Transition = {
  type: "spring",
  stiffness: 260,
  damping: 22,
};

export const springGentle: Transition = {
  type: "spring",
  stiffness: 120,
  damping: 18,
};

export const easeFast: Transition = {
  duration: 0.2,
  ease: "easeOut",
};

export const easeMedium: Transition = {
  duration: 0.35,
  ease: "easeOut",
};

// ── Entrance variants ─────────────────────────────────────────────────────────

/** Fade + subtle rise. Use on individual items. */
export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: springGentle,
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: easeFast,
  },
};

/** Fade only. Use on overlays and panels. */
export const fadeIn: Variants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: easeMedium },
  exit:   { opacity: 0, transition: easeFast },
};

/** Stagger container — wraps a list of fadeUp children. */
export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.07,
      delayChildren: 0.05,
    },
  },
};

/** Stagger container with a slightly longer delay (page-level). */
export const pageContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: easeFast,
  },
};

/** Slide in from left. Use on list items with x-axis reveal. */
export const slideInLeft: Variants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0, transition: springGentle },
};

/** Expand height + fade. Use on collapsible panels. */
export const expandPanel: Variants = {
  hidden: { opacity: 0, height: 0 },
  visible: {
    opacity: 1,
    height: "auto",
    transition: { duration: 0.32, ease: "easeOut" },
  },
  exit: {
    opacity: 0,
    height: 0,
    transition: { duration: 0.22, ease: "easeIn" },
  },
};

// ── Interaction props (spread directly onto motion elements) ─────────────────

/** Cards — subtle lift on hover, no scale. */
export const hoverLift = {
  whileHover: { y: -3, transition: easeFast },
  whileTap:   { y: 0,  transition: easeFast },
};

/** Buttons — scale up on hover, scale down on tap. */
export const hoverButton = {
  whileHover: { scale: 1.03, transition: easeFast },
  whileTap:   { scale: 0.97, transition: easeFast },
};

/** Links / small interactive elements — lighter scale. */
export const hoverSubtle = {
  whileHover: { scale: 1.02, transition: easeFast },
  whileTap:   { scale: 0.98, transition: easeFast },
};

/** Scale pop — for badges and icons appearing. */
export const scalePop: Variants = {
  hidden:  { scale: 0, opacity: 0 },
  visible: { scale: 1, opacity: 1, transition: springSnappy },
};
