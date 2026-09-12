"use client";

import { useQuiz } from "@/app/workspace/environments/quiz/QuizContext";

export function QuizNavigator() {
  const { state, dispatch } = useQuiz();
  const question = state.questions[state.currentIndex];
  if (!question) return null;
  const submitted = Boolean(state.submittedQuestionIds[question.id]);
  const finalQuestion = state.currentIndex === state.questions.length - 1;
  return <footer className="mt-10 flex items-center justify-between border-t border-line pt-5"><p className="font-mono text-xs text-muted">Question {state.currentIndex + 1} of {state.questions.length}</p><div className="flex gap-3"><button type="button" className="rounded-sm px-3 py-2 text-sm text-ink transition-colors hover:bg-raised focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-45" disabled={state.currentIndex === 0} onClick={() => dispatch({ type: "PREVIOUS" })}>Previous</button>{submitted ? <button type="button" className="rounded-sm bg-accent px-4 py-2 text-sm text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" onClick={() => dispatch({ type: "NEXT" })}>{finalQuestion ? "Finish" : "Next"}</button> : <button type="button" className="rounded-sm bg-accent px-4 py-2 text-sm text-white transition-opacity hover:opacity-90 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-45" disabled={!state.selectedOptionIds[question.id]} onClick={() => dispatch({ type: "SUBMIT_CURRENT" })}>Check answer</button>}</div></footer>;
}
