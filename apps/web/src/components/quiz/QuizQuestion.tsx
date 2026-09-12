"use client";

import { useQuiz } from "@/app/workspace/environments/quiz/QuizContext";
import { isQuestionCorrect } from "@/app/workspace/environments/quiz/QuizState";

export function QuizQuestion() {
  const { state, dispatch } = useQuiz();
  const question = state.questions[state.currentIndex];
  if (!question) return null;

  const selectedOptionId = state.selectedOptionIds[question.id];
  const submitted = Boolean(state.submittedQuestionIds[question.id]);
  const correct = isQuestionCorrect(state, question.id);

  return <fieldset className="border-0 p-0"><legend className="max-w-3xl text-[clamp(1.6rem,3vw,2.5rem)] leading-tight tracking-tight text-ink">{question.question}</legend><div className="mt-8 grid gap-3" role="radiogroup" aria-label="Answer choices">{question.options.map((option) => {
    const selected = selectedOptionId === option.id;
    const optionIsCorrect = option.id === question.correctOptionId;
    const tone = submitted ? (optionIsCorrect ? "border-success bg-success/10" : selected ? "border-danger bg-danger/10" : "border-line bg-surface opacity-65") : selected ? "border-accent bg-accent/10" : "border-line bg-surface hover:bg-raised";
    return <label key={option.id} className={`flex cursor-pointer items-start gap-3 rounded-md border p-4 text-ink transition-colors ${tone} ${submitted ? "cursor-default" : ""}`}><input className="mt-1 size-4 accent-accent focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent" type="radio" name={question.id} value={option.id} checked={selected} disabled={submitted} onChange={() => dispatch({ type: "SELECT_OPTION", payload: { questionId: question.id, optionId: option.id } })} /><span><span className="mr-3 font-mono text-xs text-muted">{option.id}</span>{option.text}</span></label>;
  })}</div>{submitted && <div className={`mt-6 border-l-2 px-4 py-1 ${correct ? "border-success" : "border-danger"}`} role="status" aria-live="polite"><p className={`font-medium ${correct ? "text-success" : "text-danger"}`}>{correct ? "Correct" : "Not quite"}</p><p className="mt-2 leading-7 text-ink">{question.explanation}</p></div>}</fieldset>;
}
