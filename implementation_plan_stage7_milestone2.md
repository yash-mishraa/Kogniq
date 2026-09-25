# Kogniq — Stage 7 Milestone 2
# Product Scope Discovery, Architecture Planning & Milestone Proposal

## 1. Executive Summary
The Stage 7 Milestone 2 integration was previously blocked because the repository's `.ai` documents defined Stage 7 broadly as "Agentic Workflows" without actionable, step-by-step milestone definitions. Following a comprehensive codebase discovery, it is clear Kogniq possesses robust deterministic tools (Semantic Search, Material Generation, Knowledge Tracking) but lacks an orchestrator to dynamically link these tools through natural language. 

I propose defining **Stage 7 Milestone 2 as the Interactive Agentic Tutor Foundation**. This scope safely introduces a strictly bounded, tool-using ReAct (Reason + Act) agent into the existing `Study` workspace, allowing learners to ask follow-up questions and receive explanations securely grounded in their authorized documents.

## 2. Repository Evidence
- **Roadmap (`.ai/roadmap.md`):** Defines Stage 7 as "Add bounded agents where tool use materially improves learning or operations."
- **Current Limitations:** The existing `ExplainMistakeUseCase` (in `apps/api/src/apps/api/app/routers/learning.py`) provides single-turn, deterministic AI help. It cannot handle interactive follow-ups.
- **Existing Strengths:** `RetrieveUseCase` (`routers/retrieval.py`) provides tested, authorized semantic search over processed document chunks.
- **Domain Readiness:** `AbstractTextGenerationProvider` currently specifies `supports_tools: bool` metadata, but the interface requires extending to natively support `messages` and `tools` payloads.

## 3. Existing Capability Inventory

| Capability | Actual implementation | Relevant files | Maturity | Can an agent use it? |
|---|---|---|---|---|
| Semantic Search | Implemented & Tested | `routers/retrieval.py` | Fully implemented | Yes, as a retrieval tool |
| Quiz Generation | Implemented & Tested | `routers/learning.py` | Fully implemented | Yes, but too complex for M2 |
| Explain Mistake | Implemented & Tested | `explain_mistake.py` | Fully implemented | Replaced/augmented by Tutor |
| Flashcard Review | Implemented & Tested | `StudyEnvironment` | UI + Backend | No (Requires user action) |
| Knowledge State | Implemented | `knowledge_states` | Fully implemented | Yes, for context |
| LLM Generation | Implemented | `AbstractTextGenerationProvider`| Fully implemented | Requires signature update |

## 4. Stage 7 Direction
"Agentic Workflows" dictates a shift from one-shot AI generation to an iterative LLM loop. An agent evaluates a user's intent, decides which tool to call, waits for the application to execute the tool deterministically, and synthesizes the result. What remains undefined is the foundational architecture to support this multi-turn tool-calling loop securely.

## 5. Candidate Milestone Directions

| Proposal | Core purpose | Existing capabilities reused | New infrastructure required | Complexity | Main risks |
|---|---|---|---|---|---|
| **A. Autonomous Synthesizer** | Auto-generates all study materials in background | `GenerateLearningUseCase`, `jobs` | Async workflow persistence | Medium-High | High token cost, unpredictable UX |
| **B. Agentic Study Tutor** | Interactive chat for grounded Q&A and follow-ups | `RetrieveUseCase`, LLM Provider | Tool abstraction, Chat UI | Medium | Prompt injection, hallucination |
| **C. Deterministic Orchestrator** | Backend-only state machine for multi-step jobs | `UnitOfWork` | Workflow schema | Low | No immediate user value |

*Trade-offs:* Option B provides immediate, high-visibility learner value (solving the rigidness of the current one-shot "Explain my mistake" UI) while directly leveraging the already-built vector search capabilities.

## 6. Proposed Stage 7 Milestone 2
**Proposed milestone name:** Interactive Agentic Tutor Foundation
**Problem statement:** Learners currently receive one-shot AI help but cannot ask follow-up questions or explore concepts interactively. A bounded, tool-using agent is needed to facilitate grounded, multi-turn educational dialogues.
**User-facing behavior:**
Inside the `Study` workspace, the user opens an "AI Tutor" side-panel. They ask, "Why is the inner membrane folded?" The AI Tutor autonomously searches the current document using semantic search, reads the extracted chunks, and replies with a grounded explanation.
**Core workflow:**
1. User submits a message.
2. Backend `AgentOrchestratorUseCase` processes the message and conversation history.
3. Orchestrator prompts the LLM provider, exposing the `semantic_search` tool.
4. LLM outputs a `semantic_search` tool call.
5. Orchestrator executes `RetrieveUseCase` deterministically.
6. Orchestrator returns chunk text to the LLM.
7. LLM generates the final response.
**Inputs:** User message, Active Document ID, Chat History array.
**Outputs:** Agent response string, Array of tool-call execution traces (e.g., "Searched document...").
**Existing components reused:** `RetrieveUseCase`, `AuthenticationService`, `AbstractTextGenerationProvider`.
**New components required:**
- *Domain:* `AgentMessage`, `ToolCall`, `ToolDefinition` contracts.
- *Application:* `AgentOrchestratorUseCase`, `SemanticSearchTool` wrapper.
- *API:* `POST /api/v1/agent/tutor/chat`.
- *Frontend:* `TutorChatPanel.tsx` component inside `StudyEnvironment`.
**Explicit non-goals:** Autonomous quiz generation, multi-agent systems, persistent cross-device chat histories.

