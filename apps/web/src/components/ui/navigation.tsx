"use client";
import { motion, useReducedMotion } from "framer-motion";
import { PanelRightClose, PanelRightOpen } from "lucide-react";
import type { ReactNode } from "react";
import { useState } from "react";
import { cn } from "@/lib/utils";
import { IconButton } from "./button";

export function Sidebar({ children, footer }: { children: ReactNode; footer?: ReactNode }) { return <aside className="flex w-60 shrink-0 flex-col border-r bg-surface"><div className="flex h-12 items-center border-b px-4"><span className="font-mono text-sm font-semibold tracking-[-.08em]">KOGNIQ</span><span className="ml-2 h-1.5 w-1.5 rounded-full bg-accent" /></div><nav aria-label="Workspace navigation" className="flex-1 p-2">{children}</nav>{footer && <div className="border-t p-2">{footer}</div>}</aside>; }
export function SidebarItem({ icon, children, active = false }: { icon: ReactNode; children: ReactNode; active?: boolean }) { return <button className={cn("flex h-9 w-full items-center gap-2 rounded-sm px-2.5 text-left text-sm text-muted transition-colors hover:bg-raised hover:text-ink", active && "bg-raised font-medium text-ink")}><span className="size-4">{icon}</span>{children}</button>; }
export function ApplicationLayout({ sidebar, workspace, inspector }: { sidebar: ReactNode; workspace: ReactNode; inspector?: ReactNode }) {
  const [isInspectorOpen, setInspectorOpen] = useState(true); const reduceMotion = useReducedMotion();
  return <div className="flex h-screen overflow-hidden bg-canvas">{sidebar}<main className="min-w-0 flex-1">{workspace}</main>{inspector && <motion.aside initial={false} animate={{ width: isInspectorOpen ? 296 : 0 }} transition={reduceMotion ? { duration: 0 } : { duration: 0.18, ease: "easeOut" }} className="relative shrink-0 overflow-hidden border-l bg-surface"><div className="absolute left-0 top-1 z-10"><IconButton label={isInspectorOpen ? "Hide inspector" : "Show inspector"} onClick={() => setInspectorOpen((value) => !value)}>{isInspectorOpen ? <PanelRightClose className="size-4" /> : <PanelRightOpen className="size-4" />}</IconButton></div><div className="h-full w-[296px] pt-12">{inspector}</div></motion.aside>}</div>;
}
export function ResizablePanels({ left, right }: { left: ReactNode; right: ReactNode }) { return <div className="grid h-full min-h-0 grid-cols-[minmax(0,1fr)_minmax(260px,32%)]"><section className="min-w-0 overflow-auto">{left}</section><aside className="min-w-0 overflow-auto border-l bg-surface">{right}</aside></div>; }
