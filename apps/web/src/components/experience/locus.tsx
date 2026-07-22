"use client";

import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { FormEvent, useId, useMemo, useState } from "react";
import { cn } from "@/lib/utils";

export type LocusSuggestion = { label: string; detail: string };

export function Locus({ prompt, suggestions, onSelect, className }: { prompt: string; suggestions: LocusSuggestion[]; onSelect: (suggestion: LocusSuggestion) => void; className?: string }) {
  const labelId = useId();
  const [value, setValue] = useState("");
  const [focused, setFocused] = useState(false);
  const reduceMotion = useReducedMotion();
  const visible = useMemo(() => suggestions.filter((item) => item.label.toLowerCase().includes(value.toLowerCase()) || item.detail.toLowerCase().includes(value.toLowerCase())), [suggestions, value]);
  const showSuggestions = focused;
  const submit = (event: FormEvent) => { event.preventDefault(); if (visible[0]) onSelect(visible[0]); };

  return <div className={cn("locus-field", className)}>
    <form onSubmit={submit} className="flex items-center text-[clamp(1.15rem,2vw,1.55rem)] tracking-[-0.035em]">
      <label id={labelId} className="sr-only">{prompt}</label>
      <span aria-hidden className="locus-caret" />
      <input aria-labelledby={labelId} value={value} onChange={(event) => setValue(event.target.value)} onFocus={() => setFocused(true)} onBlur={() => window.setTimeout(() => setFocused(false), 120)} placeholder={prompt} className="locus-input" />
    </form>
    <AnimatePresence initial={false}>
      {showSuggestions && <motion.ul initial={reduceMotion ? false : { opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} exit={reduceMotion ? undefined : { opacity: 0, y: -3 }} transition={{ duration: reduceMotion ? 0 : 0.16 }} aria-label="Suggested next steps" className="mt-5 max-w-xl space-y-1">
        {visible.slice(0, 4).map((item) => <li key={item.label}><button type="button" onMouseDown={(event) => event.preventDefault()} onClick={() => onSelect(item)} className="group flex w-full items-baseline gap-3 py-2 text-left outline-none"><span className="text-sm text-ink transition-colors group-hover:text-accent group-focus-visible:text-accent">{item.label}</span><span className="font-mono text-[10px] text-muted">{item.detail}</span></button></li>)}
      </motion.ul>}
    </AnimatePresence>
  </div>;
}
