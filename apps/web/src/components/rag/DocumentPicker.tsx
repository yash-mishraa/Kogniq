"use client";

import { useQuery } from "@tanstack/react-query";
import { useId } from "react";
import { ragApi } from "@/lib/rag/api";
import { documentStatus } from "@/lib/rag/presentation";
import { ErrorNotice } from "./shared";

export function DocumentPicker({
  value,
  onChange,
  label = "Documents to search",
  hint = "Leave all unchecked to search every document that is ready.",
}: {
  value: string[];
  onChange: (ids: string[]) => void;
  label?: string;
  hint?: string;
}) {
  const documents = useQuery({ queryKey: ["documents"], queryFn: ragApi.documents });
  const hintId = useId();
  const labelId = useId();

  if (documents.error) return <ErrorNotice error={documents.error} />;

  const ready = documents.data?.filter((doc) => doc.status === "Ready") ?? [];
  const unavailable = documents.data?.filter((doc) => doc.status !== "Ready") ?? [];

  const toggle = (id: string) => {
    onChange(value.includes(id) ? value.filter((item) => item !== id) : [...value, id]);
  };

  return (
    <div role="group" aria-labelledby={labelId} aria-describedby={hintId} className="min-w-0">
      <div className="flex items-baseline justify-between gap-3">
        <span id={labelId} className="eyebrow">
          {label}
        </span>
        <span className="font-mono text-[11px] text-muted">
          {value.length ? `${value.length} selected` : "all ready"}
        </span>
      </div>
      <p id={hintId} className="mt-0.5 text-[11px] leading-5 text-muted">
        {hint}
      </p>
      <div className="mt-2 max-h-44 overflow-y-auto rounded-sm border bg-surface">
        {documents.isLoading ? (
          <p className="px-3 py-3 text-xs text-muted">Loading documents…</p>
        ) : ready.length === 0 ? (
          <p className="px-3 py-3 text-xs leading-5 text-muted">
            No documents are ready yet. Add one in My Documents and wait for it to finish preparing.
          </p>
        ) : (
          ready.map((doc) => {
            const checked = value.includes(doc.id);
            return (
              <label
                key={doc.id}
                className="flex w-full cursor-pointer items-start gap-3 border-b border-line/60 px-3 py-2.5 text-left last:border-0 hover:bg-raised/60"
              >
                <input
                  type="checkbox"
                  className="mt-0.5"
                  checked={checked}
                  onChange={() => toggle(doc.id)}
                />
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-xs font-medium text-ink">{doc.title}</span>
                  <span className="mt-0.5 block text-[11px] text-muted">
                    {documentStatus(doc).label} · {doc.chunk_count} passage
                    {doc.chunk_count === 1 ? "" : "s"}
                  </span>
                </span>
              </label>
            );
          })
        )}
        {unavailable.length ? (
          <div className="border-t bg-raised/40 px-3 py-2">
            <p className="text-[10px] leading-4 text-muted">
              {unavailable.length} document{unavailable.length === 1 ? "" : "s"} cannot be searched
              yet because {unavailable.length === 1 ? "it is" : "they are"} still preparing or need
              attention.
            </p>
          </div>
        ) : null}
      </div>
    </div>
  );
}