## 7. Architecture Proposal
- **Domain:** Extend `AbstractTextGenerationProvider` to include a `generate_with_tools()` interface.
- **Application:** Implement an orchestrator that runs a strict `while` loop (max 3 iterations) to resolve tool calls before returning the final string.
- **API:** Stateless endpoint that accepts the full conversation history from the frontend.
- **Frontend:** React hook managing ephemeral chat state and rendering assistant vs. user bubbles.

## 8. Agent and Tool Boundaries
**Agent responsibilities:** Deciding whether to search the document, formulating the search query, synthesizing the final answer.
**Deterministic application responsibilities:** Enforcing the `document_id` authorization filter, executing the vector search natively, and enforcing the iteration loop limit.
**Available tools:**
- *Name:* `semantic_search`
- *Input schema:* `query: str`
- *Output schema:* Array of text chunks.
- *Auth checks:* The Agent *cannot* specify the `document_id`. The Orchestrator hardcodes the `document_id` derived securely from the authenticated endpoint context.

## 9. Security and Privacy Plan
- **Existing controls:** The system requires valid session tokens to reach the endpoint.
- **Required controls:** The API must explicitly validate that the user owns the `document_id` *before* initiating the agent loop. The agent must never be able to alter the document ID it queries.
- **Prompt injection:** The system prompt must firmly instruct the model to refuse instructions hidden within retrieved chunks.
- **Cost controls:** Hardcoded max 3 tool-call iterations per request. Enforced `max_tokens`.

## 10. AI Integration Strategy
- **Deterministic functionality:** Context authorization, tool execution routing, loop termination.
- **AI-dependent functionality:** Query formulation, ReAct reasoning, answer synthesis.
- **Mock functionality:** A `MockAgentProvider` that returns a hardcoded sequence (Tool Call -> Final Answer) for rapid frontend testing.
- **Production requirements:** The LLM provider (e.g., Gemini) SDK must be mapped to the generic `ToolDefinition` schema in the infrastructure layer.

## 11. Data and Workflow State Proposal
Persistent workflow state is **unnecessary** for this milestone. By designing the API to accept the full `messages` array from the frontend (standard practice for Chat UIs), we completely eliminate the need for a complex database schema, migrations, or WebSocket sync issues. The frontend local state acts as the ephemeral session store. This radically reduces architectural risk while meeting the milestone goal.

## 12. Testing and Acceptance Plan
- **Domain:** Validate the ReAct loop max-iteration cutoff to prevent infinite loops.
- **Application:** Verify `AgentOrchestratorUseCase` routes the `semantic_search` call correctly and injects the hardcoded `document_id`.
- **API:** Verify a 403 Forbidden is returned if the user queries a document they don't own.
- **Frontend:** Test rendering of user messages, loading states ("Tutor is thinking..."), and tool execution indicators ("Searching document...").
- **Integration:** Test the mock provider to ensure the frontend can complete a multi-turn tool cycle without an actual LLM key.

## 13. Implementation Phases
1. **Domain & Infrastructure:** Update `AbstractTextGenerationProvider` with tool-calling signatures.
2. **Application:** Build `AgentOrchestratorUseCase` and the `SemanticSearchTool` wrapper.
3. **API:** Expose `POST /api/v1/agent/tutor/chat`.
4. **Frontend:** Build `TutorChatPanel.tsx` in `StudyEnvironment`.
5. **Testing & Verification:** Run full validation suites.

## 14. Risks and Limitations
- **Architectural risks:** Abstracting tool calls across different LLM providers can be brittle depending on the provider SDKs.
- **Product decisions required:** Confirm whether stateless frontend conversation history is acceptable for M2.
- **Deferred improvements:** Persisting chat history for cross-device resume.

## 15. Final Recommendation
The proposed scope is narrowly bounded, leverages existing vector search, and delivers immediate, interactive learner value. 

**Decisions requiring explicit approval:**
1. Approval of the **stateless conversation design** (ephemeral frontend state).
2. Approval of limiting the agent strictly to the **semantic_search tool**.

Please provide explicit approval of this plan so we may begin implementation of Stage 7 Milestone 2.
