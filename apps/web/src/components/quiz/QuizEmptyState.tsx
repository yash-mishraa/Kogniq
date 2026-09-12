export function QuizEmptyState({ hasDocument }: { hasDocument: boolean }) {
  return <div className="flex flex-1 flex-col justify-center"><p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">Quiz</p><h2 className="mt-3 text-3xl tracking-tight text-ink">{hasDocument ? "No quiz available" : "Choose a document first"}</h2><p className="mt-3 max-w-lg leading-7 text-muted">{hasDocument ? "This document has no persisted quiz material yet." : "Select a ready document in Documents, then return here to test your understanding."}</p></div>;
}
