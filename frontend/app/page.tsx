"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import SchemeCarousel from "@/components/SchemeCarousel";
import {
  pageContainer,
  staggerContainer,
  fadeUp,
  fadeIn,
  hoverLift,
  hoverButton,
} from "@/lib/motion";

const EXPLORE_CARDS = [
  {
    icon: "🔍",
    title: "About AccessLens",
    body: "AccessLens v2 is a policy access simulation engine that maps real-world barriers to government scheme eligibility — helping identify who gets left behind.",
  },
  {
    icon: "📋",
    title: "How to Use",
    body: "Fill in your profile on the Input page. The system matches you to a persona, scores your eligibility and risk, and surfaces the most relevant schemes.",
  },
  {
    icon: "⚙️",
    title: "How It Works",
    body: "A multi-layer pipeline combines persona mapping, access risk modelling, and AI-generated explanations to produce transparent, actionable recommendations.",
  },
];

export default function HomePage() {
  return (
    <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-16 space-y-24">

      {/* ── Hero ── */}
      <motion.section
        initial="hidden"
        animate="visible"
        variants={pageContainer}
        className="flex flex-col items-center text-center gap-6"
      >
        <motion.div variants={fadeUp}>
          <div className="inline-flex items-center gap-2 rounded-full border border-brand/30 bg-brand/10 px-4 py-1.5 text-xs font-medium text-brand-soft">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-brand opacity-75" />
              <span className="relative inline-flex h-2 w-2 rounded-full bg-brand" />
            </span>
            Policy Access Simulation
          </div>
        </motion.div>

        <motion.h1
          variants={fadeUp}
          className="text-5xl font-bold tracking-tight text-content-primary sm:text-6xl lg:text-7xl"
        >
          Access
          <span className="text-brand-soft">Lens</span>{" "}
          <span className="text-content-muted">v2</span>
        </motion.h1>

        <motion.p
          variants={fadeUp}
          className="max-w-2xl text-lg text-content-secondary leading-relaxed"
        >
          Policy access simulation &amp; scheme recommendation system. Understand
          your eligibility, identify barriers, and find the schemes that matter
          to you.
        </motion.p>

        <motion.div variants={fadeUp}>
          <motion.div {...hoverButton}>
            <Link href="/input" className="btn btn-primary text-base glow-primary">
              Get Started
              <motion.span
                className="inline-block"
                animate={{ x: [0, 4, 0] }}
                transition={{ repeat: Infinity, duration: 1.6, ease: "easeInOut" }}
              >
                →
              </motion.span>
            </Link>
          </motion.div>
        </motion.div>
      </motion.section>

      {/* ── Carousel Banner ── */}
      <motion.section
        variants={fadeIn}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        className="space-y-4"
      >
        <h2 className="text-2xl font-semibold text-content-primary">Featured Schemes</h2>
        <SchemeCarousel />
      </motion.section>

      {/* ── Explore ── */}
      <motion.section
        variants={fadeIn}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-80px" }}
        className="space-y-6"
      >
        <h2 className="text-2xl font-semibold text-content-primary">Explore</h2>
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-40px" }}
          className="grid gap-6 sm:grid-cols-3"
        >
          {EXPLORE_CARDS.map((card) => (
            <motion.div
              key={card.title}
              variants={fadeUp}
              {...hoverLift}
              className="card card-hover p-6 group cursor-pointer"
            >
              <span className="text-3xl block">{card.icon}</span>
              <h3 className="mt-4 text-base font-semibold text-content-primary group-hover:text-white transition-colors">
                {card.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-content-secondary group-hover:text-content-primary transition-colors">
                {card.body}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </motion.section>

    </main>
  );
}
