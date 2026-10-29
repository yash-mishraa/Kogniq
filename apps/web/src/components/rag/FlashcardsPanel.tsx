"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Eye,
  Layers,
  Plus,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui";
import { FlashcardItemData, ragApi } from "@/lib/rag/api";
import { SectionHeading, UserErrorNotice } from "./shared";

interface FlashcardsPanelProps {
  initialDocumentId?: string;
  onOpenDocuments?: () => void;
}

export function FlashcardsPanel({ initialDocumentId, onOpenDocuments }: FlashcardsPanelProps) {
  const queryClient = useQueryClient();
  const [selectedDocId, setSelectedDocId] = useState<string>(initialDocumentId || "");
  const [currentIndex, setCurrentIndex] = useState(0);
  const [revealed, setRevealed] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [reviewedResponses, setReviewedResponses] = useState<Record<string, string>>({});
  const [manualQuestion, setManualQuestion] = useState("");
  const [manualAnswer, setManualAnswer] = useState("");
  const [manualDifficulty, setManualDifficulty] = useState("medium");

  const docsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: ragApi.documents,
  });

  const readyDocs = (docsQuery.data || []).filter((d) => d.status === "Ready");
  const activeDocId = selectedDocId || (readyDocs.length > 0 ? readyDocs[0].id : "");

  const flashcardsQuery = useQuery({
    queryKey: ["flashcards", activeDocId],
    queryFn: () => ragApi.getFlashcards(activeDocId),
    enabled: Boolean(activeDocId),
  });

  const generateMutation = useMutation({
    mutationFn: () => ragApi.generateFlashcards(activeDocId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["flashcards", activeDocId] });
      setCurrentIndex(0);
      setRevealed(false);
    },
  });

  const addCardMutation = useMutation({
    mutationFn: () =>
      ragApi.addFlashcard(activeDocId, {
        question: manualQuestion,
        answer: manualAnswer,
        difficulty: manualDifficulty,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["flashcards", activeDocId] });
      setManualQuestion("");
      setManualAnswer("");
      setShowAddModal(false);
    },
  });

  const cards = flashcardsQuery.data || [];
  const currentCard: FlashcardItemData | undefined = cards[currentIndex];

  const handleDifficulty = (rating: string) => {
    if (!currentCard) return;
    setReviewedResponses((prev) => ({ ...prev, [currentCard.id]: rating }));
    setRevealed(false);
    if (currentIndex < cards.length - 1) {
      setCurrentIndex((i) => i + 1);
    }
  };

  const handleReset = () => {
    setCurrentIndex(0);
    setRevealed(false);
    setReviewedResponses({});
  };

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 py-6 px-4">
      <SectionHeading
        eyebrow="Study"
        title="Flashcards"
        detail="Study key concepts extracted from your documents with spaced self-testing."
      />

      {/* Document Selector & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-4">
        <div className="flex items-center gap-3">
          <BookOpen className="h-5 w-5 text-[#888888]" />
          <span className="text-xs uppercase tracking-wider text-[#888888]">Source:</span>
          <select
            value={activeDocId}
            onChange={(e) => {
              setSelectedDocId(e.target.value);
              setCurrentIndex(0);
              setRevealed(false);
            }}
            className="rounded border border-[#262626] bg-[#141414] px-3 py-1.5 text-sm text-[#f0f0f0] focus:border-[#404040] focus:outline-none"
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
            className="border border-[#262626] text-xs text-[#d0d0d0] hover:bg-[#1f1f1f]"
          >
            <Plus className="mr-1.5 h-3.5 w-3.5" />
            Add Card
          </Button>
          <Button
            size="sm"
            onClick={() => generateMutation.mutate()}
            disabled={!activeDocId || generateMutation.isPending}
            className="border border-[#383838] bg-[#1a1a1a] text-xs text-[#f0f0f0] hover:bg-[#262626]"
          >
            <Sparkles className="mr-1.5 h-3.5 w-3.5 text-[#a0a0a0]" />
            {generateMutation.isPending ? "Generating..." : "Generate Deck"}
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
          <Layers className="h-10 w-10 text-[#555555] mb-3" />
          <h3 className="text-base font-medium text-[#f0f0f0]">No documents ready</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Upload and index a document first to practice with flashcards.
          </p>
          {onOpenDocuments && (
            <Button size="sm" onClick={onOpenDocuments} className="mt-4 text-xs">
              Open Documents
            </Button>
          )}
        </div>
      ) : flashcardsQuery.isLoading ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-16 text-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#555555] border-t-[#ffffff] mb-3" />
          <p className="text-xs text-[#888888]">Loading flashcards...</p>
        </div>
      ) : cards.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-12 text-center">
          <Layers className="h-10 w-10 text-[#555555] mb-3" />
          <h3 className="text-base font-medium text-[#f0f0f0]">No flashcards yet for this document</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Generate flashcards using local or cloud AI, or create custom cards manually.
          </p>
          <div className="mt-5 flex gap-3">
            <Button
              size="sm"
              onClick={() => generateMutation.mutate()}
              disabled={generateMutation.isPending}
              className="text-xs"
            >
              <Sparkles className="mr-1.5 h-3.5 w-3.5" />
              Generate Flashcards
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowAddModal(true)}
              className="border border-[#262626] text-xs text-[#d0d0d0]"
            >
              <Plus className="mr-1.5 h-3.5 w-3.5" />
              Create Manually
            </Button>
          </div>
        </div>
      ) : (
        /* Interactive Flashcard Study Deck */
        <div className="flex flex-col gap-4">
          {/* Deck Status Bar */}
          <div className="flex items-center justify-between text-xs text-[#888888] px-1">
            <span>
              Card <span className="text-[#f0f0f0] font-mono">{currentIndex + 1}</span> of{" "}
              <span className="font-mono">{cards.length}</span>
            </span>
            <div className="flex items-center gap-3">
              <span>
                Reviewed:{" "}
                <span className="text-[#f0f0f0] font-mono">
                  {Object.keys(reviewedResponses).length}/{cards.length}
                </span>
              </span>
              <button
                onClick={handleReset}
                className="flex items-center gap-1 hover:text-[#f0f0f0] transition-colors"
                title="Restart review"
              >
                <RotateCcw className="h-3 w-3" />
                Reset
              </button>
            </div>
          </div>

          {/* Card Presentation */}
          {currentCard && (
            <div className="relative flex min-h-[300px] flex-col justify-between rounded-xl border border-[#262626] bg-[#0f0f0f] p-8 shadow-2xl transition-all">
              <div className="flex items-start justify-between">
                <span className="rounded bg-[#1a1a1a] px-2 py-0.5 font-mono text-[11px] uppercase tracking-wider text-[#888888] border border-[#262626]">
                  {currentCard.difficulty || "medium"}
                </span>
                <span className="text-xs font-mono text-[#555555]">
                  {currentIndex + 1} / {cards.length}
                </span>
              </div>

              {/* Question */}
              <div className="my-6">
                <span className="text-xs uppercase tracking-widest text-[#707070]">Question</span>
                <p className="mt-2 text-lg font-medium leading-relaxed text-[#f5f5f5]">
                  {currentCard.question}
                </p>
              </div>

              {/* Answer Section */}
              {revealed ? (
                <div className="mt-4 rounded-lg border border-[#222222] bg-[#141414] p-5">
                  <span className="text-xs uppercase tracking-widest text-[#888888]">Answer</span>
                  <p className="mt-2 text-sm leading-relaxed text-[#e0e0e0] font-sans">
                    {currentCard.answer}
                  </p>
                </div>
              ) : (
                <div className="flex justify-center my-4">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setRevealed(true)}
                    className="border border-[#2e2e2e] bg-[#141414] text-xs text-[#e0e0e0] hover:bg-[#1c1c1c]"
                  >
                    <Eye className="mr-1.5 h-3.5 w-3.5 text-[#888888]" />
                    Reveal Answer
                  </Button>
                </div>
              )}

              {/* Rating Controls (visible when answer is revealed) */}
              {revealed ? (
                <div className="mt-6 flex flex-wrap items-center justify-between border-t border-[#1f1f1f] pt-4 gap-2">
                  <span className="text-xs text-[#777777]">How well did you know this?</span>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDifficulty("hard")}
                      className="rounded border border-[#3a1d1d] bg-[#1a0e0e] px-3 py-1.5 text-xs text-[#e87070] hover:bg-[#2b1414] transition-colors"
                    >
                      Hard / Missed
                    </button>
                    <button
                      onClick={() => handleDifficulty("medium")}
                      className="rounded border border-[#36321d] bg-[#17150c] px-3 py-1.5 text-xs text-[#e2b865] hover:bg-[#292412] transition-colors"
                    >
                      Good
                    </button>
                    <button
                      onClick={() => handleDifficulty("easy")}
                      className="rounded border border-[#1d3322] bg-[#0c170f] px-3 py-1.5 text-xs text-[#6ee7a3] hover:bg-[#142618] transition-colors"
                    >
                      Easy
                    </button>
                  </div>
                </div>
              ) : (
                <div className="mt-6 flex items-center justify-between border-t border-[#1f1f1f] pt-4 text-xs text-[#555555]">
                  <span>Click reveal when you are ready to check your answer.</span>
                </div>
              )}
            </div>
          )}

          {/* Navigation Controls */}
          <div className="flex items-center justify-between px-2 pt-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (currentIndex > 0) {
                  setCurrentIndex((i) => i - 1);
                  setRevealed(false);
                }
              }}
              disabled={currentIndex === 0}
              className="border border-[#222222] text-xs text-[#c0c0c0]"
            >
              <ChevronLeft className="mr-1 h-3.5 w-3.5" />
              Previous
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                if (currentIndex < cards.length - 1) {
                  setCurrentIndex((i) => i + 1);
                  setRevealed(false);
                }
              }}
              disabled={currentIndex >= cards.length - 1}
              className="border border-[#222222] text-xs text-[#c0c0c0]"
            >
              Next
              <ChevronRight className="ml-1 h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      )}

      {/* Manual Card Creation Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-lg rounded-xl border border-[#262626] bg-[#0f0f0f] p-6 shadow-2xl">
            <h3 className="text-base font-medium text-[#f0f0f0]">Create Flashcard</h3>
            <p className="mt-1 text-xs text-[#888888]">
              Add a custom card to this document&apos;s deck.
            </p>

            <div className="mt-4 flex flex-col gap-4">
              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Question
                </label>
                <textarea
                  value={manualQuestion}
                  onChange={(e) => setManualQuestion(e.target.value)}
                  placeholder="Enter the question or concept..."
                  className="w-full rounded border border-[#262626] bg-[#141414] p-2.5 text-sm text-[#f0f0f0] focus:border-[#444444] focus:outline-none min-h-[70px]"
                />
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Answer
                </label>
                <textarea
                  value={manualAnswer}
                  onChange={(e) => setManualAnswer(e.target.value)}
                  placeholder="Enter the correct answer or explanation..."
                  className="w-full rounded border border-[#262626] bg-[#141414] p-2.5 text-sm text-[#f0f0f0] focus:border-[#444444] focus:outline-none min-h-[90px]"
                />
              </div>

              <div>
                <label className="block text-xs uppercase tracking-wider text-[#777777] mb-1">
                  Difficulty
                </label>
                <select
                  value={manualDifficulty}
                  onChange={(e) => setManualDifficulty(e.target.value)}
                  className="w-full rounded border border-[#262626] bg-[#141414] p-2 text-sm text-[#f0f0f0] focus:border-[#444444] focus:outline-none"
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
                onClick={() => addCardMutation.mutate()}
                disabled={!manualQuestion.trim() || !manualAnswer.trim() || addCardMutation.isPending}
                className="text-xs"
              >
                {addCardMutation.isPending ? "Saving..." : "Save Flashcard"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
