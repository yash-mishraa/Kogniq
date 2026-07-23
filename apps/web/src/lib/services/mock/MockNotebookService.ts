import type { INotebookService } from "../interfaces/INotebookService";
import type { Notebook } from "@/app/workspace/environments/notebook/NotebookTypes";

export const MOCK_NOTEBOOKS: Notebook[] = [
  {
    id: "transformer-research",
    title: "Transformer Architecture",
    history: [
      { timestamp: "2 days ago", description: "Created from Transformer Architecture" },
      { timestamp: "Yesterday", description: "Expanded after Semantic Search" },
      { timestamp: "Today", description: "Updated after Study Session" }
    ],
    entries: [
      {
        id: "entry-1",
        title: "Initial Understanding of Self-Attention",
        createdAt: "2 days ago",
        thoughts: [
          {
            id: "t1",
            type: "observation",
            content: "Unlike RNNs which read sequentially, Transformers look at the entire sequence at once. This means they process information spatially rather than temporally.",
            annotations: [
              { id: "a1", type: "marginalia", content: "Key paradigm shift" }
            ]
          },
          {
            id: "t2",
            type: "question",
            content: "If there's no sequential processing, how does the model know the order of the words? Without order, 'Dog bites man' and 'Man bites dog' look identical to the network.",
            annotations: [
              { id: "a2", type: "marginalia", content: "Needs clarification" }
            ]
          },
          {
            id: "t3",
            type: "reflection",
            content: "Ah, this is where Positional Encoding comes in. It injects a signature of the position into the embedding itself. Beautifully elegant.",
            references: [
              {
                id: "r1",
                sourceType: "concept",
                title: "Positional Encoding",
                path: ["Transformer Architecture", "Input Processing", "Positional Encoding"]
              }
            ]
          }
        ]
      },
      {
        id: "entry-2",
        title: "Multi-Head Attention",
        createdAt: "Today",
        thoughts: [
          {
            id: "t4",
            type: "connection",
            content: "Multi-head attention feels similar to having multiple kernels in a CNN. Each 'head' can learn to focus on a different type of relationship (e.g., grammatical vs semantic).",
            references: [
              {
                id: "r2",
                sourceType: "note",
                title: "CNN Kernels",
                path: ["Computer Vision", "Convolutional Neural Networks", "Kernels"]
              }
            ]
          },
          {
            id: "t5",
            type: "reminder",
            content: "Revisit the formula for scaled dot-product attention before the interview. Remember why dividing by sqrt(d_k) prevents vanishing gradients.",
            annotations: [
              { id: "a3", type: "marginalia", content: "Interview Prep" }
            ]
          }
        ]
      }
    ]
  },
  {
    id: "database-normalization",
    title: "Database Normalization",
    history: [
      { timestamp: "1 week ago", description: "Created from Database Systems Chapter 4" }
    ],
    entries: [
      {
        id: "entry-3",
        title: "Boyce-Codd Normal Form",
        createdAt: "1 week ago",
        thoughts: [
          {
            id: "t6",
            type: "observation",
            content: "BCNF is essentially a stronger version of 3NF. 'Every determinant must be a candidate key'.",
          }
        ]
      }
    ]
  }
];

export class MockNotebookService implements INotebookService {
  async getNotebooks(signal?: AbortSignal): Promise<Notebook[]> {
    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => {
        resolve(MOCK_NOTEBOOKS);
      }, 800);

      if (signal) {
        signal.addEventListener("abort", () => {
          clearTimeout(timeout);
          reject(new DOMException("Aborted", "AbortError"));
        });
      }
    });
  }
}
