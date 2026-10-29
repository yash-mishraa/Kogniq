"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { EntryExperience } from "@/components/experience/entry";
import { Footline } from "@/components/experience/footer";
import { Button } from "@/components/ui";
import { cn } from "@/lib/utils";
import { ApiRequestError, ragApi } from "@/lib/rag/api";
import { ActivityPanel } from "./ActivityPanel";
import { AskPanel } from "./AskPanel";
import { ChunkingPanel } from "./ChunkingPanel";
import { DocumentsPanel } from "./DocumentsPanel";
import { EvaluationPanel } from "./EvaluationPanel";
import { FlashcardsPanel } from "./FlashcardsPanel";
import { HomePanel } from "./HomePanel";
import { KnowledgeGraphPanel } from "./KnowledgeGraphPanel";
import { OverviewPanel } from "./OverviewPanel";
import { QuizzesPanel } from "./QuizzesPanel";
import { RetrievalPanel } from "./RetrievalPanel";
import { UserErrorNotice } from "./shared";

type EverydayView = "home" | "documents" | "ask" | "flashcards" | "quizzes" | "knowledge";
type EngineeringView = "overview" | "chunking" | "retrieval" | "evaluation" | "activity";
type View = EverydayView | EngineeringView;

const EVERYDAY_NAV: { id: EverydayView; label: string }[] = [
  { id: "home", label: "Home" },
  { id: "documents", label: "My Documents" },
  { id: "ask", label: "Ask Questions" },
  { id: "flashcards", label: "Flashcards" },
  { id: "quizzes", label: "Quizzes" },
  { id: "knowledge", label: "Knowledge Graph" },
];

const ENGINEERING_NAV: { id: EngineeringView; label: string; hint: string }[] = [
  { id: "overview", label: "Overview", hint: "System, index, and quality" },
  { id: "chunking", label: "Chunking", hint: "Preview and compare" },
  { id: "retrieval", label: "Retrieval", hint: "Hybrid search" },
  { id: "evaluation", label: "Evaluation", hint: "Measure quality" },
  { id: "activity", label: "Activity", hint: "Query telemetry" },
];

function isEngineering(view: View): view is EngineeringView {
  return ENGINEERING_NAV.some((item) => item.id === view);
}

const VIEW_LABELS: Record<View, string> = {
  home: "Home",
  documents: "My Documents",
  ask: "Ask Questions",
  flashcards: "Flashcards",
  quizzes: "Quizzes",
  knowledge: "Knowledge Graph",
  overview: "Engineering overview",
  chunking: "Chunking",
  retrieval: "Retrieval",
  evaluation: "Evaluation",
  activity: "Activity",
};

export function RagConsole() {
  const [view, setView] = useState<View>("home");
  const [engineeringView, setEngineeringView] = useState<EngineeringView>("overview");
  const [visited, setVisited] = useState<Set<View>>(() => new Set<View>(["home"]));
  const [handoff, setHandoff] = useState<{ query: string; documentIds: string[] }>({
    query: "",
    documentIds: [],
  });
  const [documentFocus, setDocumentFocus] = useState<{ id: string; token: number } | null>(null);

  const session = useQuery({
    queryKey: ["session"],
    queryFn: ragApi.session,
    retry: false,
    staleTime: 60_000,
  });

  const go = (next: View) => {
    if (isEngineering(next)) setEngineeringView(next);
    setView(next);
    setVisited((current) => {
      if (current.has(next)) return current;
      const updated = new Set(current);
      updated.add(next);
      return updated;
    });
  };

  const openDocuments = (documentId?: string) => {
    if (documentId) setDocumentFocus({ id: documentId, token: Date.now() });
    go("documents");
  };

  const openAsk = (query: string, documentIds: string[]) => {
    setHandoff({ query, documentIds });
    go("ask");
  };

  if (session.isLoading) return <Boot />;

  if (session.error) {
    const isAuthError = session.error instanceof ApiRequestError && session.error.status === 401;
    if (isAuthError) return <EntryExperience />;
    return <Unreachable error={session.error} onRetry={() => session.refetch()} />;
  }

  if (!session.data) return <EntryExperience />;

  return (
    <ConsoleShell
      email={session.data.email}
      view={view}
      visited={visited}
      onNavigate={go}
      onOpenEngineering={() => go(engineeringView)}
      handoff={handoff}
      documentFocus={documentFocus}
      onOpenDocuments={openDocuments}
      onAsk={openAsk}
    />
  );
}

