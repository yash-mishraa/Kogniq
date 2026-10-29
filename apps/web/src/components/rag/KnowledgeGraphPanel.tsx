"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
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
  onAsk?: (query: string, documentIds: string[]) => void;
  onNavigate?: (view: "flashcards" | "ask" | "quizzes") => void;
}

function formatRelType(type: string | number): string {
  const map: Record<string, string> = {
    "1": "Depends On",
    "2": "Uses",
    "3": "Defines",
    "4": "References",
    "5": "Extends",
    "6": "Implements",
    "7": "Explains",
    "8": "Related To",
    DEPENDS_ON: "Depends On",
    USES: "Uses",
    DEFINES: "Defines",
    REFERENCES: "References",
    EXTENDS: "Extends",
    IMPLEMENTS: "Implements",
    EXPLAINS: "Explains",
    RELATED_TO: "Related To",
  };
  return map[String(type).toUpperCase()] || String(type).replace(/_/g, " ");
}

function getConceptStyle(type: string) {
  const t = (type || "").toUpperCase();
  if (t.includes("ALGO")) {
    return {
      fill: "#064e3b",
      stroke: "#10b981",
      glow: "rgba(16,185,129,0.35)",
      badge: "border-emerald-800/60 bg-emerald-950/40 text-emerald-400",
      dot: "bg-emerald-400",
    };
  }
  if (t.includes("DEF")) {
    return {
      fill: "#0c4a6e",
      stroke: "#38bdf8",
      glow: "rgba(56,189,248,0.35)",
      badge: "border-sky-800/60 bg-sky-950/40 text-sky-400",
      dot: "bg-sky-400",
    };
  }
  if (t.includes("THEORY") || t.includes("PRINCIPLE")) {
    return {
      fill: "#3b0764",
      stroke: "#c084fc",
      glow: "rgba(192,132,252,0.35)",
      badge: "border-purple-800/60 bg-purple-950/40 text-purple-300",
      dot: "bg-purple-400",
    };
  }
  if (t.includes("DATA") || t.includes("STRUCT")) {
    return {
      fill: "#4c0519",
      stroke: "#fb7185",
      glow: "rgba(251,113,133,0.35)",
      badge: "border-rose-800/60 bg-rose-950/40 text-rose-300",
      dot: "bg-rose-400",
    };
  }
  return {
    fill: "#27272a",
    stroke: "#a1a1aa",
    glow: "rgba(161,161,170,0.25)",
    badge: "border-zinc-700/60 bg-zinc-900/60 text-zinc-300",
    dot: "bg-zinc-400",
  };
}

