"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import UserForm from "@/components/UserForm";
import { getPrediction } from "@/lib/api";
import type { UserInput } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { pageContainer, fadeUp, staggerContainer, hoverButton } from "@/lib/motion";

const QUICK_FILL: UserInput = {
  age: 34,
  gender: "female",
  rural_urban: "rural",
  income_level: "low",
  occupation: "farmer",
  education_level: "primary",
  digital_access: "limited",
  document_completeness: 0.5,
  institutional_dependency: "high",
};

const TIPS = [
  { icon: "👤", text: "Fill in your demographic details accurately for the best match." },
  { icon: "📄", text: "Document completeness (0–1) reflects how many official documents you have." },
  { icon: "📶", text: "Digital access describes your ability to use online services." },
  { icon: "🏛️", text: "Institutional dependency indicates how much you rely on government offices." },
];

export default function InputPage() {
  const router = useRouter();
  const store = useAppStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quickFillKey, setQuickFillKey] = useState(0);

  async function handleSubmit(data: UserInput) {
    setLoading(true);
    setError(null);
    store.reset();
    try {
      const prediction = await getPrediction(data);
      store.setResult(prediction);
      store.setUserInput(data);
      setLoading(false);
      // 150ms delay — lets the loading state render before navigation
      setTimeout(() => router.push("/results"), 150);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An unexpected error occurred");
      setLoading(false);
    }
  }

  function handleQuickFill() {
    store.setUserInput(QUICK_FILL);
    setQuickFillKey((k) => k + 1);
  }

  return (
    <AnimatePresence mode="wait">
      <motion.main
        key="input-page"
        initial="hidden"
        animate="visible"
        exit="exit"
        variants={pageContainer}
        className="mx-auto w-full max-w-4xl flex-1 px-4 py-10 space-y-8"
      >
        {/* Header */}
        <motion.div variants={fadeUp} className="space-y-2">
          <h1 className="text-3xl font-bold text-content-primary">Your Profile</h1>
          <p className="text-sm text-content-secondary">
            Provide your details to get personalised scheme recommendations.
          </p>
        </motion.div>

        {/* Tips */}
        <motion.div variants={fadeUp} className="card p-5">
          <p className="mb-4 text-sm font-semibold text-content-primary">
            💡 How to provide your information
          </p>
          <motion.ul
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="grid gap-3 sm:grid-cols-2"
          >
            {TIPS.map((tip) => (
              <motion.li
                key={tip.text}
                variants={fadeUp}
                className="flex items-start gap-2 text-sm text-content-secondary"
              >
                <span className="text-lg shrink-0">{tip.icon}</span>
                <span>{tip.text}</span>
              </motion.li>
            ))}
          </motion.ul>
        </motion.div>

        {/* Quick Fill */}
        <motion.div variants={fadeUp} className="flex items-center justify-between">
          <p className="text-xs text-content-muted">Want to try a demo?</p>
          <motion.button
            {...hoverButton}
            onClick={handleQuickFill}
            className="btn btn-secondary text-xs"
          >
            ⚡ Quick Fill Example
          </motion.button>
        </motion.div>

        {/* Form */}
        <motion.div variants={fadeUp}>
          <UserForm
            key={quickFillKey}
            onSubmit={handleSubmit}
            loading={loading}
            initialValues={quickFillKey > 0 ? QUICK_FILL : undefined}
          />
        </motion.div>

        {/* Error */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8, scale: 0.97 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, scale: 0.97 }}
              transition={{ duration: 0.2 }}
              className="card p-5"
              style={{ borderColor: "var(--danger)", background: "rgba(239,68,68,0.06)" }}
            >
              <div className="flex items-start gap-3">
                <span className="text-xl text-danger shrink-0">⚠</span>
                <div>
                  <p className="text-sm font-semibold text-danger">
                    Unable to connect to server
                  </p>
                  <p className="mt-1 text-xs text-content-secondary">
                    Please check that the backend is running and reachable.
                  </p>
                  {process.env.NODE_ENV === "development" && (
                    <p className="mt-2 rounded-lg px-3 py-2 font-mono text-xs text-danger/80 break-all"
                       style={{ background: "rgba(239,68,68,0.08)" }}>
                      {error}
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.main>
    </AnimatePresence>
  );
}
