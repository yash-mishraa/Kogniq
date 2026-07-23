import type { KnowledgeConceptId, KnowledgeGraph } from "./KnowledgeTypes";

import type { ResourceState } from "@/lib/core/ResourceState";

export interface KnowledgeState {
  graph: ResourceState<KnowledgeGraph>;
  activeConceptId: KnowledgeConceptId | null;
  trail: KnowledgeConceptId[]; // History of visited concepts
}

export type KnowledgeAction =
  | { type: "SET_GRAPH"; payload: ResourceState<KnowledgeGraph> }
  | { type: "SELECT_CONCEPT"; payload: KnowledgeConceptId | null };

export const MOCK_TRANSFORMER_GRAPH: KnowledgeGraph = {
  concepts: [
    {
      id: "transformer",
      label: "Transformer Architecture",
      explanation: "A neural network architecture that relies entirely on self-attention mechanisms, dispensing with recurrence and convolutions entirely.",
      importance: "primary",
    },
    {
      id: "self-attention",
      label: "Self Attention",
      explanation: "Allows every token in an input sequence to attend to every other token, capturing complex dependencies regardless of their distance.",
      importance: "primary",
    },
    {
      id: "encoder",
      label: "Encoder",
      explanation: "Processes the input sequence into a continuous representation that holds the learned information.",
      importance: "secondary",
    },
    {
      id: "decoder",
      label: "Decoder",
      explanation: "Generates the output sequence autoregressively, attending to both the encoder's output and previously generated tokens.",
      importance: "secondary",
    },
    {
      id: "multi-head-attention",
      label: "Multi Head Attention",
      explanation: "Runs multiple attention mechanisms in parallel, allowing the model to jointly attend to information from different representation subspaces.",
      importance: "secondary",
    },
    {
      id: "attention-weights",
      label: "Attention Weights",
      explanation: "The computed probabilities that determine how much focus each token should place on other tokens.",
      importance: "tertiary",
    },
    {
      id: "residual-connection",
      label: "Residual Connection",
      explanation: "Adds the input of a layer to its output, preventing the vanishing gradient problem in deep networks.",
      importance: "tertiary",
    },
    {
      id: "layer-normalization",
      label: "Layer Normalization",
      explanation: "Normalizes the inputs across the features for each token, stabilizing the learning process.",
      importance: "tertiary",
    },
    {
      id: "positional-encoding",
      label: "Positional Encoding",
      explanation: "Injects information about the relative or absolute position of tokens since the architecture lacks recurrence.",
      importance: "secondary",
    },
    {
      id: "feed-forward-network",
      label: "Feed Forward Network",
      explanation: "Applies a non-linear transformation to each token's representation independently and identically.",
      importance: "tertiary",
    },
  ],
  relationships: [
    { sourceId: "transformer", targetId: "encoder" },
    { sourceId: "transformer", targetId: "decoder" },
    { sourceId: "encoder", targetId: "self-attention" },
    { sourceId: "decoder", targetId: "self-attention" },
    { sourceId: "self-attention", targetId: "multi-head-attention" },
    { sourceId: "multi-head-attention", targetId: "attention-weights" },
    { sourceId: "transformer", targetId: "positional-encoding" },
    { sourceId: "encoder", targetId: "feed-forward-network" },
    { sourceId: "decoder", targetId: "feed-forward-network" },
    { sourceId: "encoder", targetId: "residual-connection" },
    { sourceId: "encoder", targetId: "layer-normalization" },
    { sourceId: "decoder", targetId: "residual-connection" },
    { sourceId: "decoder", targetId: "layer-normalization" },
  ],
  evidence: [
    {
      conceptId: "transformer",
      documentId: "attention-is-all-you-need",
      snippet: "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
    },
    {
      conceptId: "self-attention",
      documentId: "attention-is-all-you-need",
      snippet: "Self-attention, sometimes called intra-attention is an attention mechanism relating different positions of a single sequence in order to compute a representation of the sequence.",
    },
  ],
};
