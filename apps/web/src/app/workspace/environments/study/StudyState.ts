import type { StudyState, StudyAction, StudyMaterial } from "./StudyTypes";
import { abortResourceHydration, startResourceHydration } from "@/lib/core/ResourceState";

export const MOCK_STUDY_MATERIAL: StudyMaterial = {
  concept: {
    id: "transformer-architecture",
    title: "Transformer Architecture",
    sourceDocument: "Attention Is All You Need",
    relatedConcepts: ["Self-Attention", "Multi-Head Attention", "Positional Encoding"],
  },
  understand: {
    intuition: "Before Transformers, sequence models like RNNs read text one word at a time from left to right. Transformers look at the entire sentence at once, calculating how much 'attention' each word should pay to every other word to understand the full context.",
    whyItMatters: "This parallel processing unlocked massive scale. Instead of waiting for the previous word to be processed, we can train on entire documents simultaneously using modern GPUs. This architecture is the foundation for all modern LLMs (GPT, Claude, Gemini).",
    keyTakeaways: [
      "Dispenses entirely with recurrence and convolutions.",
      "Relies solely on attention mechanisms to draw global dependencies.",
      "Allows for significantly more parallelization during training."
    ]
  },
  review: {
    notes: [
      {
        section: "Core Mechanism",
        points: [
          "Replaces sequential processing with parallel attention.",
          "Uses Query (Q), Key (K), and Value (V) matrices to compute attention weights.",
          "Attention(Q, K, V) = softmax((Q * K^T) / sqrt(d_k)) * V"
        ]
      },
      {
        section: "Multi-Head Attention",
        points: [
          "Runs multiple attention mechanisms in parallel.",
          "Allows the model to jointly attend to information from different representation subspaces at different positions."
        ]
      },
      {
        section: "Positional Encoding",
        points: [
          "Since there's no recurrence, the model doesn't inherently know word order.",
          "Injects position information into input embeddings using sine and cosine functions of different frequencies."
        ]
      }
    ]
  },
  recall: [
    {
      prompt: "Why do Transformers need Positional Encoding when RNNs do not?",
      explanation: "RNNs process tokens sequentially, so word order is inherently captured by the time steps. Transformers process all tokens in parallel simultaneously. Without positional encoding, a Transformer would treat the sentence 'Dog bites man' exactly the same as 'Man bites dog'."
    },
    {
      prompt: "What is the purpose of the scaling factor (sqrt(d_k)) in the attention formula?",
      explanation: "For large dimensions, the dot product of Q and K can grow very large, pushing the softmax function into regions where it has extremely small gradients (vanishing gradients). The scaling factor counteracts this."
    }
  ],
  test: [
    {
      question: "Which component allows the Transformer to focus on different parts of the input sequence simultaneously for a single output token?",
      options: [
        "Positional Encoding",
        "Multi-Head Attention",
        "Layer Normalization",
        "Feed-Forward Network"
      ],
      correctOptionIndex: 1,
      explanation: "Multi-Head Attention runs multiple self-attention operations in parallel, allowing the model to attend to different representation subspaces (e.g., one head might focus on grammar, another on semantic relationships)."
    }
  ]
};

export const initialStudyState: StudyState = {
  isStudying: false,
  activeMode: "understand",
  material: {
    status: "idle",
    data: null,
    error: null,
  },
  recallIndex: 0,
  testIndex: 0,
};

export function studyReducer(state: StudyState, action: StudyAction): StudyState {
  switch (action.type) {
    case "START_STUDY":
      return {
        ...state,
        isStudying: true,
        activeMode: "understand",
        material: action.payload,
        recallIndex: 0,
        testIndex: 0,
      };
    case "SET_MODE":
      return { ...state, activeMode: action.payload };
    case "NEXT_RECALL":
      return { ...state, recallIndex: state.recallIndex + 1 };
    case "NEXT_TEST":
      return { ...state, testIndex: state.testIndex + 1 };
    case "START_HYDRATION":
      return { ...state, material: startResourceHydration(state.material, action.payload.requestId) };
    case "ABORT_HYDRATION":
      return { ...state, material: abortResourceHydration(state.material, action.payload.requestId) };
    case "END_STUDY":
      return initialStudyState;
    default:
      return state;
  }
}
