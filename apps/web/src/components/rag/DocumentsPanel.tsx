"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Button, Card, Table, UploadZone } from "@/components/ui";
import { formatDate } from "@/lib/rag/format";
import { ragApi, type ChunkInspection, type DocumentSummary } from "@/lib/rag/api";
import {
  documentAction,
  documentBuckets,
  documentStatus,
} from "@/lib/rag/presentation";
import {
  Disclosure,
  DocumentStatusBadge,
  KeyValue,
  Loading,
  Notice,
  SectionHeading,
  UserErrorNotice,
} from "./shared";

const ACCEPTED =
  ".pdf,.txt,.md,.markdown,.tex,.latex,text/plain,text/markdown,application/pdf,application/x-tex,text/x-tex";

export function DocumentsPanel({
  focus,
  onAsk,
}: {
  focus: { id: string; token: number } | null;
  onAsk: (documentId: string) => void;
}) {
  const queryClient = useQueryClient();
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [chunkLimit, setChunkLimit] = useState(60);
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

  useEffect(() => {
    if (!focus) return;
    setSelectedId(focus.id);
  }, [focus]);

  useEffect(() => {
    if (!selectedId) return;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const timer = window.setTimeout(() => {
      document
        .getElementById("document-detail")
        ?.scrollIntoView({ behavior: reduceMotion ? "auto" : "smooth", block: "start" });
    }, 80);
    return () => window.clearTimeout(timer);
  }, [selectedId, focus?.token]);

  const upload = useMutation({
    mutationFn: ragApi.upload,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents"] });
      await queryClient.invalidateQueries({ queryKey: ["overview"] });
    },
    onError: (error) => setActionError(error),
  });

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ["documents"] });
    await queryClient.invalidateQueries({ queryKey: ["overview"] });
  };

  const retry = useMutation({
    mutationFn: ragApi.retry,
    onSuccess: invalidate,
    onError: (error) => setActionError(error),
  });
  const reindex = useMutation({
    mutationFn: ragApi.reindex,
    onSuccess: invalidate,
    onError: (error) => setActionError(error),
  });
  const remove = useMutation({
    mutationFn: ragApi.deleteDocument,
    onSuccess: async (_, id) => {
      if (selectedId === id) setSelectedId(null);
      await invalidate();
    },
    onError: (error) => setActionError(error),
  });

  const chunks = useQuery({
    queryKey: ["chunks", selectedId, chunkLimit],
    queryFn: () => ragApi.documentChunks(selectedId!, chunkLimit),
    enabled: Boolean(selectedId),
  });

  const onFiles = (files: File[]) => {
    setActionError(null);
    const file = files[0];
    if (file) upload.mutate(file);
  };

  const buckets = documentBuckets(documents.data ?? []);
  const selectedDocument = documents.data?.find((doc) => doc.id === selectedId) ?? null;
  const busy = retry.isPending || reindex.isPending || remove.isPending;

  const runAction = (kind: "retry" | "prepare", id: string) => {
    setActionError(null);
    if (kind === "retry") retry.mutate(id);
    else reindex.mutate(id);
  };

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="My documents"
        title="Your documents"
        detail="Add documents, see when they are ready, and open the passages Kogniq can search. PDF, plain text, and Markdown, up to 10 MB per file."
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => documents.refetch()}
            disabled={documents.isFetching}
          >
            Refresh
          </Button>
        }
      />

      <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="min-w-0 p-5">
          <h3 className="section-title">Add a document</h3>
          <p className="mt-1 text-xs leading-5 text-muted">
            Drag a file into the area below or choose one from your device. Kogniq reads and
            prepares it in the background. It is searchable only after it says “Ready to use”.
          </p>
          <div className="mt-4">
            <UploadZone accept={ACCEPTED} onFiles={onFiles} />
          </div>
          <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
            PDF · TXT · Markdown · LaTeX · 10 MB maximum
          </p>
          {upload.isPending ? (
            <div className="mt-3">
              <Loading label="Uploading" />
            </div>
          ) : null}
          {upload.isSuccess ? (
            <div className="mt-3">
              <Notice tone="success" title="Upload received">
                {upload.data.title} is being prepared. Watch its status below; it will change to
                “Ready to use” when it can be searched.
              </Notice>
            </div>
          ) : null}
          <div className="mt-3">
            <UserErrorNotice error={actionError} />
          </div>
        </Card>

        <Card className="min-w-0 p-5">
          <h3 className="section-title">At a glance</h3>
          {documents.isLoading ? (
            <Loading label="Loading your documents" />
          ) : documents.error ? (
            <div className="mt-4">
              <UserErrorNotice error={documents.error} onRetry={() => documents.refetch()} />
            </div>
          ) : (
            <>
              <div className="mt-4 grid grid-cols-2 gap-px border-y border-line/60 bg-line/60">
                {[
                  ["Ready to use", buckets.ready.length],
                  ["Preparing", buckets.preparing.length],
                  ["Needs attention", buckets.attention.length],
                  ["Not prepared yet", buckets.unprepared.length],
                ].map(([label, count]) => (
                  <div key={String(label)} className="bg-canvas px-3 py-3">
                    <p className="eyebrow leading-4">{label}</p>
                    <p className="mt-2 font-mono text-lg leading-none text-ink">{count}</p>
                  </div>
                ))}
              </div>
              <p className="mt-4 text-xs leading-5 text-muted">
                {buckets.total === 0
                  ? "No documents yet. Add your first file to begin."
                  : `${buckets.total} document${buckets.total === 1 ? "" : "s"} in this workspace. Deleting a document also removes the passages Kogniq prepared from it.`}
              </p>
            </>
          )}
        </Card>
      </div>

      {buckets.attention.length ? (
        <Notice tone="warning" title="Some documents need attention">
          {buckets.attention.length} document{buckets.attention.length === 1 ? "" : "s"} could not be
          prepared. Your original file is still stored, so you can try again. Open a document for
          details.
        </Notice>
      ) : null}

      <Card className="overflow-hidden">
        <div className="border-b px-5 py-4">
          <h3 className="section-title">Library</h3>
        </div>
        {documents.isLoading ? (
          <Loading label="Loading library" />
        ) : documents.error ? (
          <div className="p-5">
            <UserErrorNotice error={documents.error} onRetry={() => documents.refetch()} />
          </div>
        ) : !documents.data?.length ? (
          <div className="px-5 py-8">
            <p className="text-sm font-medium text-ink">No documents yet.</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-muted">
              Upload a PDF, text, or Markdown file above. It becomes available for questions after
              Kogniq finishes preparing it.
            </p>
          </div>
        ) : (
          <Table>
            <thead className="border-b border-line/70">
              <tr>
                <th className="px-4 py-2 font-medium">Document</th>
                <th className="px-4 py-2 font-medium">Status</th>
                <th className="px-4 py-2 font-medium">Passages</th>
                <th className="px-4 py-2 font-medium">Added</th>
                <th className="px-4 py-2 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.data.map((doc) => {
                const action = documentAction(doc);
                return (
                  <tr key={doc.id} className="border-t border-line/70 align-top">
                    <td className="max-w-[22rem] px-4 py-3">
                      <button
                        type="button"
                        className="block max-w-full text-left"
                        onClick={() => setSelectedId(doc.id)}
                        title="Open the passages in this document"
                      >
                        <span className="block truncate font-medium text-ink underline decoration-transparent underline-offset-4 transition-colors hover:decoration-line-strong">
                          {doc.title}
                        </span>
                      </button>
                    </td>
                    <td className="px-4 py-3">
                      <DocumentStatusBadge document={doc} />
                    </td>
                    <td className="px-4 py-3">
                      <button
                        type="button"
                        onClick={() => setSelectedId(doc.id)}
                        className="text-xs text-muted underline decoration-line underline-offset-4 transition-colors hover:text-ink hover:decoration-line-strong"
                      >
                        {doc.chunk_count} passage{doc.chunk_count === 1 ? "" : "s"}
                      </button>
                    </td>
                    <td className="px-4 py-3 text-xs text-muted">{formatDate(doc.importDate)}</td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap items-center gap-3">
                        {action?.kind === "ask" ? (
                          <button
                            type="button"
                            onClick={() => onAsk(doc.id)}
                            className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
                          >
                            Ask about this
                          </button>
                        ) : null}
                        {action && action.kind !== "ask" ? (
                          <button
                            type="button"
                            onClick={() => runAction(action.kind, doc.id)}
                            disabled={busy}
                            className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent disabled:opacity-40"
                          >
                            {action.label}
                          </button>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => {
                            if (
                              window.confirm(
                                `Delete “${doc.title}”? This removes the document and the passages Kogniq prepared from it.`,
                              )
                            ) {
                              remove.mutate(doc.id);
                            }
                          }}
                          disabled={busy}
                          className="text-xs text-muted underline decoration-line underline-offset-4 transition-colors hover:text-danger hover:decoration-danger/40 disabled:opacity-40"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </Table>
        )}
      </Card>

      {selectedId ? (
        <Card id="document-detail" className="scroll-mt-24 overflow-hidden">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b px-5 py-4">
            <div className="min-w-0">
              <h3 className="section-title">Inside this document</h3>
              <p className="mt-0.5 text-xs leading-5 text-muted">
                {selectedDocument ? selectedDocument.title : "Selected document"} — these are the
                passages Kogniq can search and cite.
              </p>
            </div>
            <Button variant="ghost" size="sm" onClick={() => setSelectedId(null)}>
              Close
            </Button>
          </div>
          {chunks.isLoading ? (
            <Loading label="Loading passages" />
          ) : chunks.error ? (
            <div className="p-5">
              <UserErrorNotice error={chunks.error} onRetry={() => chunks.refetch()} />
            </div>
          ) : (
            <ChunkView
              inspection={chunks.data!}
              document={selectedDocument}
              busy={busy}
              onRetry={() => {
                if (!selectedDocument) return;
                const action = documentAction(selectedDocument);
                if (action?.kind === "retry") runAction("retry", selectedDocument.id);
                else runAction("prepare", selectedDocument.id);
              }}
              onAsk={onAsk}
              onLoadMore={() => setChunkLimit((value) => value + 60)}
            />
          )}
        </Card>
      ) : null}
    </div>
  );
}

