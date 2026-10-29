"use client";
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { FileQuestion, type LucideIcon } from "lucide-react";
import type { HTMLAttributes, ReactNode } from "react";
import { cn } from "@/lib/utils";

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: "neutral" | "accent" | "success" | "warning" | "danger";
  children: ReactNode;
}) {
  const tones = {
    neutral: "border-line text-muted",
    accent: "border-accent/40 text-accent",
    success: "border-success/40 text-success",
    warning: "border-warning/40 text-warning",
    danger: "border-danger/40 text-danger",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-xs border px-1.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-[0.08em]",
        tones[tone],
      )}
    >
      {children}
    </span>
  );
}

export function Card({ className, ...props }: HTMLAttributes<HTMLElement>) {
  return <section className={cn("rounded-sm border border-line/80 bg-surface/50", className)} {...props} />;
}

export function Tabs({
  items,
  defaultValue,
}: {
  defaultValue: string;
  items: { value: string; label: string; content: ReactNode }[];
}) {
  return (
    <TabsPrimitive.Root defaultValue={defaultValue}>
      <TabsPrimitive.List aria-label="Content sections" className="flex gap-4 border-b border-line/70">
        {items.map((item) => (
          <TabsPrimitive.Trigger
            key={item.value}
            value={item.value}
            className="relative -mb-px border-b border-transparent px-0.5 py-2.5 font-mono text-[10px] uppercase tracking-[0.14em] text-muted transition-colors hover:text-ink data-[state=active]:border-accent data-[state=active]:text-ink"
          >
            {item.label}
          </TabsPrimitive.Trigger>
        ))}
      </TabsPrimitive.List>
      {items.map((item) => (
        <TabsPrimitive.Content
          key={item.value}
          value={item.value}
          className="p-4 text-sm text-muted focus:outline-none"
        >
          {item.content}
        </TabsPrimitive.Content>
      ))}
    </TabsPrimitive.Root>
  );
}

export function EmptyState({
  icon: Icon = FileQuestion,
  title,
  detail,
  action,
}: {
  icon?: LucideIcon;
  title: string;
  detail: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex min-h-48 flex-col items-center justify-center border border-dashed border-line px-6 text-center">
      <Icon aria-hidden className="mb-4 size-4 text-muted" />
      <h3 className="text-sm font-medium text-ink">{title}</h3>
      <p className="mt-2 max-w-sm text-sm leading-6 text-muted">{detail}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}

export function Progress({ value, label }: { value: number; label?: string }) {
  return (
    <div className="space-y-2">
      <div className="flex justify-between font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="h-px overflow-hidden bg-line">
        <div
          className="h-full bg-accent transition-[width] duration-[var(--motion-base)]"
          style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
        />
      </div>
    </div>
  );
}

export function Table({ children, className }: { children: ReactNode; className?: string }) {
  return (
    <div className={cn("overflow-x-auto border-t border-line/70", className)}>
      <table className="w-full text-left text-sm">{children}</table>
    </div>
  );
}
