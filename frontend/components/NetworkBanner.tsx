"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useOnlineStatus } from "@/lib/network";

export default function NetworkBanner() {
  const online = useOnlineStatus();

  return (
    <AnimatePresence>
      {!online && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          transition={{ duration: 0.25 }}
          className="overflow-hidden"
        >
          <div
            className="flex items-center justify-center gap-2 px-4 py-2 text-xs font-medium"
            style={{
              background: "rgba(245,158,11,0.12)",
              borderBottom: "1px solid rgba(245,158,11,0.25)",
              color: "#fbbf24",
            }}
          >
            <span>⚠</span>
            You are offline — API calls will fail until your connection is restored.
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
