"use client";

import { MotionConfig, motion, useReducedMotion } from "framer-motion";
import type { ReactNode } from "react";
import { resolveWorkspaceTransition, workspaceMotion } from "./WorkspaceMotion";

export function WorkspaceTransitions({ children }: { children: ReactNode }) {
  const reduceMotion = useReducedMotion();
  return <MotionConfig reducedMotion="user" transition={resolveWorkspaceTransition(Boolean(reduceMotion))}><motion.div layout initial={workspaceMotion.locusInitial} animate={workspaceMotion.locusReveal} transition={resolveWorkspaceTransition(Boolean(reduceMotion))}>{children}</motion.div></MotionConfig>;
}
