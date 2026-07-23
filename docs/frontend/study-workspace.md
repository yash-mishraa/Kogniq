# Study Workspace Foundation

The Study Workspace provides a unified set of continuous learning perspectives over existing knowledge. It actively resists the concept of a "dashboard" filled with disconnected AI features. 

## Learning Philosophy

We view learning as a progression of understanding. 
Instead of exposing separate tools (Summarizer, Flashcard Generator, Quiz Maker), the workspace exposes Learning Modes:
- **Understand**: Gaining the intuition.
- **Review**: Consolidating knowledge into notes.
- **Recall**: Practicing active retrieval.
- **Test**: Checking deep understanding.

*(Note: The architecture includes a stub for a future "Reflection" stage between Understand and Review).*

## Typography and Continuity

The Study Workspace uses typography as its primary visual language. There are no grids of cards, tab bars, or wizards.
- **Timeline**: A subtle text-based progression indicator rather than a navigation menu.
- **Context Panel**: Subtly preserves orientation (Source, Concept, Related Concepts).
- **Motion**: Changing learning modes reorganizes content smoothly using layout animations, reinforcing that these are different perspectives on the same underlying concept.

## Anti-Patterns

- **No Flip Cards**: The Recall mode avoids traditional Anki-style flip interactions. Instead, it presents a calm prompt that expands downwards to reveal the explanation.
- **No Forms**: The Test mode avoids standard form elements (radio buttons/checkboxes). It reads like an unfolding conversation.
- **No Dashboards**: There is no starting grid. You enter study context from the Locus.

## Locus Integration

In the Study environment, the Locus is geared entirely toward resuming context rather than generating new queries. The placeholder reads `│ Continue learning...` and offers suggestions of recent study sessions.
