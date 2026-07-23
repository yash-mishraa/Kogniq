# Search Workspace Foundation

The Search Workspace in Kogniq provides a unified, semantic retrieval layer that enables users to find concepts and understanding, rather than just matching file names.

## Retrieval Philosophy

Kogniq views search as another perspective on your knowledge. The interface actively works against feeling like a traditional search engine:
- We prefer terms like "Findings" or "Semantic Matches" over "Search Results".
- Retrievals are framed around understanding. 
- There are no visible technical scores or vector similarity thresholds presented to the user.

## Evidence Design

Evidence is the primary visual element of a finding. We display the context block (`SearchEvidence`) in a calm, editorial typography format that instantly communicates *why* a document matched the query. The user should not have to guess. 

## Interaction Lifecycle

1. **Empty State:** The user is greeted with a generic `Locus` configured for free-text submission (`mode="free-text"`).
2. **Thinking State:** To build anticipation and reinforce the semantic nature of the search, the environment cycles through gentle typographic states ("Searching your knowledge...", "Connecting related concepts...", "Found relevant passages.") instead of showing a generic loading spinner.
3. **Findings State:** The matched knowledge is displayed as an elegant list.

## Search States

- `idle`: Awaiting user input.
- `connecting`: Simulating the heavy semantic retrieval phase.
- `found`: The findings are displayed.
- `empty`: No matches.

## Motion Principles

When a finding is selected, it does not navigate away to a new page. Instead, it smoothly expands using `framer-motion` layout animations. The `SearchInspector` slides open, retaining full search context (filters, query, other findings) in a subdued state. This maintains spatial continuity.