function ConsoleShell({
  email,
  view,
  visited,
  onNavigate,
  onOpenEngineering,
  handoff,
  documentFocus,
  onOpenDocuments,
  onAsk,
}: {
  email: string;
  view: View;
  visited: Set<View>;
  onNavigate: (view: View) => void;
  onOpenEngineering: () => void;
  handoff: { query: string; documentIds: string[] };
  documentFocus: { id: string; token: number } | null;
  onOpenDocuments: (documentId?: string) => void;
  onAsk: (query: string, documentIds: string[]) => void;
}) {
  const engineering = isEngineering(view);

  return (
    <div className="flex min-h-dvh flex-col bg-canvas">
      <header className="sticky top-0 z-10 border-b border-line/70 bg-canvas/85 backdrop-blur">
        <div className="mx-auto flex w-full max-w-[1440px] items-center justify-between gap-6 px-6 py-4 sm:px-10">
          <button
            type="button"
            onClick={() => onNavigate("home")}
            aria-label="Kogniq home"
            className="kogniq-word text-[1.65rem] leading-none text-ink outline-none transition-opacity hover:opacity-80"
          >
            Kogniq
          </button>

          <nav aria-label="Primary" className="hidden items-center gap-5 lg:flex">
            {EVERYDAY_NAV.map((item) => {
              const active = view === item.id;
              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => onNavigate(item.id)}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "py-1 font-mono text-[10px] uppercase tracking-[0.16em] transition-colors",
                    active ? "text-ink" : "text-muted hover:text-ink",
                  )}
                >
                  <span
                    aria-hidden
                    className={cn(
                      "mr-2 inline-block w-1 text-center align-middle",
                      active ? "text-accent" : "text-transparent",
                    )}
                  >
                    •
                  </span>
                  {item.label}
                </button>
              );
            })}
            <span aria-hidden className="h-3 w-px bg-line" />
            <button
              type="button"
              onClick={onOpenEngineering}
              aria-current={engineering ? "page" : undefined}
              className={cn(
                "py-1 font-mono text-[10px] uppercase tracking-[0.16em] transition-colors",
                engineering ? "text-ink" : "text-muted hover:text-ink",
              )}
            >
              <span
                aria-hidden
                className={cn(
                  "mr-2 inline-block w-1 text-center align-middle",
                  engineering ? "text-accent" : "text-transparent",
                )}
              >
                •
              </span>
              Engineering Console
            </button>
          </nav>

          <div className="flex items-center gap-4">
            <span className="hidden max-w-[16rem] truncate font-mono text-[10px] text-muted xl:block">
              {email}
            </span>
            <SignOutButton />
          </div>
        </div>

        <nav
          aria-label="Primary"
          className="flex gap-1 overflow-x-auto border-t border-line/60 px-4 lg:hidden"
        >
          {EVERYDAY_NAV.map((item) => {
            const active = view === item.id;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onNavigate(item.id)}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "shrink-0 border-b-2 px-3 py-3 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors",
                  active ? "border-accent text-ink" : "border-transparent text-muted",
                )}
              >
                {item.label}
              </button>
            );
          })}
          <button
            type="button"
            onClick={onOpenEngineering}
            aria-current={engineering ? "page" : undefined}
            className={cn(
              "shrink-0 border-b-2 px-3 py-3 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors",
              engineering ? "border-accent text-ink" : "border-transparent text-muted",
            )}
          >
            Engineering Console
          </button>
        </nav>

        {engineering ? (
          <div className="border-t border-line/60 bg-canvas/70">
            <div className="mx-auto flex w-full max-w-[1440px] items-center gap-5 overflow-x-auto px-6 py-2.5 sm:px-10">
              <span className="shrink-0 font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
                Engineering
              </span>
              <nav aria-label="Engineering console sections" className="flex items-center gap-5">
                {ENGINEERING_NAV.map((item) => {
                  const active = view === item.id;
                  return (
                    <button
                      key={item.id}
                      type="button"
                      onClick={() => onNavigate(item.id)}
                      aria-current={active ? "page" : undefined}
                      title={item.hint}
                      className={cn(
                        "shrink-0 border-b py-1 font-mono text-[10px] uppercase tracking-[0.14em] transition-colors",
                        active
                          ? "border-accent text-ink"
                          : "border-transparent text-muted hover:text-ink",
                      )}
                    >
                      {item.label}
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>
        ) : null}
      </header>

      <main className="mx-auto w-full max-w-[1440px] flex-1 px-6 py-10 sm:px-10 sm:py-14">
        <h1 className="sr-only">{VIEW_LABELS[view]} — Kogniq</h1>

        <section hidden={view !== "home"} className={view === "home" ? "panel-enter" : undefined}>
          {visited.has("home") ? (
            <HomePanel onAsk={onAsk} onOpenDocuments={onOpenDocuments} />
          ) : null}
        </section>

        <section
          hidden={view !== "documents"}
          className={view === "documents" ? "panel-enter" : undefined}
        >
          {visited.has("documents") ? (
            <DocumentsPanel focus={documentFocus} onAsk={(id) => onAsk("", [id])} />
          ) : null}
        </section>

        <section hidden={view !== "ask"} className={view === "ask" ? "panel-enter" : undefined}>
          {visited.has("ask") ? (
            <AskPanel
              initialQuery={handoff.query}
              initialDocumentIds={handoff.documentIds}
              onOpenDocument={onOpenDocuments}
              onOpenDocuments={() => onOpenDocuments()}
            />
          ) : null}
        </section>

        <section
          hidden={view !== "flashcards"}
          className={view === "flashcards" ? "panel-enter" : undefined}
        >
          {visited.has("flashcards") ? (
            <FlashcardsPanel
              initialDocumentId={handoff.documentIds[0]}
              onOpenDocuments={() => onOpenDocuments()}
            />
          ) : null}
        </section>

        <section
          hidden={view !== "quizzes"}
          className={view === "quizzes" ? "panel-enter" : undefined}
        >
          {visited.has("quizzes") ? (
            <QuizzesPanel
              initialDocumentId={handoff.documentIds[0]}
              onOpenDocuments={() => onOpenDocuments()}
            />
          ) : null}
        </section>

        <section
          hidden={view !== "knowledge"}
          className={view === "knowledge" ? "panel-enter" : undefined}
        >
          {visited.has("knowledge") ? (
            <KnowledgeGraphPanel
              initialDocumentId={handoff.documentIds[0]}
              onOpenDocuments={() => onOpenDocuments()}
            />
          ) : null}
        </section>

        <section
          hidden={view !== "overview"}
          className={view === "overview" ? "panel-enter" : undefined}
        >
          {visited.has("overview") ? (
            <OverviewPanel onOpenActivity={() => onNavigate("activity")} />
          ) : null}
        </section>

        <section
          hidden={view !== "chunking"}
          className={view === "chunking" ? "panel-enter" : undefined}
        >
          {visited.has("chunking") ? <ChunkingPanel /> : null}
        </section>

        <section
          hidden={view !== "retrieval"}
          className={view === "retrieval" ? "panel-enter" : undefined}
        >
          {visited.has("retrieval") ? <RetrievalPanel onAsk={onAsk} /> : null}
        </section>

        <section
          hidden={view !== "evaluation"}
          className={view === "evaluation" ? "panel-enter" : undefined}
        >
          {visited.has("evaluation") ? <EvaluationPanel /> : null}
        </section>

        <section
          hidden={view !== "activity"}
          className={view === "activity" ? "panel-enter" : undefined}
        >
          {visited.has("activity") ? <ActivityPanel /> : null}
        </section>
      </main>

      <footer className="border-t border-line/60">
        <div className="mx-auto flex w-full max-w-[1440px] flex-wrap items-center justify-between gap-4 px-6 py-6 sm:px-10">
          <Footline />
          <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
            Everyday workspace · Engineering console
          </p>
        </div>
      </footer>
    </div>
  );
}

function SignOutButton() {
  const queryClient = useQueryClient();
  const logout = useMutation({
    mutationFn: ragApi.logout,
    onSuccess: async () => {
      await queryClient.invalidateQueries();
    },
  });

  return (
    <button
      type="button"
      onClick={() => logout.mutate()}
      disabled={logout.isPending}
      className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted transition-colors hover:text-ink disabled:opacity-50"
    >
      {logout.isPending ? "Signing out…" : "Sign out"}
    </button>
  );
}

function Boot() {
  return (
    <main className="grid min-h-dvh place-items-center bg-canvas">
      <div className="flex items-baseline gap-2 text-ink">
        <span className="kogniq-word text-4xl leading-none">Kogniq</span>
        <span
          aria-hidden
          className="h-[1em] w-px animate-[quiet-pulse_1.6s_ease-in-out_infinite] bg-current"
        />
      </div>
      <span className="sr-only" role="status" aria-live="polite">
        Checking session
      </span>
    </main>
  );
}

function Unreachable({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  return (
    <main className="flex min-h-dvh flex-col bg-canvas px-6 py-7 text-ink sm:px-10 sm:py-9">
      <p className="kogniq-word text-[clamp(1.9rem,4vw,3.25rem)] leading-none">Kogniq</p>
      <div className="mx-auto flex w-full max-w-2xl flex-1 items-center py-16">
        <div>
          <p className="eyebrow">Connection</p>
          <h1 className="mt-4 text-[clamp(2rem,4vw,3.6rem)] font-medium leading-[1.02] tracking-[-0.055em]">
            Kogniq can’t connect right now.
          </h1>
          <p className="mt-4 max-w-md text-sm leading-6 text-muted">
            The app could not verify your session. Your documents are safe. Check that the service is
            running, then try again.
          </p>
          <div className="mt-6">
            <UserErrorNotice error={error} onRetry={onRetry} />
          </div>
          <Button className="mt-6" onClick={onRetry}>
            Try again
          </Button>
        </div>
      </div>
      <Footline />
    </main>
  );
}
