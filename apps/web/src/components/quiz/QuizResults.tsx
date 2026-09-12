"use client";

import { useQuiz } from "@/app/workspace/environments/quiz/QuizContext";
import { quizScore } from "@/app/workspace/environments/quiz/QuizState";

export function QuizResults() {
  const { state, dispatch } = useQuiz();
  const score = quizScore(state);
  const total = state.questions.length;
  const percentage = total ? Math.round((score / total) * 100) : 0;
  return <section className="flex flex-1 flex-col justify-center"><p className="font-mono text-xs uppercase tracking-[0.18em] text-muted">Quiz complete</p><h2 className="mt-3 text-4xl tracking-tight text-ink">{percentage}% correct</h2><p className="mt-3 text-muted">{score} correct · {total - score} incorrect · {total} questions</p><div className="mt-8 flex gap-3"><button type="button" className="rounded-sm bg-accent px-4 py-2 text-sm text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => dispatch({ type: "RESTART" })}>Restart quiz</button><button type="button" className="rounded-sm px-4 py-2 text-sm text-ink transition-colors hover:bg-raised focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => dispatch({ type: "REVIEW", payload: { index: 0 } })}>Review answers</button></div></section>;
}
