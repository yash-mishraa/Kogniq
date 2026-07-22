"use client";

import { type ReactNode, useEffect, useRef } from "react";
import { useWorkspace } from "@/app/workspace/WorkspaceContext";
export function WorkspaceContent({ children }: { children: ReactNode }) { const { activeEnvironmentId, memory, remember } = useWorkspace(); const ref = useRef<HTMLDivElement>(null); useEffect(() => { if (ref.current) ref.current.scrollTop = memory[activeEnvironmentId]?.scrollPosition ?? 0; }, [activeEnvironmentId, memory]); return <div ref={ref} onScroll={(event) => remember(activeEnvironmentId, { scrollPosition: event.currentTarget.scrollTop })} className="flex flex-1 flex-col overflow-auto py-14">{children}</div>; }