export function KnowledgeGraphPanel({
  initialDocumentId,
  onOpenDocuments,
  onAsk,
  onNavigate,
}: KnowledgeGraphPanelProps) {
  const queryClient = useQueryClient();
  const [selectedDocId, setSelectedDocId] = useState<string>(initialDocumentId || "");
  const [searchQuery, setSearchQuery] = useState("");
  const [activeConceptId, setActiveConceptId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

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

  const filteredConcepts = useMemo(() => {
    if (!searchQuery.trim()) return graphData.concepts;
    const q = searchQuery.toLowerCase();
    return graphData.concepts.filter(
      (c) =>
        c.name.toLowerCase().includes(q) ||
        (c.description && c.description.toLowerCase().includes(q)) ||
        c.concept_type.toLowerCase().includes(q)
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
        r.target_concept === activeConcept.name
    );
  }, [activeConcept, graphData.relationships]);

  // Compute organic tiered layout
  const layout = useMemo(() => {
    const concepts = graphData.concepts;
    const count = concepts.length;
    if (count === 0) return { nodes: [], edges: [] };

    const width = 800;
    const height = 500;
    const centerX = width / 2;
    const centerY = height / 2;

    // Calculate degree (connection count) for each concept
    const degrees: Record<string, number> = {};
    concepts.forEach((c) => {
      degrees[c.id] = 0;
      degrees[c.name] = 0;
    });
    graphData.relationships.forEach((r) => {
      degrees[r.source_concept] = (degrees[r.source_concept] || 0) + 1;
      degrees[r.target_concept] = (degrees[r.target_concept] || 0) + 1;
    });

    // Partition into core hubs (top degree) and satellites
    const sorted = [...concepts].sort(
      (a, b) => (degrees[b.id] || degrees[b.name] || 0) - (degrees[a.id] || degrees[a.name] || 0)
    );

    const nodePositions: Record<string, { x: number; y: number; concept: KnowledgeConceptItemData; isHub: boolean }> = {};

    const hubCount = Math.min(3, Math.max(1, Math.floor(count * 0.3)));
    const hubs = sorted.slice(0, hubCount);
    const satellites = sorted.slice(hubCount);

    // Place hubs closer to the center
    hubs.forEach((hub, i) => {
      if (hubs.length === 1) {
        nodePositions[hub.id] = { x: centerX, y: centerY, concept: hub, isHub: true };
        nodePositions[hub.name] = nodePositions[hub.id];
      } else {
        const angle = (2 * Math.PI * i) / hubs.length - Math.PI / 2;
        const dist = 75;
        const x = centerX + dist * Math.cos(angle);
        const y = centerY + dist * Math.sin(angle);
        nodePositions[hub.id] = { x, y, concept: hub, isHub: true };
        nodePositions[hub.name] = nodePositions[hub.id];
      }
    });

    // Place satellites in an outer ring with slight staggered radius to prevent label collision
    satellites.forEach((sat, i) => {
      const angle = (2 * Math.PI * i) / satellites.length - Math.PI / 4;
      const stagger = (i % 2 === 0 ? 0 : 25);
      const radius = 175 + stagger;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);
      nodePositions[sat.id] = { x, y, concept: sat, isHub: false };
      nodePositions[sat.name] = nodePositions[sat.id];
    });

    const edges = graphData.relationships
      .map((rel) => {
        const source = nodePositions[rel.source_concept];
        const target = nodePositions[rel.target_concept];
        if (!source || !target) return null;
        const isHighlighted = Boolean(
          activeConcept &&
            (rel.source_concept === activeConcept.id ||
              rel.target_concept === activeConcept.id ||
              rel.source_concept === activeConcept.name ||
              rel.target_concept === activeConcept.name)
        );
        return {
          id: rel.id,
          x1: source.x,
          y1: source.y,
          x2: target.x,
          y2: target.y,
          label: formatRelType(rel.relationship_type),
          isHighlighted,
        };
      })
      .filter(Boolean);

    const nodes = concepts.map((concept) => {
      const pos = nodePositions[concept.id] || { x: centerX, y: centerY, isHub: false };
      const isSelected = activeConcept?.id === concept.id;
      const isConnected = Boolean(
        activeConcept &&
          relatedEdges.some(
            (r) =>
              (r.source_concept === concept.id || r.source_concept === concept.name) ||
              (r.target_concept === concept.id || r.target_concept === concept.name)
          )
      );
      return {
        id: concept.id,
        name: concept.name,
        type: concept.concept_type,
        x: pos.x,
        y: pos.y,
        isHub: pos.isHub,
        isSelected,
        isConnected,
        isDimmed: Boolean(activeConcept && !isSelected && !isConnected),
      };
    });

    return { nodes, edges };
  }, [graphData.concepts, graphData.relationships, activeConcept, relatedEdges]);

  const handleAskAboutConcept = () => {
    if (!activeConcept || !onAsk) return;
    onAsk(`Explain "${activeConcept.name}" and how it is used in this document.`, activeDocId ? [activeDocId] : []);
  };

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-6 py-6 px-4">
      <SectionHeading
        eyebrow="Explore"
        title="Knowledge Graph"
        detail="Explore key concepts, structural hierarchies, and domain relationships extracted from your documents."
      />

      {/* Document Selector & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-4 rounded-lg border border-[#1f1f1f] bg-[#0c0c0c] p-4">
        <div className="flex items-center gap-3">
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
          {extractMutation.isPending ? "Extracting Concepts..." : "Re-extract Graph"}
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
          <h3 className="text-base font-medium text-[#f0f0f0]">Knowledge graph not yet extracted</h3>
          <p className="mt-2 text-xs text-[#888888] max-w-md leading-relaxed">
            Extract concepts and domain relationships from this document using AI to explore conceptual connections and power flashcards.
          </p>
          <Button
            size="sm"
            onClick={() => extractMutation.mutate()}
            disabled={extractMutation.isPending}
            className="mt-5 text-xs"
          >
            {extractMutation.isPending ? "Extracting..." : "Extract Knowledge Graph"}
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Interactive Graph Canvas */}
          <div className="lg:col-span-2 flex flex-col rounded-xl border border-[#222222] bg-[#09090b] p-4 shadow-2xl relative overflow-hidden">
            {/* Canvas Header & Stats */}
            <div className="flex items-center justify-between border-b border-[#1c1c1f] pb-3 mb-2 px-1">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs uppercase tracking-wider text-[#a1a1aa]">
                  {graphData.concepts.length} Concepts
                </span>
                <span className="text-[#3f3f46]">•</span>
                <span className="font-mono text-xs uppercase tracking-wider text-[#71717a]">
                  {graphData.relationships.length} Relationships
                </span>
              </div>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => setZoomLevel((z) => Math.min(1.6, z + 0.15))}
                  className="rounded border border-[#27272a] bg-[#18181b] px-2 py-0.5 text-xs text-[#d4d4d8] hover:bg-[#27272a]"
                  title="Zoom In"
                >
                  +
                </button>
                <button
                  type="button"
                  onClick={() => setZoomLevel((z) => Math.max(0.7, z - 0.15))}
                  className="rounded border border-[#27272a] bg-[#18181b] px-2 py-0.5 text-xs text-[#d4d4d8] hover:bg-[#27272a]"
                  title="Zoom Out"
                >
                  −
                </button>
                <button
                  type="button"
                  onClick={() => setZoomLevel(1)}
                  className="rounded border border-[#27272a] bg-[#18181b] px-2 py-0.5 text-[10px] uppercase font-mono text-[#a1a1aa] hover:bg-[#27272a]"
                  title="Reset Zoom"
                >
                  Reset
                </button>
              </div>
            </div>

            {/* SVG Visual Canvas */}
            <div className="relative flex items-center justify-center w-full min-h-[460px] overflow-hidden rounded-lg bg-[#050507]">
              <svg
                viewBox="0 0 800 500"
                className="w-full h-full max-h-[500px] transition-transform duration-200"
                style={{ transform: `scale(${zoomLevel})` }}
              >
                <defs>
                  {/* Subtle Background Grid */}
                  <pattern id="graph-grid" width="30" height="30" patternUnits="userSpaceOnUse">
                    <circle cx="15" cy="15" r="0.8" fill="#1e1e24" />
                  </pattern>

                  {/* Marker Arrow */}
                  <marker
                    id="arrow"
                    viewBox="0 0 10 10"
                    refX="22"
                    refY="5"
                    markerWidth="6"
                    markerHeight="6"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#52525b" />
                  </marker>
                  <marker
                    id="arrow-active"
                    viewBox="0 0 10 10"
                    refX="22"
                    refY="5"
                    markerWidth="7"
                    markerHeight="7"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#ffffff" />
                  </marker>
                </defs>

                <rect width="800" height="500" fill="url(#graph-grid)" />

                {/* Relationships / Edges */}
                {layout.edges.map((edge) => {
                  if (!edge) return null;
                  return (
                    <g key={edge.id} className="transition-opacity duration-300">
                      <line
                        x1={edge.x1}
                        y1={edge.y1}
                        x2={edge.x2}
                        y2={edge.y2}
                        stroke={edge.isHighlighted ? "#ffffff" : "#27272a"}
                        strokeWidth={edge.isHighlighted ? 2 : 1}
                        strokeDasharray={edge.isHighlighted ? "none" : "3,3"}
                        opacity={edge.isHighlighted ? 0.95 : activeConcept ? 0.15 : 0.45}
                        markerEnd={edge.isHighlighted ? "url(#arrow-active)" : "url(#arrow)"}
                      />
                      {edge.isHighlighted && (
                        <g>
                          <rect
                            x={(edge.x1 + edge.x2) / 2 - 38}
                            y={(edge.y1 + edge.y2) / 2 - 10}
                            width="76"
                            height="16"
                            rx="3"
                            fill="#18181b"
                            stroke="#3f3f46"
                            strokeWidth="0.8"
                          />
                          <text
                            x={(edge.x1 + edge.x2) / 2}
                            y={(edge.y1 + edge.y2) / 2 + 1}
                            fill="#e4e4e7"
                            fontSize="8"
                            textAnchor="middle"
                            dominantBaseline="middle"
                            className="font-mono uppercase tracking-wider select-none"
                          >
                            {edge.label}
                          </text>
                        </g>
                      )}
                    </g>
                  );
                })}

                {/* Concepts / Nodes */}
                {layout.nodes.map((node) => {
                  const style = getConceptStyle(node.type);
                  const radius = node.isSelected ? 18 : node.isHub ? 15 : 12;

                  return (
                    <g
                      key={node.id}
                      onClick={() => setActiveConceptId(node.id)}
                      className={`cursor-pointer transition-opacity duration-200 ${
                        node.isDimmed ? "opacity-25 hover:opacity-80" : "opacity-100"
                      }`}
                    >
                      {/* Active / Highlight Outer Halo */}
                      {node.isSelected && (
                        <circle
                          cx={node.x}
                          cy={node.y}
                          r={radius + 8}
                          fill="none"
                          stroke="#ffffff"
                          strokeWidth="1.5"
                          opacity="0.3"
                          className="animate-pulse"
                        />
                      )}

                      {/* Node Circle */}
                      <circle
                        cx={node.x}
                        cy={node.y}
                        r={radius}
                        fill={node.isSelected ? "#ffffff" : style.fill}
                        stroke={node.isSelected ? "#ffffff" : style.stroke}
                        strokeWidth={node.isSelected ? 2.5 : node.isHub ? 2 : 1.2}
                      />

                      {/* Label Text with readability pill background */}
                      <g>
                        <text
                          x={node.x}
                          y={node.y + radius + 14}
                          fill={node.isSelected ? "#ffffff" : "#d4d4d8"}
                          fontSize={node.isSelected ? "11" : "10"}
                          fontWeight={node.isSelected ? "600" : "400"}
                          textAnchor="middle"
                          className="font-sans select-none tracking-tight"
                          stroke="#050507"
                          strokeWidth="3"
                          paintOrder="stroke fill"
                        >
                          {node.name.length > 20 ? `${node.name.slice(0, 18)}…` : node.name}
                        </text>
                      </g>
                    </g>
                  );
                })}
              </svg>
            </div>
          </div>

          {/* Detailed Concept Inspector Sidebar */}
          <div className="flex flex-col gap-4 rounded-xl border border-[#222222] bg-[#0c0c0e] p-5 shadow-2xl">
            {/* Search Input */}
            <div className="relative">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search concepts in graph..."
                className="w-full rounded border border-[#27272a] bg-[#141416] py-1.5 px-3 text-xs text-[#f4f4f5] focus:border-[#52525b] focus:outline-none"
              />
            </div>

            {/* Selected Concept Deep Dive */}
            {activeConcept ? (
              <div className="flex flex-col gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span
                      className={`rounded px-2 py-0.5 font-mono text-[9px] uppercase tracking-wider border ${
                        getConceptStyle(activeConcept.concept_type).badge
                      }`}
                    >
                      {activeConcept.concept_type || "CONCEPT"}
                    </span>
                  </div>
                  <h4 className="text-lg font-semibold text-[#fafafa] tracking-tight">
                    {activeConcept.name}
                  </h4>
                  <p className="mt-2 text-xs leading-relaxed text-[#a1a1aa]">
                    {activeConcept.description ||
                      `${activeConcept.name} is a key conceptual component extracted from this document.`}
                  </p>
                </div>

                {/* Direct Connections */}
                <div className="border-t border-[#1f1f23] pt-3">
                  <h5 className="text-[10px] font-mono uppercase tracking-wider text-[#71717a] mb-2.5">
                    Connected Concepts ({relatedEdges.length})
                  </h5>
                  {relatedEdges.length === 0 ? (
                    <p className="text-xs text-[#52525b]">No direct relationships documented.</p>
                  ) : (
                    <div className="flex flex-col gap-2 max-h-[170px] overflow-y-auto pr-1">
                      {relatedEdges.map((rel) => {
                        const isSource =
                          rel.source_concept === activeConcept.id ||
                          rel.source_concept === activeConcept.name;
                        const otherConceptName = isSource ? rel.target_concept : rel.source_concept;
                        const targetConcept = graphData.concepts.find(
                          (c) => c.id === otherConceptName || c.name === otherConceptName
                        );

                        return (
                          <button
                            key={rel.id}
                            type="button"
                            onClick={() => targetConcept && setActiveConceptId(targetConcept.id)}
                            className="flex items-center justify-between rounded border border-[#27272a] bg-[#121214] p-2 text-left text-xs hover:border-[#3f3f46] hover:bg-[#18181b] transition-all"
                          >
                            <span className="font-medium text-[#e4e4e7] truncate max-w-[150px]">
                              {targetConcept?.name || otherConceptName}
                            </span>
                            <span className="font-mono text-[9px] uppercase tracking-wider text-[#a1a1aa] bg-[#1c1c20] px-2 py-0.5 rounded border border-[#2a2a30] shrink-0 ml-2">
                              {formatRelType(rel.relationship_type)}
                            </span>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Quick Actions */}
                <div className="border-t border-[#1f1f23] pt-3 flex flex-col gap-2">
                  {onAsk && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={handleAskAboutConcept}
                      className="w-full border border-[#27272a] bg-[#141416] text-xs text-[#e4e4e7] hover:bg-[#202024] justify-center"
                    >
                      Ask Question about {activeConcept.name.slice(0, 18)}
                    </Button>
                  )}
                  {onNavigate && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => onNavigate("flashcards")}
                      className="w-full border border-[#27272a] text-xs text-[#a1a1aa] hover:bg-[#18181b] justify-center"
                    >
                      Study Flashcards
                    </Button>
                  )}
                </div>

                {/* Concept Directory Pills */}
                <div className="border-t border-[#1f1f23] pt-3">
                  <h5 className="text-[10px] font-mono uppercase tracking-wider text-[#71717a] mb-2">
                    All Extracted Concepts ({filteredConcepts.length})
                  </h5>
                  <div className="flex flex-wrap gap-1.5 max-h-[110px] overflow-y-auto">
                    {filteredConcepts.map((c) => {
                      const isCurrent = c.id === activeConcept.id;
                      return (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => setActiveConceptId(c.id)}
                          className={`rounded px-2 py-1 text-[11px] transition-all ${
                            isCurrent
                              ? "bg-[#ffffff] text-[#000000] font-medium shadow"
                              : "border border-[#27272a] bg-[#141416] text-[#a1a1aa] hover:text-[#fafafa] hover:border-[#3f3f46]"
                          }`}
                        >
                          {c.name}
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-[#52525b]">Select a concept to inspect its details.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
