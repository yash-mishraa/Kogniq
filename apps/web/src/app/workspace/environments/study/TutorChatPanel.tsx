"use client";

import React, { useState, useRef, useEffect } from "react";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface TutorChatPanelProps {
  documentId?: string;
  onClose?: () => void;
}

function TutorQuizProposal({ proposal, documentId }: { proposal: any, documentId: string }) {
  const [status, setStatus] = useState<"pending" | "submitting" | "success" | "error" | "dismissed">("pending");

  if (status === "dismissed") return null;

  const handleAccept = async () => {
    setStatus("submitting");
    try {
      const token = localStorage.getItem("token") || "demo-user-1";
      const res = await fetch(`/api/v1/learning/${documentId}/quizzes`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          question: proposal.question,
          options: proposal.options,
          correct_answer: proposal.correct_answer,
          explanation: proposal.explanation,
          difficulty: proposal.difficulty,
          idempotency_key: proposal.idempotency_key
        })
      });
      if (res.ok) {
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch (e) {
      setStatus("error");
    }
  };

  return (
    <div className="flex justify-start mb-4">
      <div className="w-full max-w-[90%] p-4 rounded-lg bg-indigo-50 border border-indigo-200 shadow-sm text-sm">
        <h4 className="font-semibold text-indigo-800 mb-2 flex items-center">
          <span className="mr-2">📝</span> AI Suggested Quiz Question
        </h4>
        <div className="mb-2 font-medium">{proposal.question}</div>
        <ul className="mb-2 space-y-1 list-disc pl-4 text-gray-700">
          {proposal.options.map((opt: string, idx: number) => (
            <li key={idx}>
              {opt} {opt === proposal.correct_answer && <span className="text-green-600 ml-2">✓</span>}
            </li>
          ))}
        </ul>
        <div className="mb-2 text-gray-700 italic border-l-2 border-indigo-300 pl-2"><strong>Explanation:</strong> {proposal.explanation}</div>
        <div className="mb-3 text-xs text-gray-500 uppercase font-semibold tracking-wider">Difficulty: {proposal.difficulty}</div>
        
        {status === "pending" && (
          <div className="flex space-x-2">
            <button onClick={handleAccept} className="px-3 py-1 bg-indigo-600 text-white rounded hover:bg-indigo-700 font-medium">Add to Quiz</button>
            <button onClick={() => setStatus("dismissed")} className="px-3 py-1 bg-transparent text-gray-600 hover:text-gray-800">Dismiss</button>
          </div>
        )}
        {status === "submitting" && <div className="text-gray-500 italic">Adding...</div>}
        {status === "success" && <div className="text-green-600 font-semibold flex items-center"><span className="mr-1">✓</span> Added to Quiz</div>}
        {status === "error" && <div className="text-red-600 font-semibold">Failed to add question.</div>}
      </div>
    </div>
  );
}

function TutorNoteProposal({ proposal, documentId }: { proposal: any, documentId: string }) {
  const [status, setStatus] = useState<"pending" | "submitting" | "success" | "error" | "dismissed">("pending");

  if (status === "dismissed") return null;

  const handleAccept = async () => {
    setStatus("submitting");
    try {
      const token = localStorage.getItem("token") || "demo-user-1";
      const res = await fetch(`/api/v1/notebooks/${documentId}/entries`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          title: proposal.title,
          content: proposal.content,
          idempotency_key: proposal.idempotency_key
        })
      });
      if (res.ok) {
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch (e) {
      setStatus("error");
    }
  };

  return (
    <div className="flex justify-start mb-4">
      <div className="w-full max-w-[90%] p-4 rounded-lg bg-blue-50 border border-blue-200 shadow-sm text-sm">
        <h4 className="font-semibold text-blue-800 mb-2 flex items-center">
          <span className="mr-2">📝</span> AI Suggested Note
        </h4>
        <div className="mb-2"><strong>Title:</strong> {proposal.title}</div>
        <div className="mb-4 text-gray-700 whitespace-pre-wrap">{proposal.content}</div>
        
        {status === "pending" && (
          <div className="flex space-x-2">
            <button onClick={handleAccept} className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 font-medium">Save Note</button>
            <button onClick={() => setStatus("dismissed")} className="px-3 py-1 bg-transparent text-gray-600 hover:text-gray-800">Dismiss</button>
          </div>
        )}
        {status === "submitting" && <div className="text-gray-500 italic">Saving...</div>}
        {status === "success" && <div className="text-green-600 font-semibold flex items-center"><span className="mr-1">✓</span> Saved to Notebook</div>}
        {status === "error" && <div className="text-red-600 font-semibold">Failed to save note.</div>}
      </div>
    </div>
  );
}

