import type { ReactNode } from "react";
import { WorkspaceTransitions } from "@/app/workspace/WorkspaceTransitions";
export function WorkspaceTransitionBoundary({ children }: { children: ReactNode }) { return <WorkspaceTransitions>{children}</WorkspaceTransitions>; }
