"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { Button, Card, UploadZone } from "@/components/ui";
import { ragApi } from "@/lib/rag/api";
import { formatDate } from "@/lib/rag/format";
import {
  documentBuckets,
  documentStatus,
  queryStatus,
} from "@/lib/rag/presentation";
import {
  DocumentStatusBadge,
  Loading,
  Notice,
  SectionHeading,
  UserErrorNotice,
} from "./shared";

const ACCEPTED = ".pdf,.txt,.md,.markdown,text/plain,text/markdown,application/pdf";

export function HomePanel({
  onAsk,
  onOpenDocuments,
}: {
  onAsk: (query: string, documentIds: string[]) => void;
  onOpenDocuments: (documentId?: string) => void;
}) {
  const queryClient = useQueryClient();
  const [actionError, setActionError] = useState<unknown>(null);

  const documents = useQuery({
    queryKey: ["documents"],
    queryFn: ragApi.documents,
    refetchInterval: (query) => {
      const data = query.state.data;
      return data?.some((doc) => doc.status === "Processing" || doc.status === "Uploaded")
        ? 4000
        : false;
    },
  });

  const overview = useQuery({ queryKey: ["overview"], queryFn: ragApi.overview });

  const upload = useMutation({
    mutationFn: ragApi.upload,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      await queryClient.invalidateQueries({ queryKey: ["overview"] });
    },
    onError: (error) => setActionError(error),
  });

  const onFiles = (files: File[]) => {
    setActionError(null);
    const file = files[0];
    if (file) upload.mutate(file);
  };

  const buckets = documentBuckets(documents.data ?? []);
  const recentDocuments = [...(documents.data ?? [])]
    .sort((left, right) => Date.parse(right.importDate) - Date.parse(left.importDate))
    .slice(0, 4);
  const recentQuestions = overview.data?.recent_queries.slice(0, 4) ?? [];
  const nothingReady = buckets.total > 0 && buckets.ready.length === 0;

  return (
    <div className="space-y-8">
      <SectionHeading
        eyebrow="Home"
        title="Find answers in your documents."
        detail="Kogniq reads the documents you add, finds the passages that matter, and shows you where each answer comes from."
        actions={
          <>
            <Button onClick={() => onAsk("", [])}>Ask a question</Button>
            <Button variant="secondary" onClick={() => onOpenDocuments()}>
              My documents
            </Button>
          </>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="min-w-0 space-y-4">
          <Card className="p-5">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <h3 className="section-title">Your documents</h3>
              <button
                type="button"
                onClick={() => onOpenDocuments()}
                className="text-xs text-muted underline decoration-line underline-offset-4 transition-colors hover:text-ink hover:decoration-line-strong"
              >
                Manage documents
              </button>
            </div>

            {documents.isLoading ? (
              <Loading label="Loading your documents" />
            ) : documents.error ? (
              <div className="mt-4">
                <UserErrorNotice error={documents.error} onRetry={() => documents.refetch()} />
              </div>
            ) : (
              <>
                <div className="mt-4 grid grid-cols-2 gap-px border-y border-line/60 bg-line/60 sm:grid-cols-4">
                  {[
                    ["Ready to use", buckets.ready.length],
                    ["Preparing", buckets.preparing.length],
                    ["Needs attention", buckets.attention.length],
                    ["Not prepared", buckets.unprepared.length],
                  ].map(([label, count]) => (
                    <div key={String(label)} className="bg-canvas px-3 py-3">
                      <p className="eyebrow leading-4">{label}</p>
                      <p className="mt-2 font-mono text-lg leading-none text-ink">{count}</p>
                    </div>
                  ))}
                </div>

                {buckets.total === 0 ? (
                  <div className="mt-5 border-t border-line/60 pt-5">
                    <h4 className="text-[1.05rem] font-medium tracking-[-0.02em] text-ink">
                      Start with a document.
                    </h4>
                    <p className="mt-2 max-w-md text-sm leading-6 text-muted">
                      Add a PDF, plain-text file, or Markdown file. Once Kogniq finishes preparing
                      it, you can ask questions and read the passages behind every answer.
                    </p>
                    <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                      Use the upload area on this page
                    </p>
                  </div>
                ) : nothingReady ? (
                  <div className="mt-5 border-t border-line/60 pt-5">
                    <h4 className="text-[1.05rem] font-medium tracking-[-0.02em] text-ink">
                      Your documents are not ready yet.
                    </h4>
                    <p className="mt-2 max-w-md text-sm leading-6 text-muted">
                      {buckets.preparing.length
                        ? "Kogniq is still preparing them. They will become available automatically when that finishes."
                        : "Open My Documents to prepare them, or to see what went wrong."}
                    </p>
                    <Button className="mt-4" variant="secondary" size="sm" onClick={() => onOpenDocuments()}>
                      Open My Documents
                    </Button>
                  </div>
                ) : (
                  <ul className="mt-2">
                    {recentDocuments.map((doc) => {
                      const status = documentStatus(doc);
                      return (
                        <li
                          key={doc.id}
                          className="flex flex-wrap items-center justify-between gap-x-4 gap-y-2 border-b border-line/60 py-3 last:border-0"
                        >
                          <div className="min-w-0 flex-1">
                            <p className="truncate text-sm font-medium text-ink">{doc.title}</p>
                            <p className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-muted">
                              <DocumentStatusBadge document={doc} />
                              <span>Added {formatDate(doc.importDate)}</span>
                            </p>
                            {status.phase === "attention" ? (
                              <p className="mt-1 text-xs leading-5 text-muted">
                                Preparation stopped before this document was ready. Your original
                                file is still stored.
                              </p>
                            ) : null}
                          </div>
                          <div className="flex shrink-0 items-center gap-3">
                            {status.phase === "ready" ? (
                              <button
                                type="button"
                                onClick={() => onAsk("", [doc.id])}
                                className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
                              >
                                Ask about this
                              </button>
                            ) : null}
                            <button
                              type="button"
                              onClick={() => onOpenDocuments(doc.id)}
                              className="text-xs text-muted underline decoration-line underline-offset-4 transition-colors hover:text-ink hover:decoration-line-strong"
                            >
                              Open
                            </button>
                          </div>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </>
            )}
          </Card>

          <Card className="p-5">
            <div className="flex flex-wrap items-baseline justify-between gap-3">
              <h3 className="section-title">Recent questions</h3>
              {overview.data ? (
                <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
                  {overview.data.queries_7d.count} in the last 7 days
                </span>
              ) : null}
            </div>
            {overview.isLoading ? (
              <Loading label="Loading recent questions" />
            ) : overview.error ? (
              <div className="mt-3">
                <UserErrorNotice error={overview.error} onRetry={() => overview.refetch()} />
              </div>
            ) : recentQuestions.length === 0 ? (
              <p className="mt-3 text-sm leading-6 text-muted">
                Questions you ask will appear here, so you can return to them later.
              </p>
            ) : (
              <ul className="mt-2">
                {recentQuestions.map((question) => {
                  const status = queryStatus(question.status);
                  return (
                    <li key={question.id} className="border-b border-line/60 last:border-0">
                      <button
                        type="button"
                        onClick={() => onAsk(question.query_text, [])}
                        className="flex w-full flex-wrap items-baseline justify-between gap-x-4 gap-y-1 py-3 text-left"
                      >
                        <span className="min-w-0 flex-1 truncate text-sm text-ink">
                          {question.query_text}
                        </span>
                        <span className="flex shrink-0 items-center gap-3 text-[11px] text-muted">
                          <span>{status.label}</span>
                          <span>{formatDate(question.created_at)}</span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}
          </Card>
        </div>

        <div className="min-w-0 space-y-4">
          <Card className="p-5">
            <h3 className="section-title">Add a document</h3>
            <p className="mt-1 text-xs leading-5 text-muted">
              PDF, plain text, or Markdown. Up to 10 MB per file. Kogniq prepares it in the
              background.
            </p>
            <div className="mt-4">
              <UploadZone accept={ACCEPTED} onFiles={onFiles} />
            </div>
            {upload.isPending ? (
              <div className="mt-3">
                <Loading label="Uploading" />
              </div>
            ) : null}
            {upload.isSuccess ? (
              <div className="mt-3">
                <Notice tone="success" title="Upload received">
                  {upload.data.title} is being prepared. It will say “Ready to use” when you can ask
                  questions about it.
                </Notice>
              </div>
            ) : null}
            <div className="mt-3">
              <UserErrorNotice error={actionError} />
            </div>
          </Card>

          <Card className="p-5">
            <h3 className="section-title">What to expect</h3>
            <ol className="mt-3 space-y-3 text-sm leading-6 text-muted">
              <li className="flex gap-3">
                <span className="font-mono text-[10px] text-muted">01</span>
                <span>Add a document. Kogniq reads it and prepares it for search.</span>
              </li>
              <li className="flex gap-3">
                <span className="font-mono text-[10px] text-muted">02</span>
                <span>Ask a question in your own words.</span>
              </li>
              <li className="flex gap-3">
                <span className="font-mono text-[10px] text-muted">03</span>
                <span>
                  Read the answer and open the passages that support it. If the documents do not
                  contain an answer, Kogniq says so.
                </span>
              </li>
            </ol>
          </Card>
        </div>
      </div>
    </div>
  );
}
