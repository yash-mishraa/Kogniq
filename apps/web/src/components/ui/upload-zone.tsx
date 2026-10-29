"use client";
import { FileUp } from "lucide-react";
import { useId, useState } from "react";
import { cn } from "@/lib/utils";

export function UploadZone({
  accept,
  onFiles,
}: {
  accept?: string;
  onFiles?: (files: File[]) => void;
}) {
  const id = useId();
  const [active, setActive] = useState(false);
  const forward = (files: FileList | null) => files && onFiles?.([...files]);

  return (
    <div
      onDragOver={(event) => {
        event.preventDefault();
        setActive(true);
      }}
      onDragLeave={() => setActive(false)}
      onDrop={(event) => {
        event.preventDefault();
        setActive(false);
        forward(event.dataTransfer.files);
      }}
      className={cn(
        "flex min-h-40 flex-col items-center justify-center border border-dashed px-6 text-center transition-colors",
        active ? "border-accent bg-accent-muted/60" : "border-line hover:border-line-strong",
      )}
    >
      <FileUp className="mb-4 size-4 text-muted" aria-hidden />
      <p className="text-sm font-medium text-ink">Drop files here</p>
      <p className="mt-1 text-xs text-muted">
        or{" "}
        <label
          htmlFor={id}
          className="cursor-pointer text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
        >
          choose from device
        </label>
      </p>
      <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
        PDF · TXT · Markdown
      </p>
      <input
        id={id}
        className="sr-only"
        type="file"
        accept={accept}
        onChange={(event) => forward(event.target.files)}
      />
    </div>
  );
}
