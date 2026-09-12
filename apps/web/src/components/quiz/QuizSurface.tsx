"use client";

import { motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";

export function QuizSurface({ children }: { children: ReactNode }) {
  const reduceMotion = useReducedMotion();
  return <motion.section initial={reduceMotion ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reduceMotion ? 0 : 0.24 }} className="mx-auto flex min-h-full w-full max-w-3xl flex-1 flex-col px-6 py-10 lg:px-12">{children}</motion.section>;
}
