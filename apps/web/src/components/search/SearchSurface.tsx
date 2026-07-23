"use client";

import type { ReactNode } from "react";
import { motion } from "framer-motion";

export function SearchSurface({ children }: { children: ReactNode }) {
  return (
    <motion.div
      className="flex flex-1 w-full h-full relative overflow-hidden bg-canvas"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
    >
      <div className="flex w-full h-full flex-col max-w-5xl mx-auto px-6 lg:px-12 pt-12">
        {children}
      </div>
    </motion.div>
  );
}