function ChunkView({
  inspection,
  document,
  busy,
  onRetry,
  onAsk,
  onLoadMore,
}: {
  inspection: ChunkInspection;
  document: DocumentSummary | null;
  busy: boolean;
  onRetry: () => void;
  onAsk: (documentId: string) => void;
  onLoadMore: () => void;
}) {
  const status = document ? documentStatus(document) : null;
  const action = document ? documentAction(document) : null;
  const failed = status?.phase === "attention";

  return (
    <div className="space-y-4 p-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-3">
          {status ? <span className="eyebrow">{status.label}</span> : null}
          <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
            {inspection.chunk_count} passage{inspection.chunk_count === 1 ? "" : "s"}
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {action?.kind === "ask" && document ? (
            <button
              type="button"
              onClick={() => onAsk(document.id)}
              className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
            >
              Ask about this document
            </button>
          ) : null}
          {action && action.kind !== "ask" ? (
            <button
              type="button"
              onClick={onRetry}
              disabled={busy}
              className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent disabled:opacity-40"
            >
              {action.label}
            </button>
          ) : null}
        </div>
      </div>

      {failed ? (
        <Notice tone="danger" title="This document needs attention">
          Preparation stopped before the document was ready. Your original file is still stored, so
          you can try again. If it keeps failing, open the Engineering Console for the technical
          details.
        </Notice>
      ) : null}

      {status?.phase === "unprepared" ? (
        <Notice tone="warning" title="This document is not prepared yet">
          Kogniq has not prepared searchable passages for this file. Prepare it to start asking
          questions about it.
        </Notice>
      ) : null}

      {inspection.chunks.length === 0 ? (
        <p className="text-sm leading-6 text-muted">
          No passages are available yet.{" "}
          {action && action.kind !== "ask" ? "Prepare the document to create them." : null}
        </p>
      ) : (
        <div className="space-y-2">
          {inspection.chunks.map((chunk) => (
            <article key={chunk.id} className="rounded-sm border bg-raised/30 p-3">
              <header className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted">
                <span>Passage {chunk.chunk_index + 1}</span>
                {chunk.page_number !== null && chunk.page_number !== undefined ? (
                  <span>Page {chunk.page_number}</span>
                ) : null}
                {chunk.section_title ? (
                  <span className="truncate">{chunk.section_title}</span>
                ) : null}
              </header>
              <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-ink/90">
                {chunk.text}
              </p>
            </article>
          ))}
        </div>
      )}

      {inspection.chunks.length < inspection.chunk_count ? (
        <Button variant="secondary" size="sm" onClick={onLoadMore}>
          Show more passages
        </Button>
      ) : null}

      <Disclosure label="Technical details" openLabel="Hide technical details">
        <dl className="grid gap-x-8 sm:grid-cols-2">
          <KeyValue label="Document ID" value={inspection.document_id} />
          <KeyValue label="Stored status" value={inspection.status} />
          <KeyValue label="Passages stored" value={inspection.chunk_count} />
          <KeyValue label="Passages shown" value={inspection.chunks.length} />
          {document?.embedding_model ? (
            <KeyValue label="Embedding model" value={document.embedding_model} />
          ) : null}
          {document?.embedding_dimensions ? (
            <KeyValue label="Dimensions" value={document.embedding_dimensions} />
          ) : null}
          {document?.indexed_at ? (
            <KeyValue label="Indexed" value={formatDate(document.indexed_at)} />
          ) : null}
          {document?.chunker_config ? (
            <KeyValue label="Chunker" value={document.chunker_config} />
          ) : null}
        </dl>
        {document?.error ? (
          <div className="mt-3">
            <p className="eyebrow">Recorded error</p>
            <p className="mt-2 whitespace-pre-wrap break-words font-mono text-[11px] leading-5 text-muted">
              {document.error}
            </p>
          </div>
        ) : null}
      </Disclosure>
    </div>
  );
}
