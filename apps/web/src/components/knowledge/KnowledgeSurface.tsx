"use client";

import { motion } from "framer-motion";
import { type ReactNode } from "react";

export function KnowledgeSurface({ children }: { children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="flex-1 flex w-full h-full bg-white relative overflow-hidden"
    >
      {children}
    </motion.div>
  );
}
