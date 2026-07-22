"use client";
import { FileUp } from "lucide-react";
import { useId, useState } from "react";
import { cn } from "@/lib/utils";

export function UploadZone({ accept, onFiles }: { accept?: string; onFiles?: (files: File[]) => void }) {
  const id = useId(); const [active, setActive] = useState(false); const forward = (files: FileList | null) => files && onFiles?.([...files]);
  return <div onDragOver={(event) => { event.preventDefault(); setActive(true); }} onDragLeave={() => setActive(false)} onDrop={(event) => { event.preventDefault(); setActive(false); forward(event.dataTransfer.files); }} className={cn("flex min-h-40 flex-col items-center justify-center border border-dashed px-6 text-center transition-colors", active ? "border-accent bg-[hsl(var(--accent-muted))]" : "bg-raised/30")}><FileUp className="mb-3 size-5 text-muted" aria-hidden /><p className="text-sm font-medium">Drop files here</p><p className="mt-1 text-xs text-muted">or <label htmlFor={id} className="cursor-pointer text-accent underline underline-offset-2">choose from device</label></p><input id={id} className="sr-only" type="file" accept={accept} onChange={(event) => forward(event.target.files)} /></div>;
}
