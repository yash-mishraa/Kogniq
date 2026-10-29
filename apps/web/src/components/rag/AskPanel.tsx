"use client";

import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { Button, Card, Textarea } from "@/components/ui";
import { ragApi } from "@/lib/rag/api";
import { formatMs } from "@/lib/rag/format";
import { answerOutcome } from "@/lib/rag/presentation";
import { AnswerBody } from "./AnswerBody";
import { DocumentPicker } from "./DocumentPicker";
import {
  Disclosure,
  KeyValue,
  Loading,
  Notice,
  SectionHeading,
  UserErrorNotice,
} from "./shared";

export function AskPanel({
  initialQuery,
  initialDocumentIds,
  onOpenDocument,
  onOpenDocuments,
}: {
  initialQuery: string;
  initialDocumentIds: string[];
  onOpenDocument: (documentId: string) => void;
  onOpenDocuments: () => void;
}) {
  const [query, setQuery] = useState(initialQuery);
  const [documentIds, setDocumentIds] = useState(initialDocumentIds);
  const [topK, setTopK] = useState(6);
  const [minimumSimilarity, setMinimumSimilarity] = useState(0.25);
  const answer = useMutation({ mutationFn: ragApi.ask });

  useEffect(() => {
    if (initialQuery) setQuery(initialQuery);
  }, [initialQuery]);

  useEffect(() => {
    setDocumentIds(initialDocumentIds);
  }, [initialDocumentIds]);

  const run = () => {
    if (!query.trim()) return;
    answer.mutate({
      query: query.trim(),
      document_ids: documentIds,
      top_k: topK,
      minimum_similarity: minimumSimilarity,
    });
  };

  const data = answer.data;
  const outcome = data ? answerOutcome(data) : null;
  const validSourceIds = data?.citations.map((citation) => citation.source_id) ?? [];
  const cited = new Set(validSourceIds);

  return (
    <div className="space-y-6">
      <SectionHeading
        eyebrow="Ask questions"
        title="Ask questions about your documents"
        detail="Choose the documents you want Kogniq to search, then ask in your own words. Every answer shows the passages it came from."
      />

      <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="min-w-0 space-y-4 p-5">
          <div>
            <label htmlFor="ask-question" className="eyebrow">
              Your question
            </label>
            <Textarea
              id="ask-question"
              className="mt-1.5 min-h-28"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                  event.preventDefault();
                  run();
                }
              }}
              placeholder="What are the main findings of this document?"
            />
            <p className="mt-2 text-[11px] leading-5 text-muted">
              Ask about anything the selected documents should be able to answer. Press Command or
              Control and Enter to submit.
            </p>
          </div>

          <DocumentPicker value={documentIds} onChange={setDocumentIds} />

          <Disclosure label="Search settings" openLabel="Hide search settings">
            <div className="grid grid-cols-2 gap-3">
              <label className="block">
                <span className="eyebrow">Passages to consider</span>
                <input
                  className="mt-1.5 h-9 w-full rounded-sm border border-line bg-transparent px-3 text-sm text-ink outline-none transition-colors hover:border-line-strong focus:border-accent focus:ring-1 focus:ring-accent/25"
                  type="number"
                  min={1}
                  max={20}
                  value={topK}
                  onChange={(event) => setTopK(Number(event.target.value))}
                />
                <span className="mt-1 block text-[10px] leading-4 text-muted">Between 1 and 20.</span>
              </label>
              <label className="block">
                <span className="eyebrow">Minimum match strength</span>
                <input
                  className="mt-1.5 h-9 w-full rounded-sm border border-line bg-transparent px-3 text-sm text-ink outline-none transition-colors hover:border-line-strong focus:border-accent focus:ring-1 focus:ring-accent/25"
                  type="number"
                  min={0}
                  max={1}
                  step={0.05}
                  value={minimumSimilarity}
                  onChange={(event) => setMinimumSimilarity(Number(event.target.value))}
                />
                <span className="mt-1 block text-[10px] leading-4 text-muted">
                  Lower values include weaker matches.
                </span>
              </label>
            </div>
          </Disclosure>

          <div className="flex flex-wrap items-center gap-3">
            <Button onClick={run} disabled={!query.trim() || answer.isPending}>
              {answer.isPending ? "Finding an answer…" : "Ask"}
            </Button>
            {answer.isPending ? (
              <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
                Searching your documents
              </span>
            ) : null}
          </div>
          <UserErrorNotice error={answer.error} onRetry={run} />
        </Card>

        <Card className="min-w-0 p-5">
          <h3 className="section-title">How answers work</h3>
          <ol className="mt-4 space-y-4 text-sm leading-6 text-muted">
            <li className="flex gap-3">
              <span className="font-mono text-[10px] text-muted">01</span>
              <span>Kogniq searches only the documents you select.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-[10px] text-muted">02</span>
              <span>
                The answer is written from the passages it finds, and every claim should point to
                one of them.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-[10px] text-muted">03</span>
              <span>
                If the documents do not contain enough information, Kogniq says so instead of
                guessing.
              </span>
            </li>
            <li className="flex gap-3">
              <span className="font-mono text-[10px] text-muted">04</span>
              <span>You can open any supporting passage in its document.</span>
            </li>
          </ol>
        </Card>
      </div>

      {answer.isPending ? <Loading label="Searching your documents and writing an answer" /> : null}

      {data && outcome ? (
        <div className="space-y-4">
          {outcome.message ? (
            <Notice tone={outcome.tone} title={outcome.label}>
              {outcome.message}
            </Notice>
          ) : (
            <Notice tone="success" title={outcome.label}>
              This answer is supported by {data.citations.length} cited passage
              {data.citations.length === 1 ? "" : "s"} from your documents.
            </Notice>
          )}

          <Card className="p-5">
            <p className="eyebrow">Answer</p>
            <p className="mt-2 text-xs leading-5 text-muted">{data.query}</p>
            <div className="mt-4">
              <AnswerBody answer={data.answer} validSourceIds={validSourceIds} />
            </div>
            <p className="mt-5 border-t border-line/60 pt-4 text-xs leading-5 text-muted">
              {outcome.tone === "success"
                ? "Open a supporting passage below to read it in context, or ask a follow-up question."
                : "Try selecting more documents or asking a narrower question. You can also open My Documents to check what is ready to search."}
            </p>
            {outcome.tone !== "success" ? (
              <Button className="mt-3" variant="secondary" size="sm" onClick={onOpenDocuments}>
                Open My Documents
              </Button>
            ) : null}
          </Card>

          {data.citations.length ? (
            <Card className="p-5">
              <h3 className="section-title">Where this answer comes from</h3>
              <p className="mt-1 text-xs leading-5 text-muted">
                These passages were checked against the answer. Select one to read it in its
                document.
              </p>
              <div className="mt-4 space-y-3">
                {data.citations.map((citation) => (
                  <article
                    id={`citation-${citation.source_id}`}
                    key={citation.source_id}
                    className="scroll-mt-24 rounded-sm border border-accent/30 bg-accent/5 p-4"
                  >
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1">
                      <span className="rounded-xs bg-accent/10 px-1.5 py-0.5 font-mono text-[10px] text-accent">
                        {citation.source_id}
                      </span>
                      <span className="text-sm font-medium text-ink">{citation.document_title}</span>
                      {citation.page_number !== null && citation.page_number !== undefined ? (
                        <span className="text-xs text-muted">Page {citation.page_number}</span>
                      ) : null}
                      {citation.section_title ? (
                        <span className="truncate text-xs text-muted">{citation.section_title}</span>
                      ) : null}
                    </div>
                    <p className="mt-2 text-sm leading-6 text-ink/90">{citation.excerpt}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-4">
                      <button
                        type="button"
                        onClick={() => onOpenDocument(citation.document_id)}
                        className="text-xs text-accent underline decoration-accent/40 underline-offset-4 transition-colors hover:decoration-accent"
                      >
                        View in document
                      </button>
                      <a
                        href={`#source-${citation.source_id}`}
                        className="text-xs text-muted underline decoration-line underline-offset-4 transition-colors hover:text-ink hover:decoration-line-strong"
                      >
                        Read the full passage
                      </a>
                    </div>
                  </article>
                ))}
              </div>
            </Card>
          ) : (
            <Notice tone="warning" title="No supporting passages">
              Kogniq did not find a valid passage to support this answer, so it is not presented as
              grounded in your documents.
            </Notice>
          )}

          {data.sources.length ? (
            <Card className="p-5">
              <h3 className="section-title">Passages Kogniq used</h3>
              <p className="mt-1 text-xs leading-5 text-muted">
                The passages retrieved from your documents for this question. Cited passages are
                marked.
              </p>
              <div className="mt-4 space-y-2">
                {data.sources.map((source) => (
                  <article
                    id={`source-${source.source_id}`}
                    key={source.chunk_id}
                    className={`scroll-mt-24 rounded-sm border p-3 ${
                      cited.has(source.source_id)
                        ? "border-accent/40 bg-accent/5"
                        : "bg-raised/20"
                    }`}
                  >
                    <header className="flex flex-wrap items-center gap-x-4 gap-y-1 text-[11px] text-muted">
                      <span className="font-mono text-accent">{source.source_id}</span>
                      <span className="font-medium text-ink">{source.document_title}</span>
                      <span>Passage {source.chunk_index + 1}</span>
                      {source.page_number !== null && source.page_number !== undefined ? (
                        <span>Page {source.page_number}</span>
                      ) : null}
                      {source.section_title ? (
                        <span className="truncate">{source.section_title}</span>
                      ) : null}
                      <span className={cited.has(source.source_id) ? "text-accent" : ""}>
                        {cited.has(source.source_id) ? "Cited in the answer" : "Not cited"}
                      </span>
                    </header>
                    <p className="mt-2 text-sm leading-6 text-ink/90">{source.excerpt}</p>
                    <Disclosure label="Read the full passage" openLabel="Hide the full passage" className="mt-3">
                      <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink/90">
                        {source.text}
                      </p>
                    </Disclosure>
                  </article>
                ))}
              </div>
            </Card>
          ) : null}

          <Card className="p-5">
            <Disclosure label="View technical details" openLabel="Hide technical details">
              <dl className="grid gap-x-8 sm:grid-cols-2">
                <KeyValue label="Stored status" value={data.status} />
                <KeyValue label="Grounded" value={data.grounded ? "yes" : "no"} />
                <KeyValue label="Retrieval strategy" value={data.strategy} />
                <KeyValue label="Retrieved passages" value={data.sources.length} />
                <KeyValue
                  label="Validated citations"
                  value={`${data.citations.length} of ${data.sources.length} supplied`}
                />
                <KeyValue label="Retrieval time" value={formatMs(data.timings.retrieval_ms)} />
                <KeyValue label="Generation time" value={formatMs(data.timings.generation_ms)} />
                <KeyValue label="Total time" value={formatMs(data.timings.total_ms)} />
                <KeyValue label="Provider" value={data.provider ?? "not reported"} />
                <KeyValue label="Model" value={data.model ?? "not reported"} />
                <KeyValue
                  label="Tokens"
                  value={
                    data.usage.total_tokens
                      ? `${data.usage.prompt_tokens ?? "—"} prompt · ${data.usage.completion_tokens ?? "—"} completion · ${data.usage.total_tokens} total`
                      : "not reported"
                  }
                />
                <KeyValue label="Prompt cache" value={data.cache_status} />
              </dl>
              {data.warnings.length ? (
                <div className="mt-4 space-y-2">
                  <p className="eyebrow">Warnings</p>
                  {data.warnings.map((warning) => (
                    <p
                      key={warning}
                      className="whitespace-pre-wrap break-words font-mono text-[11px] leading-5 text-muted"
                    >
                      {warning}
                    </p>
                  ))}
                </div>
              ) : null}
            </Disclosure>
          </Card>
        </div>
      ) : null}
    </div>
  );
}
