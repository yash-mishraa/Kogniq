import type { Transition } from "framer-motion";

export const workspaceMotion = {
  transition: { duration: 0.32, ease: [0.22, 1, 0.36, 1] } satisfies Transition,
  reducedTransition: { duration: 0 } satisfies Transition,
  locusReveal: { opacity: 1, y: 0 },
  locusInitial: { opacity: 0, y: 5 },
} as const;

export function resolveWorkspaceTransition(reducedMotion: boolean): Transition { return reducedMotion ? workspaceMotion.reducedTransition : workspaceMotion.transition; }
