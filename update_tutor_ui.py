import sys

proposal_code = """
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

"""

content = open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'r', encoding='utf-8').read()
content = content.replace("function TutorFlashcardProposal", proposal_code + "function TutorFlashcardProposal")

# Also need to parse the tool events for note_proposal
replacement_tool_event_code = """
      {toolEvents.map((event, idx) => {
        try {
          const parsed = JSON.parse(event);
          if (parsed.type === "flashcard_proposal") {
            return <TutorFlashcardProposal key={`event-${idx}`} proposal={parsed} documentId={documentId} />;
          }
          if (parsed.type === "note_proposal") {
            return <TutorNoteProposal key={`event-${idx}`} proposal={parsed} documentId={documentId} />;
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
"""

content = content.replace("""
        {toolEvents.map((event, idx) => (
          <div key={`event-${idx}`} className="flex justify-start mb-2">
            <div className="text-xs text-gray-400 italic flex items-center">
              <span className="mr-1">⚙️</span> {event}
            </div>
          </div>
        ))}
""".strip(), replacement_tool_event_code.strip())

open('apps/web/src/app/workspace/environments/study/TutorChatPanel.tsx', 'w', encoding='utf-8').write(content)
