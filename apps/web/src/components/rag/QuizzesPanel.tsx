"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  Award,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  RotateCcw,
  XCircle,
} from "lucide-react";
import { Button } from "@/components/ui";
import { QuizQuestionItemData, QuizQuestionOption, ragApi } from "@/lib/rag/api";
import { SectionHeading, UserErrorNotice } from "./shared";

interface QuizzesPanelProps {
  initialDocumentId?: string;
  onOpenDocuments?: () => void;
}

export function QuizzesPanel({ initialDocumentId, onOpenDocuments }: QuizzesPanelProps) {
  const queryClient = useQueryClient();
  const [selectedDocId, setSelectedDocId] = useState<string>(initialDocumentId || "");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Manual creation state
  const [manualQuestion, setManualQuestion] = useState("");
  const [manualOptions, setManualOptions] = useState(["", "", "", ""]);
  const [manualCorrectIndex, setManualCorrectIndex] = useState(0);
  const [manualExplanation, setManualExplanation] = useState("");
  const [manualDifficulty, setManualDifficulty] = useState("medium");

  const docsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: ragApi.documents,
  });

  const readyDocs = (docsQuery.data || []).filter((d) => d.status === "Ready");
  const activeDocId = selectedDocId || (readyDocs.length > 0 ? readyDocs[0].id : "");

  const quizQuery = useQuery({
    queryKey: ["quiz", activeDocId],
    queryFn: () => ragApi.getQuiz(activeDocId),
    enabled: Boolean(activeDocId),
  });

  const generateMutation = useMutation({
    mutationFn: () => ragApi.generateQuiz(activeDocId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["quiz", activeDocId] });
      setCurrentIndex(0);
      setUserAnswers({});
      setSubmitted(false);
    },
  });

  const addQuestionMutation = useMutation({
    mutationFn: () =>
      ragApi.addQuizQuestion(activeDocId, {
        question: manualQuestion,
        options: manualOptions.filter((o) => o.trim().length > 0),
        correct_answer: manualOptions[manualCorrectIndex] || manualOptions[0],
        explanation: manualExplanation,
        difficulty: manualDifficulty,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["quiz", activeDocId] });
      setManualQuestion("");
      setManualOptions(["", "", "", ""]);
      setManualExplanation("");
      setShowAddModal(false);
    },
  });

  const questions: QuizQuestionItemData[] = quizQuery.data || [];
  const currentQuestion: QuizQuestionItemData | undefined = questions[currentIndex];

  const handleSelectOption = (questionId: string, optionIdOrText: string) => {
    if (submitted) return;
    setUserAnswers((prev) => ({ ...prev, [questionId]: optionIdOrText }));
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q) => {
      const selected = userAnswers[q.id];
      const matchingOpt = q.options.find((o) => o.id === selected || o.text === selected);
      const isCorrect =
        selected &&
        (selected === q.correct_answer ||
          matchingOpt?.text.toLowerCase() === q.correct_answer.toLowerCase() ||
          matchingOpt?.id.toLowerCase() === q.correct_answer.toLowerCase());
      if (isCorrect) correct += 1;
    });
    return { score: correct, total: questions.length };
  };

  const handleRetake = () => {
    setUserAnswers({});
    setSubmitted(false);
    setCurrentIndex(0);
  };

  const scoreResult = submitted ? calculateScore() : null;

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 py-6 px-4">
      <SectionHeading
        eyebrow="Evaluation"
        title="Quizzes"
        detail="Test your comprehension with grounded multiple-choice questions."
      />

      {/* Document Selector & Actions */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 sm:gap-4 rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-3 sm:p-4">
        <div className="flex items-center gap-2 sm:gap-3 min-w-0">
          <span className="text-xs uppercase tracking-wider text-[#888888] shrink-0">Source:</span>
          <select
            value={activeDocId}
            onChange={(e) => {
              setSelectedDocId(e.target.value);
              setCurrentIndex(0);
              setUserAnswers({});
              setSubmitted(false);
            }}
            className="w-full sm:w-auto max-w-full sm:max-w-xs md:max-w-sm truncate rounded border border-[#262626] bg-[#141414] px-2.5 py-1.5 text-xs sm:text-sm text-[#f0f0f0] focus:border-[#404040] focus:outline-none"
          >
            {readyDocs.length === 0 && <option value="">No ready documents</option>}
            {readyDocs.map((doc) => (
              <option key={doc.id} value={doc.id}>
                {doc.title}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowAddModal(true)}
            disabled={!activeDocId}
            className="border border-[#262626] text-xs text-[#d0d0d0] hover:bg-[#1f1f1f] flex-1 sm:flex-initial"
          >
            Add Question
          </Button>
          <Button
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={!activeDocId || generateMutation.isPending}
            className="border border-[#383838] bg-[#1a1a1a] text-xs text-[#f0f0f0] hover:bg-[#262626] flex-1 sm:flex-initial"
          >
            {generateMutation.isPending ? "Generating..." : "Generate Quiz"}
          </Button>
        </div>
      </div>

      {generateMutation.error && (
        <UserErrorNotice
          error={generateMutation.error}
          onRetry={() => generateMutation.mutate()}
        />
      )}

      {/* Content Area */}
      {readyDocs.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-12 text-center">
          <h3 className="text-base font-medium text-[#f0f0f0]">No documents ready</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Upload and index a document first to practice with quizzes.
          </p>
          {onOpenDocuments && (
            <Button size="sm" onClick={onOpenDocuments} className="mt-4 text-xs">
              Open Documents
            </Button>
          )}
        </div>
      ) : quizQuery.isLoading ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-16 text-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#555555] border-t-[#ffffff] mb-3" />
          <p className="text-xs text-[#888888]">Loading quiz questions...</p>
        </div>
      ) : questions.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-12 text-center">
          <h3 className="text-base font-medium text-[#f0f0f0]">No quiz yet for this document</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Generate multiple-choice questions grounded in the text, or add custom questions.
          </p>
          <div className="mt-5 flex gap-3">
            <Button
              size="sm"
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="text-xs"
            >
              Generate Quiz with AI
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAddModal(true)}
              className="border border-[#262626] text-xs text-[#d0d0d0]"
            >
              Create Manually
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex flex-col gap-4">
          {/* Score Header when submitted */}
          {submitted && scoreResult && (
            <div className="flex items-center justify-between rounded-lg border border-[#2d422a] bg-[#0e1710] p-4 text-xs">
              <div className="flex items-center gap-3">
                <Award className="h-6 w-6 text-[#6ee7a3]" />
                <div>
                  <h4 className="font-medium text-[#f0f0f0] text-sm">
                    Score: {scoreResult.score} / {scoreResult.total} (
                    {Math.round((scoreResult.score / scoreResult.total) * 100)}%)
                  </h4>
                  <p className="text-[#888888]">
                    {scoreResult.score === scoreResult.total
                      ? "Flawless! Excellent grasp of the material."
                      : "Review your answers and explanations below."}
                  </p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleRetake}
                className="border border-[#384e36] text-[#6ee7a3] hover:bg-[#152317] text-xs"
              >
                <RotateCcw className="mr-1.5 h-3.5 w-3.5" />
                Retake Quiz
              </Button>
            </div>
          )}

          {/* Question Stepper */}
          <div className="flex items-center justify-between text-xs text-[#888888] px-1">
            <span>
              Question <span className="text-[#f0f0f0] font-mono">{currentIndex + 1}</span> of{" "}
              <span className="font-mono">{questions.length}</span>
            </span>
            <span>
              Answered:{" "}
              <span className="text-[#f0f0f0] font-mono">
                {Object.keys(userAnswers).length}/{questions.length}
              </span>
            </span>
          </div>

          {/* Active Question Box */}
          {currentQuestion && (
            <div className="flex flex-col rounded-xl border border-[#262626] bg-[#0f0f0f] p-6 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <span className="rounded bg-[#1a1a1a] px-2 py-0.5 font-mono text-[11px] uppercase tracking-wider text-[#888888] border border-[#262626]">
                  {currentQuestion.difficulty || "medium"}
                </span>
                <span className="text-xs font-mono text-[#555555]">
                  Q{currentIndex + 1}
                </span>
              </div>

              <p className="text-base font-medium leading-relaxed text-[#f0f0f0] mb-6">
                {currentQuestion.question}
              </p>

              {/* Options List */}
              <div className="flex flex-col gap-2.5">
                {currentQuestion.options.map((opt: QuizQuestionOption, idx: number) => {
                  const selected = userAnswers[currentQuestion.id] === opt.id || userAnswers[currentQuestion.id] === opt.text;
                  const isCorrect =
                    opt.text.toLowerCase() === currentQuestion.correct_answer.toLowerCase() ||
                    opt.id.toLowerCase() === currentQuestion.correct_answer.toLowerCase();

                  let optClass =
                    "flex items-center gap-3 rounded-lg border p-3.5 text-xs text-left transition-all cursor-pointer";
                  if (submitted) {
                    if (isCorrect) {
                      optClass += " border-[#2b5936] bg-[#0d1e11] text-[#9ae6b4]";
                    } else if (selected && !isCorrect) {
                      optClass += " border-[#5c2a2a] bg-[#240e0e] text-[#fca5a5]";
                    } else {
                      optClass += " border-[#1f1f1f] bg-[#121212] text-[#777777] opacity-60";
                    }
                  } else if (selected) {
                    optClass += " border-[#4a4a4a] bg-[#1a1a1a] text-[#ffffff] ring-1 ring-[#555555]";
                  } else {
                    optClass += " border-[#222222] bg-[#121212] text-[#d0d0d0] hover:border-[#333333] hover:bg-[#171717]";
                  }

                  return (
                    <button
                      key={opt.id || idx}
                      type="button"
                      onClick={() => handleSelectOption(currentQuestion.id, opt.id)}
                      disabled={submitted}
                      className={optClass}
                    >
                      <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded border border-[#333333] font-mono text-[10px] text-[#888888]">
                        {opt.id || ["A", "B", "C", "D"][idx]}
                      </span>
                      <span className="flex-1">{opt.text}</span>
                      {submitted && isCorrect && (
                        <CheckCircle2 className="h-4 w-4 shrink-0 text-[#6ee7a3]" />
                      )}
                      {submitted && selected && !isCorrect && (
                        <XCircle className="h-4 w-4 shrink-0 text-[#f87171]" />
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Explanation (after submission) */}
              {submitted && currentQuestion.explanation && (
                <div className="mt-5 rounded-lg border border-[#262626] bg-[#141414] p-4 text-xs">
                  <span className="uppercase tracking-widest text-[#888888] font-mono text-[10px] block mb-1">
                    Explanation
                  </span>
                  <p className="text-[#d0d0d0] leading-relaxed">
                    {currentQuestion.explanation}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Stepper Navigation & Submit */}
          <div className="flex items-center justify-between px-2 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => currentIndex > 0 && setCurrentIndex((i) => i - 1)}
              disabled={currentIndex === 0}
              className="border border-[#222222] text-xs text-[#c0c0c0]"
            >
              <ChevronLeft className="mr-1 h-3.5 w-3.5" />
              Previous
            </Button>

            <div className="flex items-center gap-2">
              {!submitted && (
                <Button
                  size="sm"
                  onClick={() => setSubmitted(true)}
                  disabled={Object.keys(userAnswers).length === 0}
                  className="bg-[#242424] text-xs text-[#f0f0f0] hover:bg-[#303030] border border-[#3a3a3a]"
                >
                  Submit Quiz ({Object.keys(userAnswers).length}/{questions.length})
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() =>
                  currentIndex < questions.length - 1 && setCurrentIndex((i) => i + 1)
                }
                disabled={currentIndex >= questions.length - 1}
                className="border border-[#222222] text-xs text-[#c0c0c0]"
              >
                Next
                <ChevronRight className="ml-1 h-3.5 w-3.5" />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Manual Question Creation Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-xl border border-[#262626] bg-[#0f0f0f] p-6 shadow-2xl">
            <h3 className="text-base font-medium text-[#f0f0f0]">Create Quiz Question</h3>
            <p className="mt-1 text-xs text-[#888888]">
              Add a multiple-choice question to this document&apos;s quiz.
            </p>

            <div className="mt-4 flex flex-col gap-3">
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Question
                </label>
                <textarea
                  value={manualQuestion}
                  onChange={(e) => setManualQuestion(e.target.value)}
                  placeholder="Enter multiple-choice question..."
                  className="w-full rounded border border-[#262626] bg-[#141414] p-2.5 text-sm text-[#f0f0f0] focus:border-[#444444] focus:outline-none min-h-[60px]"
                />
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Options (Select the radio of the correct answer)
                </label>
                <div className="flex flex-col gap-2">
                  {manualOptions.map((opt, i) => (
                    <div key={i} className="flex items-center gap-2">
                      <input
                        type="radio"
                        name="correct_option"
                        checked={manualCorrectIndex === i}
                        onChange={() => setManualCorrectIndex(i)}
                        className="h-4 w-4 accent-[#ffffff]"
                      />
                      <input
                        type="text"
                        value={opt}
                        onChange={(e) => {
                          const updated = [...manualOptions];
                          updated[i] = e.target.value;
                          setManualOptions(updated);
                        }}
                        placeholder={`Option ${["A", "B", "C", "D"][i]}...`}
                        className="flex-1 rounded border border-[#262626] bg-[#141414] p-1.5 text-xs text-[#f0f0f0] focus:border-[#444444] focus:outline-none"
                      />
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Explanation
                </label>
                <input
                  type="text"
                  value={manualExplanation}
                  onChange={(e) => setManualExplanation(e.target.value)}
                  placeholder="Why is this answer correct?"
                  className="w-full rounded border border-[#262626] bg-[#141414] p-2 text-xs text-[#f0f0f0] focus:border-[#444444] focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Difficulty
                </label>
                <select
                  value={manualDifficulty}
                  onChange={(e) => setManualDifficulty(e.target.value)}
                  className="w-full rounded border border-[#262626] bg-[#141414] p-1.5 text-xs text-[#f0f0f0] focus:border-[#444444] focus:outline-none"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAddModal(false)}
                className="border border-[#262626] text-xs text-[#a0a0a0]"
              >
                Cancel
              </Button>
              <Button
                size="sm"
                onClick={() => addQuestionMutation.mutate()}
                disabled={
                  !manualQuestion.trim() ||
                  manualOptions.filter((o) => o.trim()).length < 2 ||
                  addQuestionMutation.isPending
                }
                className="text-xs"
              >
                {addQuestionMutation.isPending ? "Saving..." : "Save Question"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