function TutorFlashcardProposal({ proposal, documentId }: { proposal: any, documentId: string }) {
  const [status, setStatus] = useState<"pending" | "submitting" | "success" | "error" | "dismissed">("pending");

  if (status === "dismissed") return null;

  const handleAccept = async () => {
    setStatus("submitting");
    try {
      const token = localStorage.getItem("token") || "demo-user-1";
      const res = await fetch(`/api/v1/learning/${documentId}/flashcards`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          question: proposal.question,
          answer: proposal.answer,
          difficulty: proposal.difficulty,
          idempotency_key: proposal.idempotency_key
        })
      });
      if (res.ok) {
        setStatus("success");
      } else {
        setStatus("error");
      }
    } catch (e) {
      setStatus("error");
    }
  };

  return (
    <div className="flex justify-start mb-4">
      <div className="w-full max-w-[90%] p-4 rounded-lg bg-yellow-50 border border-yellow-200 shadow-sm text-sm">
        <h4 className="font-semibold text-yellow-800 mb-2 flex items-center">
          <span className="mr-2">💡</span> AI Suggested Flashcard
        </h4>
        <div className="mb-2"><strong>Q:</strong> {proposal.question}</div>
        <div className="mb-2 text-gray-700"><strong>A:</strong> {proposal.answer}</div>
        <div className="mb-3 text-xs text-gray-500 uppercase font-semibold tracking-wider">Difficulty: {proposal.difficulty}</div>
        
        {status === "pending" && (
          <div className="flex space-x-2">
            <button onClick={handleAccept} className="px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 font-medium">Add to Deck</button>
            <button onClick={() => setStatus("dismissed")} className="px-3 py-1 bg-transparent text-gray-600 hover:text-gray-800">Dismiss</button>
          </div>
        )}
        {status === "submitting" && <div className="text-gray-500 italic">Adding...</div>}
        {status === "success" && <div className="text-green-600 font-semibold flex items-center"><span className="mr-1">✓</span> Added to Flashcards</div>}
        {status === "error" && <div className="text-red-600 font-semibold">Failed to add flashcard.</div>}
      </div>
    </div>
  );
}

export function TutorChatPanel({ documentId, onClose }: TutorChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return sessionStorage.getItem("activeTutorSessionId");
    }
    return null;
  });
  const [isLoading, setIsLoading] = useState(false);
  const [toolEvents, setToolEvents] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, toolEvents, isLoading]);

  useEffect(() => {
    if (typeof window !== "undefined") {
      if (sessionId) {
        sessionStorage.setItem("activeTutorSessionId", sessionId);
      } else {
        sessionStorage.removeItem("activeTutorSessionId");
      }
    }
  }, [sessionId]);

  useEffect(() => {
    if (!sessionId) return;
    const fetchHistory = async () => {
      try {
        const token = localStorage.getItem("token") || "demo-user-1";
        const response = await fetch(`/api/v1/agent/tutor/sessions/${sessionId}/messages`, {
          headers: { "Authorization": `Bearer ${token}` }
        });
        if (response.ok) {
          const data = await response.json();
          setMessages(data.map((m: any) => ({ role: m.role, content: m.content })));
        } else {
          setSessionId(null);
        }
      } catch (err) {
        console.error("Failed to fetch history:", err);
      }
    };
    fetchHistory();
  }, [sessionId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const newMessages = [...messages, { role: "user", content: inputValue } as ChatMessage];
    setMessages(newMessages);
    setInputValue("");
    setIsLoading(true);
    setError(null);
    setToolEvents([]);

    try {
      const token = localStorage.getItem("token") || "demo-user-1";
      const response = await fetch("/api/v1/agent/tutor/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          document_id: documentId || null,
          messages: [{ role: "user", content: inputValue }],
          session_id: sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }

      const data = await response.json();
      
      setMessages(prev => [...prev, { role: "assistant", content: data.content }]);
      if (data.session_id) setSessionId(data.session_id);
      if (data.tool_events && data.tool_events.length > 0) {
        setToolEvents(data.tool_events);
      }
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white border-l border-gray-200">
      <div className="flex justify-between items-center p-4 border-b border-gray-200 bg-gray-50">
        <h3 className="font-semibold text-gray-800">AI Tutor</h3>
        <div className="flex space-x-2">
          <button onClick={() => { setMessages([]); setSessionId(null); setToolEvents([]); setError(null); }} className="text-xs text-blue-600 hover:text-blue-800 bg-blue-50 px-2 py-1 rounded">
            New Chat
          </button>
          {onClose && (
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              ✖
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 p-4 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 mt-10">
            Ask me anything about the current document!
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`mb-4 flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[80%] p-3 rounded-lg ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-none"
                    : "bg-gray-100 text-gray-800 rounded-bl-none"
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))
        )}

        {toolEvents.map((event, idx) => {
          try {
            const parsed = JSON.parse(event);
            if (parsed.type === "flashcard_proposal") {
              return <TutorFlashcardProposal key={`event-${idx}`} proposal={parsed} documentId={documentId as string} />;
            }
            if (parsed.type === "note_proposal") {
              return <TutorNoteProposal key={`event-${idx}`} proposal={parsed} documentId={documentId as string} />;
            }
            if (parsed.type === "quiz_proposal") {
              return <TutorQuizProposal key={`event-${idx}`} proposal={parsed} documentId={documentId as string} />;
            }
          } catch(e) {
            // ignore
          }
          return (
            <div key={`event-${idx}`} className="flex justify-start mb-2">
              <div className="text-xs text-gray-400 italic flex items-center">
                <span className="mr-1">⚙️</span> {event}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex justify-start mb-4">
            <div className="text-sm text-gray-500 italic">Tutor is thinking...</div>
          </div>
        )}

        {error && (
          <div className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-lg border border-red-200">
            {error}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200 bg-white">
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            placeholder="Ask a question..."
            className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-500"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-blue-300 transition-colors"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

