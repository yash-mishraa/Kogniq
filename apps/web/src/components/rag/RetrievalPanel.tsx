"use client";

import { useMutation } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useState } from "react";
import { Button, Card, Input, Textarea } from "@/components/ui";
import { formatMs, formatScore } from "@/lib/rag/format";
import { ragApi } from "@/lib/rag/api";
import { DocumentPicker } from "./DocumentPicker";
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

export function RetrievalPanel({ onAsk }: { onAsk: (query: string, documentIds: string[]) => void }) {
  const [query, setQuery] = useState("");
  const [documentIds, setDocumentIds] = useState<string[]>([]);
  const [topK, setTopK] = useState(6);
  const [minimumSimilarity, setMinimumSimilarity] = useState(0.25);

  const retrieval = useMutation({ mutationFn: ragApi.retrieve });

  const run = () => {
    if (!query.trim()) return;
    retrieval.mutate({ query: query.trim(), document_ids: documentIds, top_k: topK, minimum_similarity: minimumSimilarity });
  };

  const data = retrieval.data;

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Engineering console"
        title="Retrieval inspector"
        detail="Dense vector search and SQLite FTS5/BM25 are fused with reciprocal rank fusion. No reranker is simulated."
      />

      <div className="grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
        <Card className="space-y-4 p-5">
          <label className="block">
            <span className="eyebrow">Query</span>
            <Textarea
              className="mt-1.5 min-h-24"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="What does the source say about…"
            />
          </label>

          <DocumentPicker value={documentIds} onChange={setDocumentIds} />

          <div className="grid grid-cols-2 gap-3">
            <label className="block">
              <span className="eyebrow">Top K</span>
              <Input
                className="mt-1.5"
                type="number"
                min={1}
                max={20}
                value={topK}
                onChange={(event) => setTopK(Number(event.target.value))}
              />
            </label>
            <label className="block">
              <span className="eyebrow">Min similarity</span>
              <Input
                className="mt-1.5"
                type="number"
                min={0}
                max={1}
                step={0.05}
                value={minimumSimilarity}
                onChange={(event) => setMinimumSimilarity(Number(event.target.value))}
              />
            </label>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={run} disabled={!query.trim() || retrieval.isPending}>
              <Search aria-hidden className="size-4" /> Retrieve
            </Button>
            <Button
              variant="secondary"
              onClick={() => onAsk(query.trim(), documentIds)}
              disabled={!query.trim()}
            >
              Take to grounded answer
            </Button>
          </div>
          <div><ErrorNotice error={retrieval.error} /></div>
        </Card>

        <Card className="p-5">
          <h3 className="section-title">How ranking is computed</h3>
          <dl className="mt-4">
            <KeyValue label="Dense candidates" value="vector similarity ≥ threshold" />
            <KeyValue label="Lexical candidates" value="BM25 over document_chunks_fts" />
            <KeyValue label="Fusion" value="Σ 1 / (60 + rank)" />
            <KeyValue label="Tie-break" value="vector score, then BM25 score" />
            <KeyValue label="Authorization" value="owned + Ready before fusion" />
          </dl>
          <div className="mt-4 space-y-2">
            <Notice tone="info">
              Vector and lexical ranks are shown per source so a surprising result can be traced to the
              retriever that produced it.
            </Notice>
            <Notice tone="info">
              If the lexical index is unavailable, retrieval degrades to vector-only and says so in the
              warnings instead of failing silently.
            </Notice>
          </div>
        </Card>
      </div>

      {retrieval.isPending ? <Loading label="Retrieving sources" /> : null}

      {data ? (
        <div className="space-y-4">
          <div className="grid gap-x-8 gap-y-8 sm:grid-cols-3">
            <Stat label="Sources" value={data.sources.length} hint={`requested top ${topK}`} />
            <Stat label="Retrieval latency" value={formatMs(data.timings.retrieval_ms)} hint="hybrid search" />
            <Stat label="Strategy" value={data.strategy} hint="vector + BM25 + RRF" tone="accent" />
          </div>
          <WarningList warnings={data.warnings} />
          {data.sources.length === 0 ? (
            <Notice tone="warning" title="No sources returned">
              Nothing survived authorization, hydration, or the similarity threshold. Lower the
              threshold, reindex the document, or choose another query.
            </Notice>
          ) : (
            <div className="space-y-2">
              {data.sources.map((source) => (
                <Card key={source.chunk_id} className="p-4">
                  <header className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <Mono className="rounded-xs bg-accent/10 px-1.5 py-0.5 text-accent">{source.source_id}</Mono>
                      <span className="text-sm font-medium text-ink">{source.document_title}</span>
                    </div>
                    <div className="flex flex-wrap gap-x-4 gap-y-1 font-mono text-[11px] text-muted">
                      <span>fusion {formatScore(source.fusion_score)}</span>
                      <span>vector {formatScore(source.vector_score)}</span>
                      <span>bm25 {formatScore(source.lexical_score)}</span>
                      <span>ranks v{source.vector_rank ?? "—"} / l{source.lexical_rank ?? "—"}</span>
                    </div>
                  </header>
                  <div className="mt-1 flex flex-wrap gap-x-3 text-[11px] text-muted">
                    <Mono>chunk #{source.chunk_index}</Mono>
                    {source.page_number !== null && source.page_number !== undefined ? (
                      <span>page {source.page_number}</span>
                    ) : null}
                    {source.section_title ? <span className="truncate">{source.section_title}</span> : null}
                  </div>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink/90">{source.text}</p>
                </Card>
              ))}
            </div>
          )}
        </div>
      ) : null}
    </div>
  );
}
