"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, Table } from "@/components/ui";
import { formatDate, formatMs } from "@/lib/rag/format";
import { ragApi } from "@/lib/rag/api";
import {
  ErrorNotice,
  KeyValue,
  Loading,
  Notice,
  SectionHeading,
  Stat,
  StatusBadge,
} from "./shared";

export function OverviewPanel({ onOpenActivity }: { onOpenActivity: () => void }) {
  const overview = useQuery({ queryKey: ["overview"], queryFn: ragApi.overview });
  const readiness = useQuery({ queryKey: ["readiness"], queryFn: ragApi.readiness });

  if (overview.isLoading) return <Loading label="Loading system overview" />;
  if (overview.error) return <ErrorNotice error={overview.error} />;
  const data = overview.data!;

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Engineering console"
        title="System, index, and quality"
        detail="Live document, index, and query telemetry from this workspace. Readiness reflects durable state, not upload success."
      />

      <div className="grid gap-x-8 gap-y-8 sm:grid-cols-2 lg:grid-cols-4">
        <Stat
          label="Documents"
          value={data.documents.total}
          hint={`${data.documents.ready} ready · ${data.documents.unindexed} unindexed`}
        />
        <Stat
          label="Indexed chunks"
          value={data.documents.chunks.toLocaleString()}
          hint={`${data.index.indexed_documents} documents in the vector index`}
          tone={data.documents.chunks > 0 ? "success" : "warning"}
        />
        <Stat
          label="Queries · 7 days"
          value={data.queries_7d.count}
          hint={`${data.queries_7d.answered} answered · ${data.queries_7d.insufficient} insufficient`}
        />
        <Stat
          label="Average latency"
          value={formatMs(data.queries_7d.avg_total_ms)}
          hint={`retrieval ${formatMs(data.queries_7d.avg_retrieval_ms)} · generation ${formatMs(data.queries_7d.avg_generation_ms)}`}
          tone="accent"
        />
      </div>

      {readiness.data ? (
        <Notice tone={readiness.data.ready ? "success" : "warning"} title={readiness.data.ready ? "Dependencies ready" : "Dependencies degraded"}>
          <div className="flex flex-wrap gap-x-5 gap-y-1">
            {Object.entries(readiness.data.checks).map(([name, check]) => (
              <span key={name}>
                <span className="font-mono text-xs">{name}</span>:{" "}
                {check.ok ? "ok" : "unavailable"}
                {check.count !== undefined && check.count !== null ? ` (${check.count})` : ""}
              </span>
            ))}
          </div>
        </Notice>
      ) : null}

      <div className="grid items-start gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="p-5">
          <h3 className="section-title">Index configuration</h3>
          <dl className="mt-4">
            <KeyValue label="Vector provider" value={data.index.provider} />
            <KeyValue label="Collection" value={data.index.collection} />
            <KeyValue label="Vectors" value={data.index.vector_count ?? "unavailable"} />
            <KeyValue label="Embedding model" value={data.index.embedding_model} />
            <KeyValue label="Dimensions" value={data.index.embedding_dimensions} />
            <KeyValue label="Chunker" value={data.index.chunker_config ?? "not recorded"} />
            <KeyValue label="Generated" value={formatDate(data.generated_at)} />
          </dl>
          {data.index.error ? (
            <div className="mt-3">
              <Notice tone="danger" title="Vector index unavailable">{data.index.error}</Notice>
            </div>
          ) : null}
        </Card>

        <div className="space-y-4">
          <Card className="p-5">
            <h3 className="section-title">Capabilities</h3>
            <div className="mt-4 space-y-3 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span>Hybrid retrieval</span>
                <StatusBadge status={data.capabilities.hybrid_retrieval ? "Ready" : "Unindexed"} />
              </div>
              <div className="flex items-center justify-between gap-3">
                <span>FTS5 lexical index</span>
                <StatusBadge status={data.capabilities.fts5 ? "Ready" : "Unindexed"} />
              </div>
              <div className="flex items-center justify-between gap-3">
                <span>Prompt caching</span>
                <StatusBadge status={data.capabilities.prompt_cache ? "Ready" : "not_supported"} />
              </div>
              <p className="rounded-sm border bg-raised/50 px-3 py-2 text-xs leading-relaxed text-muted">
                {data.capabilities.prompt_cache_note}
              </p>
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="section-title">Quality signals</h3>
            <dl className="mt-4">
              <KeyValue label="Evaluation runs" value={data.evaluation_runs} />
              <KeyValue label="Citations · 7 days" value={data.queries_7d.citations} />
              <KeyValue
                label="Citations per answer"
                value={
                  data.queries_7d.answered
                    ? (data.queries_7d.citations / data.queries_7d.answered).toFixed(2)
                    : "—"
                }
              />
            </dl>
          </Card>
        </div>
      </div>

      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
          <div>
            <h3 className="section-title">Recent queries</h3>
            <p className="mt-0.5 text-xs text-muted">Prompts and source text are never stored in telemetry.</p>
          </div>
          <button type="button" onClick={onOpenActivity} className="text-xs text-accent underline underline-offset-2">
            Open activity log
          </button>
        </div>
        {data.recent_queries.length === 0 ? (
          <p className="px-5 py-8 text-sm text-muted">No queries recorded yet. Ask a question to populate telemetry.</p>
        ) : (
          <Table>
            <thead className="border-b border-line/70">
              <tr>
                <th className="px-4 py-2 font-medium">Query</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Latency</th>
                <th className="px-4 py-2 font-medium">Citations</th>
                <th className="px-4 py-2 font-medium">When</th>
              </tr>
            </thead>
            <tbody>
              {data.recent_queries.map((query) => (
                <tr key={query.id} className="border-t border-line/70">
                  <td className="max-w-[22rem] truncate px-4 py-2">{query.query_text}</td>
                  <td className="px-4 py-2"><StatusBadge status={query.status} /></td>
                  <td className="px-4 py-2 font-mono text-xs">{formatMs(query.total_ms)}</td>
                  <td className="px-4 py-2 font-mono text-xs">{query.citation_count}</td>
                  <td className="px-4 py-2 text-xs text-muted">{formatDate(query.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </Table>
        )}
      </Card>
    </div>
  );
}
