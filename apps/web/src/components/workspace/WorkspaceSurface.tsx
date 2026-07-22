import type { ReactNode } from "react";
export function WorkspaceSurface({ children }: { children: ReactNode }) { return <main className="flex min-h-dvh flex-col bg-canvas px-6 py-7 sm:px-10 sm:py-9">{children}</main>; }
