"use client";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { FileQuestion, type LucideIcon } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Badge({ tone = "neutral", children }: { tone?: "neutral" | "accent" | "success" | "warning" | "danger"; children: ReactNode }) {
  const tones = { neutral: "bg-raised text-muted", accent: "bg-[hsl(var(--accent-muted))] text-accent", success: "bg-success/10 text-success", warning: "bg-warning/10 text-warning", danger: "bg-danger/10 text-danger" };
  return <span className={cn("inline-flex items-center rounded-xs px-1.5 py-0.5 font-mono text-[11px] font-medium", tones[tone])}>{children}</span>;
}
export function Card({ className, ...props }: HTMLAttributes<HTMLElement>) { return <section className={cn("rounded-md border bg-surface shadow-panel", className)} {...props} />; }
export function Tabs({ items, defaultValue }: { defaultValue: string; items: { value: string; label: string; content: ReactNode }[] }) {
  return <TabsPrimitive.Root defaultValue={defaultValue}><TabsPrimitive.List aria-label="Content sections" className="flex gap-1 border-b px-1"><>{items.map((item) => <TabsPrimitive.Trigger key={item.value} value={item.value} className="relative -mb-px border-b-2 border-transparent px-2.5 py-2 text-sm text-muted transition-colors data-[state=active]:border-accent data-[state=active]:text-ink">{item.label}</TabsPrimitive.Trigger>)}</></TabsPrimitive.List>{items.map((item) => <TabsPrimitive.Content key={item.value} value={item.value} className="p-4 text-sm text-muted focus:outline-none">{item.content}</TabsPrimitive.Content>)}</TabsPrimitive.Root>;
}
export function EmptyState({ icon: Icon = FileQuestion, title, detail, action }: { icon?: LucideIcon; title: string; detail: string; action?: ReactNode }) { return <div className="flex min-h-48 flex-col items-center justify-center border border-dashed bg-raised/40 px-6 text-center"><Icon aria-hidden className="mb-3 size-5 text-muted" /><h3 className="text-sm font-medium">{title}</h3><p className="mt-1 max-w-sm text-sm text-muted">{detail}</p>{action && <div className="mt-4">{action}</div>}</div>; }
export function Progress({ value, label }: { value: number; label?: string }) { return <div className="space-y-1.5"><div className="flex justify-between text-xs text-muted"><span>{label}</span><span className="font-mono">{value}%</span></div><div className="h-1.5 overflow-hidden rounded-full bg-raised"><div className="h-full rounded-full bg-accent transition-[width] duration-[var(--motion-base)]" style={{ width: `${Math.max(0, Math.min(100, value))}%` }} /></div></div>; }
export function Table({ children, className }: { children: ReactNode; className?: string }) { return <div className={cn("overflow-x-auto border", className)}><table className="w-full text-left text-sm">{children}</table></div>; }
