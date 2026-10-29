"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { FlaskConical, GitCompareArrows } from "lucide-react";
import { useState } from "react";
import { Button, Card, Input, Table, Textarea } from "@/components/ui";
import { cn } from "@/lib/utils";
import { ragApi, type ChunkPreview } from "@/lib/rag/api";
import {
  ErrorNotice,
  KeyValue,
  Loading,
  Mono,
  Notice,
  SectionHeading,
  Stat,
  WarningList,
} from "./shared";

type SourceMode = "text" | "document";

export function ChunkingPanel() {
  const documents = useQuery({ queryKey: ["documents"], queryFn: ragApi.documents });
  const [mode, setMode] = useState<SourceMode>("text");
  const [text, setText] = useState("");
  const [documentId, setDocumentId] = useState("");
  const [chunkSize, setChunkSize] = useState(1200);
  const [chunkOverlap, setChunkOverlap] = useState(200);
  const [maxChunks, setMaxChunks] = useState(20);

  const preview = useMutation({ mutationFn: ragApi.previewChunks });
  const comparison = useMutation({ mutationFn: ragApi.compareChunks });

  const sourceError =
    mode === "text"
      ? text.trim()
        ? null
        : "Paste some text to preview."
      : documentId
        ? null
        : "Choose a document to preview.";
  const overlapError =
    chunkOverlap >= chunkSize ? "Overlap must be smaller than chunk size." : null;
  const invalid = Boolean(sourceError || overlapError);

  const source = mode === "text" ? { text } : { document_id: documentId };

  const runPreview = () => {
    preview.mutate({ ...source, chunk_size: chunkSize, chunk_overlap: chunkOverlap, max_chunks: maxChunks });
  };

  const runCompare = () => {
    comparison.mutate({
      ...source,
      max_chunks: Math.min(maxChunks, 12),
      configs: [
        { chunk_size: 600, chunk_overlap: 100, label: "Small" },
        { chunk_size: 1200, chunk_overlap: 200, label: "Production" },
        { chunk_size: 2400, chunk_overlap: 300, label: "Large" },
      ],
    });
  };

  const result = preview.data;
  const error = preview.error ?? comparison.error;

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Engineering console"
        title="Chunking workbench"
        detail="This preview uses the same fixed-size strategy as the ingestion pipeline, including overlap and reading order."
      />

      <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr]">
        <Card className="space-y-4 p-5">
          <div className="flex gap-6 border-b border-line/70">
            {(["text", "document"] as const).map((value) => (
              <button
                key={value}
                type="button"
                onClick={() => setMode(value)}
                className={cn(
                  "relative -mb-px border-b px-0 py-2 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors",
                  mode === value
                    ? "border-accent text-ink"
                    : "border-transparent text-muted hover:text-ink",
                )}
              >
                {value === "text" ? "Paste text" : "Use document"}
              </button>
            ))}
          </div>

          {mode === "text" ? (
            <label className="block">
              <span className="eyebrow">Source text</span>
              <Textarea
                className="mt-1.5 min-h-40"
                value={text}
                onChange={(event) => setText(event.target.value)}
                placeholder="Paste a passage to inspect how it will be chunked…"
              />
            </label>
          ) : (
            <label className="block">
              <span className="eyebrow">Document</span>
              <select
                className="mt-1.5 h-9 w-full rounded-sm border border-line bg-surface px-3 text-sm text-ink outline-none focus:border-accent"
                value={documentId}
                onChange={(event) => setDocumentId(event.target.value)}
              >
                <option value="">Choose a document…</option>
                {documents.data?.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.title} ({doc.status})
                  </option>
                ))}
              </select>
              {documents.error ? <div className="mt-2"><ErrorNotice error={documents.error} /></div> : null}
            </label>
          )}

          <div className="grid grid-cols-3 gap-3">
            <label className="block">
              <span className="eyebrow">Chunk size</span>
              <Input
                className="mt-1.5"
                type="number"
                min={100}
                max={8000}
                value={chunkSize}
                onChange={(event) => setChunkSize(Number(event.target.value))}
              />
            </label>
            <label className="block">
              <span className="eyebrow">Overlap</span>
              <Input
                className="mt-1.5"
                type="number"
                min={0}
                max={4000}
                value={chunkOverlap}
                onChange={(event) => setChunkOverlap(Number(event.target.value))}
              />
            </label>
            <label className="block">
              <span className="eyebrow">Max shown</span>
              <Input
                className="mt-1.5"
                type="number"
                min={1}
                max={200}
                value={maxChunks}
                onChange={(event) => setMaxChunks(Number(event.target.value))}
              />
            </label>
          </div>

          {overlapError ? <Notice tone="warning">{overlapError}</Notice> : null}

          <div className="flex flex-wrap gap-2">
            <Button onClick={runPreview} disabled={invalid || preview.isPending}>
              <FlaskConical aria-hidden className="size-4" /> Preview chunks
            </Button>
            <Button variant="secondary" onClick={runCompare} disabled={invalid || comparison.isPending}>
              <GitCompareArrows aria-hidden className="size-4" /> Compare presets
            </Button>
          </div>
          <div><ErrorNotice error={error} /></div>
        </Card>

        <Card className="p-5">
          <h3 className="section-title">Configuration contract</h3>
          <p className="mt-1 text-xs text-muted">
            Production defaults are environment-driven. The values here are a preview only; reindex a
            document to apply a different configuration to persisted vectors.
          </p>
          <dl className="mt-4">
            <KeyValue label="Strategy" value="FixedSizeChunkStrategy" />
            <KeyValue label="Default chunk size" value="1200 chars" />
            <KeyValue label="Default overlap" value="200 chars" />
            <KeyValue label="Tokenizer estimate" value="characters ÷ 4" />
            <KeyValue label="Ordering" value="reading order, headings preserved" />
          </dl>
          <div className="mt-4">
            <Notice tone="info">
              Overlap repeats the tail of one chunk at the start of the next. It improves recall across
              boundaries but increases embedding cost and duplicate text.
            </Notice>
          </div>
        </Card>
      </div>

      {preview.isPending || comparison.isPending ? <Loading label="Chunking source" /> : null}

      {result ? <PreviewResult preview={result} /> : null}

      {comparison.data ? (
        <Card className="overflow-hidden">
          <div className="border-b px-5 py-4">
            <h3 className="section-title">Configuration comparison</h3>
            <p className="mt-0.5 text-xs text-muted">
              {comparison.data.source_characters.toLocaleString()} source characters across{" "}
              {comparison.data.results.length} configurations.
            </p>
          </div>
          <Table>
            <thead className="border-b border-line/70">
              <tr>
                <th className="px-4 py-2 font-medium">Configuration</th>
                <th className="px-4 py-2 font-medium">Chunks</th>
                <th className="px-4 py-2 font-medium">Avg chars</th>
                <th className="px-4 py-2 font-medium">Min / max</th>
                <th className="px-4 py-2 font-medium">Est. tokens</th>
              </tr>
            </thead>
            <tbody>
              {comparison.data.results.map((entry) => (
                <tr key={`${entry.stats.chunk_size}-${entry.stats.chunk_overlap}`} className="border-t border-line/70">
                  <td className="px-4 py-2">
                    <Mono>
                      {entry.stats.chunk_size} / {entry.stats.chunk_overlap}
                    </Mono>
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{entry.stats.chunk_count}</td>
                  <td className="px-4 py-2 font-mono text-xs">{entry.stats.average_chunk_characters}</td>
                  <td className="px-4 py-2 font-mono text-xs">
                    {entry.stats.min_chunk_characters} / {entry.stats.max_chunk_characters}
                  </td>
                  <td className="px-4 py-2 font-mono text-xs">{entry.stats.estimated_tokens}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card>
      ) : null}
    </div>
  );
}

function PreviewResult({ preview }: { preview: ChunkPreview }) {
  return (
    <div className="space-y-4">
      <div className="grid gap-x-8 gap-y-8 sm:grid-cols-2 lg:grid-cols-4">
        <Stat label="Chunks" value={preview.stats.chunk_count} hint={`${preview.source_characters.toLocaleString()} source chars`} />
        <Stat label="Average size" value={`${preview.stats.average_chunk_characters}`} hint="characters" />
        <Stat label="Range" value={`${preview.stats.min_chunk_characters}–${preview.stats.max_chunk_characters}`} hint="characters per chunk" />
        <Stat label="Estimated tokens" value={preview.stats.estimated_tokens.toLocaleString()} hint="characters ÷ 4" tone="accent" />
      </div>
      <WarningList warnings={preview.warnings} />
      <Card className="overflow-hidden">
        <div className="border-b px-5 py-4">
          <h3 className="section-title">Chunks</h3>
          <p className="mt-0.5 text-xs text-muted">
            Showing {preview.stats.shown_chunk_count} of {preview.stats.chunk_count}. Overlap is measured
            against the previous chunk.
          </p>
        </div>
        <div className="space-y-2 p-4">
          {preview.chunks.map((chunk) => (
            <article key={chunk.index} className="rounded-sm border bg-raised/30 p-3">
              <header className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted">
                <Mono>#{chunk.index}</Mono>
                <Mono>{chunk.character_count} chars</Mono>
                <Mono>~{chunk.estimated_tokens} tokens</Mono>
                {chunk.overlap_prefix_characters > 0 ? (
                  <Mono className="text-accent">overlap {chunk.overlap_prefix_characters}</Mono>
                ) : null}
                {chunk.page_number ? <span>page {chunk.page_number}</span> : null}
                {chunk.section_title ? <span className="truncate">{chunk.section_title}</span> : null}
              </header>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink/90">{chunk.text}</p>
            </article>
          ))}
        </div>
      </Card>
    </div>
  );
}
