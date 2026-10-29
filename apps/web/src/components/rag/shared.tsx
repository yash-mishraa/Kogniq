"use client";

import { AlertTriangle, CheckCircle2, Info, XCircle } from "lucide-react";
import type { ReactNode } from "react";
import { Badge } from "@/components/ui";
import { cn } from "@/lib/utils";
import type { DocumentSummary } from "@/lib/rag/api";
import { statusTone } from "@/lib/rag/format";
import { documentStatus, friendlyErrorMessage } from "@/lib/rag/presentation";

export function SectionHeading({
  eyebrow,
  title,
  detail,
  actions,
}: {
  eyebrow: string;
  title: string;
  detail?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-5 border-b border-line/70 pb-6">
      <div className="min-w-0">
        <p className="eyebrow">{eyebrow}</p>
        <h2 className="mt-3 max-w-4xl text-[clamp(1.9rem,3.4vw,3.1rem)] font-medium leading-[1.02] tracking-[-0.055em] text-ink">
          {title}
        </h2>
        {detail ? <p className="mt-4 max-w-2xl text-sm leading-6 text-muted">{detail}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-2">{actions}</div> : null}
    </div>
  );
}

export function Stat({
  label,
  value,
  hint,
  tone,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger" | "accent";
}) {
  const toneClass =
    tone === "success"
      ? "text-success"
      : tone === "warning"
        ? "text-warning"
        : tone === "danger"
          ? "text-danger"
          : tone === "accent"
            ? "text-accent"
            : "text-ink";
  return (
    <div className="border-t border-line/70 pt-4">
      <p className="eyebrow">{label}</p>
      <p
        className={cn(
          "mt-3 text-[clamp(1.7rem,2.6vw,2.35rem)] font-medium leading-none tracking-[-0.055em]",
          toneClass,
        )}
      >
        {value}
      </p>
      {hint ? <p className="mt-2 font-mono text-[10px] leading-4 text-muted">{hint}</p> : null}
    </div>
  );
}

/** Raw status, used only inside the engineering console. */
export function StatusBadge({ status }: { status: string }) {
  return <Badge tone={statusTone(status)}>{status.replaceAll("_", " ")}</Badge>;
}

/** Plain-language document state for the everyday workspace. */
export function DocumentStatusBadge({ document }: { document: Pick<DocumentSummary, "status"> }) {
  const view = documentStatus(document);
  return <Badge tone={view.tone}>{view.label}</Badge>;
}

/** A typographic disclosure; no icons, and it stays closed until requested. */
export function Disclosure({
  label,
  openLabel = "Hide details",
  className,
  children,
}: {
  label: string;
  openLabel?: string;
  className?: string;
  children: ReactNode;
}) {
  return (
    <details className={cn("group", className)}>
      <summary className="cursor-pointer list-none font-mono text-[10px] uppercase tracking-[0.16em] text-muted transition-colors hover:text-ink [&::-webkit-details-marker]:hidden">
        <span className="group-open:hidden">{label}</span>
        <span className="hidden group-open:inline">{openLabel}</span>
      </summary>
      <div className="mt-3">{children}</div>
    </details>
  );
}

export function Notice({
  tone = "info",
  title,
  children,
}: {
  tone?: "info" | "success" | "warning" | "danger";
  title?: string;
  children: ReactNode;
}) {
  const icon =
    tone === "success" ? (
      <CheckCircle2 aria-hidden className="mt-0.5 size-3.5 shrink-0 text-success" />
    ) : tone === "warning" ? (
      <AlertTriangle aria-hidden className="mt-0.5 size-3.5 shrink-0 text-warning" />
    ) : tone === "danger" ? (
      <XCircle aria-hidden className="mt-0.5 size-3.5 shrink-0 text-danger" />
    ) : (
      <Info aria-hidden className="mt-0.5 size-3.5 shrink-0 text-muted" />
    );
  const toneClass = {
    info: "border-line",
    success: "border-success/50",
    warning: "border-warning/50",
    danger: "border-danger/50",
  }[tone];
  return (
    <div className={cn("flex gap-2.5 border-l py-1 pl-3 text-sm", toneClass)}>
      {icon}
      <div className="min-w-0 leading-6">
        {title ? <p className="font-medium text-ink">{title}</p> : null}
        <div className="text-muted">{children}</div>
      </div>
    </div>
  );
}

export function WarningList({ warnings }: { warnings: string[] }) {
  if (!warnings.length) return null;
  return (
    <div className="space-y-2">
      {warnings.map((warning) => (
        <Notice key={warning} tone="warning">
          {warning}
        </Notice>
      ))}
    </div>
  );
}

export function ErrorNotice({ error }: { error: unknown }) {
  if (!error) return null;
  const message = error instanceof Error ? error.message : String(error);
  return (
    <Notice tone="danger" title="Request failed">
      {message}
    </Notice>
  );
}

/**
 * Everyday error: a useful sentence, an optional retry, and the raw message
 * kept behind a deliberate disclosure.
 */
export function UserErrorNotice({
  error,
  onRetry,
}: {
  error: unknown;
  onRetry?: () => void;
}) {
  if (!error) return null;
  const { message, detail } = friendlyErrorMessage(error);
  return (
    <Notice tone="danger" title="Something went wrong">
      <p>{message}</p>
      {onRetry ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
        >
          Try again
        </button>
      ) : null}
      {detail ? (
        <Disclosure label="Technical details" openLabel="Hide technical details" className="mt-3">
          <p className="break-words font-mono text-[11px] leading-5 text-muted">{detail}</p>
        </Disclosure>
      ) : null}
    </Notice>
  );
}

export function Loading({ label = "Loading" }: { label?: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex items-center gap-3 py-8 font-mono text-[10px] uppercase tracking-[0.16em] text-muted"
    >
      <span aria-hidden className="h-px w-7 animate-[quiet-pulse_1.4s_ease-in-out_infinite] bg-accent" />
      {label}…
    </div>
  );
}

export function KeyValue({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line/50 py-2 last:border-0">
      <dt className="font-mono text-[10px] uppercase tracking-[0.1em] text-muted">{label}</dt>
      <dd className="min-w-0 truncate text-right font-mono text-[11px] text-ink">{value}</dd>
    </div>
  );
}

export function Mono({ children, className }: { children: ReactNode; className?: string }) {
  return <span className={cn("font-mono text-[11px]", className)}>{children}</span>;
}
