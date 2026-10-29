"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { Button, Card, Table } from "@/components/ui";
import { formatDate, formatMs } from "@/lib/rag/format";
import { ragApi } from "@/lib/rag/api";
import { ErrorNotice, KeyValue, Loading, Mono, Notice, SectionHeading, StatusBadge } from "./shared";

export function ActivityPanel() {
  const [limit, setLimit] = useState(50);
  const queries = useQuery({ queryKey: ["queries", limit], queryFn: () => ragApi.recentQueries(limit) });
  const readiness = useQuery({ queryKey: ["readiness"], queryFn: ragApi.readiness });

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Engineering console"
        title="Query telemetry"
        detail="Durable, user-scoped records of retrieval and generation. Prompts, answers, and source text are not persisted."
        actions={
          <Button variant="secondary" size="sm" onClick={() => queries.refetch()} disabled={queries.isFetching}>
            Refresh
          </Button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.3fr_0.7fr]">
        <Card className="p-5">
          <h3 className="section-title">What is recorded</h3>
          <dl className="mt-4">
            <KeyValue label="Identity" value="server-derived user ID" />
            <KeyValue label="Query text" value="stored (first 4,000 chars)" />
            <KeyValue label="Source text" value="never stored in telemetry" />
            <KeyValue label="Timings" value="retrieval, generation, total" />
            <KeyValue label="Counts" value="candidates, selected sources, citations" />
            <KeyValue label="Cache status" value="not_supported" />
          </dl>
        </Card>
        <Card className="p-5">
          <h3 className="section-title">Readiness</h3>
          {readiness.isLoading ? (
            <Loading label="Checking dependencies" />
          ) : readiness.error ? (
            <ErrorNotice error={readiness.error} />
          ) : (
            <div className="mt-3 space-y-2">
              <Notice tone={readiness.data?.ready ? "success" : "warning"}>
                {readiness.data?.ready ? "All checks passed." : "One or more checks are degraded."}
              </Notice>
              {Object.entries(readiness.data?.checks ?? {}).map(([name, check]) => (
                <div key={name} className="flex items-center justify-between border-b border-line/60 py-1.5 last:border-0">
                  <Mono>{name}</Mono>
                  <StatusBadge status={check.ok ? "Ready" : "Failed"} />
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      <Card className="overflow-hidden">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
          <div>
            <h3 className="section-title">Recent queries</h3>
            <p className="mt-0.5 text-xs text-muted">
              Showing up to {limit} records. Cache status is reported honestly as not supported.
            </p>
          </div>
          <select
            className="h-8 rounded-sm border border-line bg-surface px-2 text-xs text-ink outline-none focus:border-accent"
            value={limit}
            onChange={(event) => setLimit(Number(event.target.value))}
          >
            {[25, 50, 100, 200].map((value) => (
              <option key={value} value={value}>
                Last {value}
              </option>
            ))}
          </select>
        </div>
        {queries.isLoading ? (
          <Loading label="Loading telemetry" />
        ) : queries.error ? (
          <div className="p-5"><ErrorNotice error={queries.error} /></div>
        ) : !queries.data?.queries.length ? (
          <p className="px-5 py-8 text-sm text-muted">No queries recorded yet.</p>
        ) : (
          <Table>
            <thead className="border-b border-line/70">
              <tr>
                <th className="px-4 py-2 font-medium">Query</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Candidates</th>
                <th className="px-4 py-2 font-medium">Selected</th>
                <th className="px-4 py-2 font-medium">Citations</th>
                <th className="px-4 py-2 font-medium">Retrieval</th>
                <th className="px-4 py-2 font-medium">Generation</th>
                <th className="px-4 py-2 font-medium">Total</th>
                <th className="px-4 py-2 font-medium">When</th>
              </tr>
            </thead>
            <tbody>
              {queries.data.queries.map((query) => (
                <tr key={query.id} className="border-t border-line/70">
                  <td className="max-w-[22rem] px-4 py-2">
                    <span className="block truncate">{query.query_text}</span>
                    <span className="font-mono text-[10px] text-muted">{query.model ?? "—"}</span>
                  </td>
                  <td className="px-4 py-2"><StatusBadge status={query.status} /></td>
                  <td className="px-4 py-2 font-mono text-xs">{query.candidate_count ?? "—"}</td>
                  <td className="px-4 py-2 font-mono text-xs">{query.selected_count ?? "—"}</td>
                  <td className="px-4 py-2 font-mono text-xs">{query.citation_count}</td>
                  <td className="px-4 py-2 font-mono text-xs">{formatMs(query.retrieval_ms)}</td>
                  <td className="px-4 py-2 font-mono text-xs">{formatMs(query.generation_ms)}</td>
                  <td className="px-4 py-2 font-mono text-xs">{formatMs(query.total_ms)}</td>
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
