"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import {
  BookOpen,
  Network,
  Search,
  Sparkles,
} from "lucide-react";
import { Button } from "@/components/ui";
import {
  KnowledgeConceptItemData,
  KnowledgeGraphResultData,
  ragApi,
} from "@/lib/rag/api";
import { SectionHeading, UserErrorNotice } from "./shared";

interface KnowledgeGraphPanelProps {
  initialDocumentId?: string;
  onOpenDocuments?: () => void;
}

export function KnowledgeGraphPanel({
  initialDocumentId,
  onOpenDocuments,
}: KnowledgeGraphPanelProps) {
  const queryClient = useQueryClient();
  const [selectedDocId, setSelectedDocId] = useState<string>(initialDocumentId || "");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeConceptId, setActiveConceptId] = useState<string | null>(null);

  const docsQuery = useQuery({
    queryKey: ["documents"],
    queryFn: ragApi.documents,
  });

  const readyDocs = (docsQuery.data || []).filter((d) => d.status === "Ready");
  const activeDocId = selectedDocId || (readyDocs.length > 0 ? readyDocs[0].id : "");

  const graphQuery = useQuery({
    queryKey: ["knowledgeGraph", activeDocId],
    queryFn: () => ragApi.getKnowledgeGraph(activeDocId),
    enabled: Boolean(activeDocId),
  });

  const extractMutation = useMutation({
    mutationFn: () => ragApi.extractKnowledgeGraph(activeDocId),
    onSuccess: (data) => {
      queryClient.setQueryData(["knowledgeGraph", activeDocId], data);
      if (data.concepts.length > 0) {
        setActiveConceptId(data.concepts[0].id);
      }
    },
  });

  const graphData: KnowledgeGraphResultData = graphQuery.data || {
    concepts: [],
    relationships: [],
  };

  // Filter concepts based on search
  const filteredConcepts = useMemo(() => {
    if (!searchQuery.trim()) return graphData.concepts;
    const q = searchQuery.toLowerCase();
    return graphData.concepts.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        c.description.toLowerCase().includes(q) ||
        c.concept_type.toLowerCase().includes(q),
    );
  }, [graphData.concepts, searchQuery]);

  const activeConcept: KnowledgeConceptItemData | undefined =
    graphData.concepts.find((c) => c.id === activeConceptId) ||
    (graphData.concepts.length > 0 ? graphData.concepts[0] : undefined);

  // Find relationships for active concept
  const relatedEdges = useMemo(() => {
    if (!activeConcept) return [];
    return graphData.relationships.filter(
      (r) =>
        r.source_concept === activeConcept.id ||
        r.target_concept === activeConcept.id ||
        r.source_concept === activeConcept.name ||
        r.target_concept === activeConcept.name,
    );
  }, [activeConcept, graphData.relationships]);

  // Compute node positions for restrained SVG graph visualization
  const layout = useMemo(() => {
    const concepts = graphData.concepts;
    const count = concepts.length;
    if (count === 0) return { nodes: [], edges: [] };

    const width = 600;
    const height = 400;
    const centerX = width / 2;
    const centerY = height / 2;
    const radius = Math.min(width, height) * 0.38;

    const nodePositions: Record<string, { x: number; y: number; concept: KnowledgeConceptItemData }> = {};

    concepts.forEach((concept, i) => {
      const angle = (2 * Math.PI * i) / count;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      nodePositions[concept.id] = { x, y, concept };
      nodePositions[concept.name] = { x, y, concept };
    });

    const edges = graphData.relationships
      .map((rel) => {
        const source = nodePositions[rel.source_concept];
        const target = nodePositions[rel.target_concept];
        if (!source || !target) return null;
        return {
          id: rel.id,
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          label: rel.relationship_type,
          isHighlighted:
            activeConcept &&
            (rel.source_concept === activeConcept.id ||
              rel.target_concept === activeConcept.id ||
              rel.source_concept === activeConcept.name ||
              rel.target_concept === activeConcept.name),
        };
      })
      .filter(Boolean);

    const nodes = concepts.map((concept) => {
      const pos = nodePositions[concept.id] || { x: centerX, y: centerY };
      return {
        id: concept.id,
        name: concept.name,
        type: concept.concept_type,
        x: pos.x,
        y: pos.y,
        isSelected: activeConcept?.id === concept.id,
      };
    });

    return { nodes, edges };
  }, [graphData.concepts, graphData.relationships, activeConcept]);

  return (
    <div className="mx-auto flex w-full max-w-5xl flex-col gap-6 py-6 px-4">
      <SectionHeading
        eyebrow="Explore"
        title="Knowledge Graph"
        detail="Explore key concepts and conceptual relationships extracted from your documents."
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
              setActiveConceptId(null);
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

        <Button
          size="sm"
          onClick={() => extractMutation.mutate()}
          disabled={!activeDocId || extractMutation.isPending}
          className="border border-[#383838] bg-[#1a1a1a] text-xs text-[#f0f0f0] hover:bg-[#262626]"
        >
          <Sparkles className="mr-1.5 h-3.5 w-3.5 text-[#a0a0a0]" />
          {extractMutation.isPending ? "Extracting..." : "Extract Graph"}
        </Button>
      </div>

      {extractMutation.error && (
        <UserErrorNotice
          error={extractMutation.error}
          onRetry={() => extractMutation.mutate()}
        />
      )}

      {/* Content Area */}
      {readyDocs.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-12 text-center">
          <Network className="h-10 w-10 text-[#555555] mb-3" />
          <h3 className="text-base font-medium text-[#f0f0f0]">No documents ready</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Upload and index a document first to explore its conceptual knowledge graph.
          </p>
          {onOpenDocuments && (
            <Button size="sm" onClick={onOpenDocuments} className="mt-4 text-xs">
              Open Documents
            </Button>
          )}
        </div>
      ) : graphQuery.isLoading ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-16 text-center">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-[#555555] border-t-[#ffffff] mb-3" />
          <p className="text-xs text-[#888888]">Loading knowledge graph...</p>
        </div>
      ) : graphData.concepts.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-12 text-center">
          <Network className="h-10 w-10 text-[#555555] mb-3" />
          <h3 className="text-base font-medium text-[#f0f0f0]">Knowledge graph not yet extracted</h3>
          <p className="mt-1 text-xs text-[#888888] max-w-sm">
            Extract concepts and domain relationships from this document using local or cloud AI.
          </p>
          <Button
            size="sm"
            onClick={() => extractMutation.mutate()}
            disabled={extractMutation.isPending}
            className="mt-5 text-xs"
          >
            <Sparkles className="mr-1.5 h-3.5 w-3.5" />
            Extract Concepts & Relationships
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Graph Visualization / Canvas */}
          <div className="lg:col-span-2 flex flex-col rounded-xl border border-[#262626] bg-[#0a0a0a] p-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-[#1c1c1c] pb-3 mb-2 px-2">
              <div className="flex items-center gap-2">
                <Network className="h-4 w-4 text-[#888888]" />
                <span className="text-xs font-medium text-[#f0f0f0]">
                  {graphData.concepts.length} Concepts • {graphData.relationships.length} Relationships
                </span>
              </div>
              <span className="text-[11px] text-[#666666]">Click node to inspect</span>
            </div>

            {/* Restrained SVG Graph Rendering */}
            <div className="relative flex items-center justify-center w-full min-h-[420px] overflow-hidden rounded-lg bg-[#080808]">
              <svg viewBox="0 0 600 400" className="w-full h-full max-h-[480px]">
                {/* Edges */}
                {layout.edges.map((edge) => (
                  <g key={edge?.id}>
                    <line
                      x1={edge?.x1}
                      y1={edge?.y1}
                      x2={edge?.x2}
                      y2={edge?.y2}
                      stroke={edge?.isHighlighted ? "#ffffff" : "#2a2a2a"}
                      strokeWidth={edge?.isHighlighted ? 1.8 : 1}
                      strokeDasharray={edge?.isHighlighted ? "none" : "3,3"}
                      opacity={edge?.isHighlighted ? 0.9 : 0.4}
                    />
                    {edge?.isHighlighted && (
                      <text
                        x={(edge.x1 + edge.x2) / 2}
                        y={(edge.y1 + edge.y2) / 2 - 4}
                        fill="#888888"
                        fontSize="9"
                        textAnchor="middle"
                        className="font-mono uppercase tracking-widest"
                      >
                        {edge.label}
                      </text>
                    )}
                  </g>
                ))}

                {/* Nodes */}
                {layout.nodes.map((node) => (
                  <g
                    key={node.id}
                    onClick={() => setActiveConceptId(node.id)}
                    className="cursor-pointer transition-all"
                  >
                    <circle
                      cx={node.x}
                      cy={node.y}
                      r={node.isSelected ? 16 : 11}
                      fill={node.isSelected ? "#ffffff" : "#1a1a1a"}
                      stroke={node.isSelected ? "#ffffff" : "#444444"}
                      strokeWidth={node.isSelected ? 2 : 1}
                    />
                    <text
                      x={node.x}
                      y={node.y + (node.isSelected ? 26 : 22)}
                      fill={node.isSelected ? "#ffffff" : "#b0b0b0"}
                      fontSize={node.isSelected ? "11" : "10"}
                      fontWeight={node.isSelected ? "600" : "400"}
                      textAnchor="middle"
                      className="font-sans select-none"
                    >
                      {node.name.length > 18 ? `${node.name.slice(0, 16)}...` : node.name}
                    </text>
                  </g>
                ))}
              </svg>
            </div>
          </div>

          {/* Concept Inspector Sidebar */}
          <div className="flex flex-col gap-4 rounded-xl border border-[#262626] bg-[#0c0c0c] p-5 shadow-xl">
            {/* Search Input */}
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-3.5 w-3.5 text-[#666666]" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search concepts..."
                className="w-full rounded border border-[#262626] bg-[#141414] py-1.5 pl-8 pr-3 text-xs text-[#f0f0f0] focus:border-[#444444] focus:outline-none"
              />
            </div>

            {/* Concept Details */}
            {activeConcept ? (
              <div className="flex flex-col gap-4">
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="rounded bg-[#1a1a1a] px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider text-[#888888] border border-[#262626]">
                      {activeConcept.concept_type || "CONCEPT"}
                    </span>
                  </div>
                  <h4 className="text-base font-semibold text-[#f5f5f5]">
                    {activeConcept.name}
                  </h4>
                  <p className="mt-2 text-xs leading-relaxed text-[#b0b0b0]">
                    {activeConcept.description || "No description provided."}
                  </p>
                </div>

                {/* Connected Concepts */}
                <div className="border-t border-[#1c1c1c] pt-3">
                  <h5 className="text-[11px] font-mono uppercase tracking-wider text-[#777777] mb-2">
                    Connected Concepts ({relatedEdges.length})
                  </h5>
                  {relatedEdges.length === 0 ? (
                    <p className="text-xs text-[#555555]">No direct relationships.</p>
                  ) : (
                    <div className="flex flex-col gap-2 max-h-[160px] overflow-y-auto pr-1">
                      {relatedEdges.map((rel) => {
                        const isSource =
                          rel.source_concept === activeConcept.id ||
                          rel.source_concept === activeConcept.name;
                        const otherConceptName = isSource ? rel.target_concept : rel.source_concept;
                        const targetConcept = graphData.concepts.find(
                          (c) => c.id === otherConceptName || c.name === otherConceptName,
                        );

                        return (
                          <button
                            key={rel.id}
                            onClick={() => targetConcept && setActiveConceptId(targetConcept.id)}
                            className="flex items-center justify-between rounded border border-[#1f1f1f] bg-[#121212] p-2 text-left text-xs hover:border-[#333333] transition-colors"
                          >
                            <span className="font-medium text-[#d0d0d0] truncate">
                              {targetConcept?.name || otherConceptName}
                            </span>
                            <span className="font-mono text-[9px] uppercase tracking-widest text-[#777777] ml-2 shrink-0">
                              {rel.relationship_type}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Filtered Concept Directory */}
                <div className="border-t border-[#1c1c1c] pt-3">
                  <h5 className="text-[11px] font-mono uppercase tracking-wider text-[#777777] mb-2">
                    All Concepts ({filteredConcepts.length})
                  </h5>
                  <div className="flex flex-wrap gap-1.5 max-h-[120px] overflow-y-auto">
                    {filteredConcepts.map((c) => (
                      <button
                        key={c.id}
                        onClick={() => setActiveConceptId(c.id)}
                        className={`rounded px-2 py-1 text-[11px] transition-colors ${
                          c.id === activeConcept.id
                            ? "bg-[#ffffff] text-[#000000] font-medium"
                            : "border border-[#222222] bg-[#141414] text-[#888888] hover:text-[#f0f0f0]"
                        }`}
                      >
                        {c.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-[#555555]">Select a concept to inspect.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
