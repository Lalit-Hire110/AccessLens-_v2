"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const SCHEMES = [
  {
    title: "PM-KISAN",
    description:
      "Direct income support of ₹6,000/year to small and marginal farmers across India.",
    link: "https://pmkisan.gov.in",
  },
  {
    title: "Ayushman Bharat",
    description:
      "Health coverage up to ₹5 lakh per family per year for secondary and tertiary care.",
    link: "https://pmjay.gov.in",
  },
  {
    title: "PM Awas Yojana",
    description:
      "Affordable housing for urban and rural poor — subsidised loans and direct grants.",
    link: "https://pmaymis.gov.in",
  },
  {
    title: "MGNREGS",
    description:
      "Guaranteed 100 days of wage employment per year to rural households.",
    link: "https://nrega.nic.in",
  },
  {
    title: "Scholarship Schemes",
    description:
      "Central and state scholarships for SC/ST/OBC students at all education levels.",
    link: "https://scholarships.gov.in",
  },
];

export default function SchemeCarousel() {
  const [active, setActive] = useState(0);
  const [direction, setDirection] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setDirection(1);
      setActive((prev) => (prev + 1) % SCHEMES.length);
    }, 4000);
    return () => clearInterval(timer);
  }, []);

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 300 : -300,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      x: direction > 0 ? -300 : 300,
      opacity: 0,
    }),
  };

  return (
    <div className="card relative overflow-hidden p-6 min-h-[200px]">
      <AnimatePresence initial={false} custom={direction} mode="wait">
        <motion.div
          key={active}
          custom={direction}
          variants={slideVariants}
          initial="enter"
          animate="center"
          exit="exit"
          transition={{
            x: { type: "spring", stiffness: 300, damping: 30 },
            opacity: { duration: 0.3 },
          }}
          className="flex flex-col justify-between"
        >
          <div>
            <motion.span
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-block rounded-full bg-brand/15 px-3 py-1 text-xs font-medium text-brand-soft border border-brand/25"
            >
              Featured Scheme
            </motion.span>
            <motion.h3
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.3 }}
              className="mt-3 text-xl font-semibold text-content-primary"
            >
              {SCHEMES[active].title}
            </motion.h3>
            <motion.p
              initial={{ y: 10, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-3 text-sm leading-relaxed text-content-secondary"
            >
              {SCHEMES[active].description}
            </motion.p>
          </div>
          <motion.a
            initial={{ y: 10, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.5 }}
            href={SCHEMES[active].link}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-flex items-center gap-1 text-sm font-medium text-brand-soft hover:text-brand transition-colors group"
          >
            Learn more
            <motion.span
              className="inline-block"
              animate={{ x: [0, 4, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
            >
              →
            </motion.span>
          </motion.a>
        </motion.div>
      </AnimatePresence>

      {/* Progress dots */}
      <div className="flex justify-center gap-2 mt-6">
        {SCHEMES.map((_, idx) => (
          <button
            key={idx}
            onClick={() => {
              setDirection(idx > active ? 1 : -1);
              setActive(idx);
            }}
            aria-label={`Go to slide ${idx + 1}`}
            className="group relative"
          >
            <motion.div
              className={`h-1.5 rounded-full transition-all duration-300 ${
                idx === active ? "w-8 bg-brand" : "w-1.5 bg-border-default"
              }`}
              whileHover={{ scale: 1.2 }}
            />
            {idx === active && (
              <motion.div
                className="absolute inset-0 rounded-full bg-brand/20"
                initial={{ scale: 1 }}
                animate={{ scale: 1.5, opacity: 0 }}
                transition={{ repeat: Infinity, duration: 2 }}
              />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
