"use client";
import * as DialogPrimitive from "@radix-ui/react-dialog";
import { Command, CornerDownLeft, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

const entries = ["Open workspace", "Find in knowledge", "Toggle inspector", "Switch theme"];
export function CommandPalette() {
  const [open, setOpen] = useState(false); const [query, setQuery] = useState("");
  useEffect(() => { const onKey = (event: KeyboardEvent) => { if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") { event.preventDefault(); setOpen(true); } }; window.addEventListener("keydown", onKey); return () => window.removeEventListener("keydown", onKey); }, []);
  const visible = entries.filter((entry) => entry.toLowerCase().includes(query.toLowerCase()));
  return <DialogPrimitive.Root open={open} onOpenChange={setOpen}><DialogPrimitive.Trigger asChild><button className="inline-flex h-8 items-center gap-2 rounded-sm border bg-surface px-2.5 text-xs text-muted hover:bg-raised"><Command className="size-3.5" />Command <kbd className="ml-2 font-mono text-[10px]">⌘K</kbd></button></DialogPrimitive.Trigger><DialogPrimitive.Portal><DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-ink/25" /><DialogPrimitive.Content aria-describedby={undefined} className="fixed left-1/2 top-[18%] z-50 w-[calc(100%-2rem)] max-w-xl -translate-x-1/2 rounded-md border bg-surface shadow-overlay"><DialogPrimitive.Title className="sr-only">Command palette</DialogPrimitive.Title><div className="flex items-center gap-3 border-b px-4"><Search className="size-4 text-muted" /><input autoFocus value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search commands" className="h-12 flex-1 bg-transparent text-sm outline-none placeholder:text-muted" /></div><div className="p-2">{visible.map((entry) => <button key={entry} onClick={() => setOpen(false)} className="flex w-full items-center justify-between rounded-xs px-3 py-2.5 text-left text-sm hover:bg-raised"><span>{entry}</span><CornerDownLeft className="size-3.5 text-muted" /></button>)}{visible.length === 0 && <p className="px-3 py-8 text-center text-sm text-muted">No commands match “{query}”.</p>}</div><div className="flex gap-3 border-t px-4 py-2 font-mono text-[10px] text-muted"><span><kbd className="rounded border px-1">↵</kbd> select</span><span><kbd className="rounded border px-1">esc</kbd> close</span></div></DialogPrimitive.Content></DialogPrimitive.Portal></DialogPrimitive.Root>;
}
