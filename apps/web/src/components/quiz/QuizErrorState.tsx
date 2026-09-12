export function QuizErrorState({ error }: { error: Error | null }) {
  return <div className="flex flex-1 flex-col justify-center"><p className="font-mono text-xs uppercase tracking-[0.18em] text-danger">Quiz unavailable</p><h2 className="mt-3 text-3xl tracking-tight text-ink">We couldn’t load this quiz.</h2><p className="mt-3 max-w-lg leading-7 text-muted">{error?.message ?? "Please try again after the document’s learning materials are available."}</p></div>;
}
