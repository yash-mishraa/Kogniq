from dataclasses import dataclass, field
from typing import Any

from backend.services.knowledge_service import KnowledgeService
from knowledge.graph import KnowledgeGraph
from knowledge.enums import RelationshipType

@dataclass
class QueryKnowledgeGraphRequest:
    document_id: str
    user_id: str
    query_type: str
    concept: str
    depth: int = 1

@dataclass
class QueryKnowledgeGraphResponse:
    status: str
    query_type: str
    resolved_concept: dict[str, str] | None = None
    concepts: list[dict[str, str]] = field(default_factory=list)
    relationships: list[dict[str, str]] = field(default_factory=list)
    truncated: bool = False
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        res: dict[str, Any] = {
            "status": self.status,
            "query_type": self.query_type,
            "truncated": self.truncated,
        }
        if self.message:
            res["message"] = self.message
        if self.resolved_concept:
            res["resolved_concept"] = self.resolved_concept
        if self.concepts:
            res["concepts"] = self.concepts
        if self.relationships:
            res["relationships"] = self.relationships
        return res

class QueryKnowledgeGraphUseCase:
    """Bounded BFS graph query over the document KnowledgeGraph."""

    # Traversal limits
    MAX_DEPTH = 3
    MAX_CONCEPTS = 20

    def __init__(self, knowledge_service: KnowledgeService) -> None:
        self.knowledge_service = knowledge_service

    async def execute(self, request: QueryKnowledgeGraphRequest) -> QueryKnowledgeGraphResponse:
        # 1. Fetch graph (handles auth/isolation internally)
        try:
            graph: KnowledgeGraph = await self.knowledge_service.get_knowledge_graph(
                document_id=request.document_id,
                user_id=request.user_id,
            )
        except Exception as e:
            return QueryKnowledgeGraphResponse(
                status="error",
                query_type=request.query_type,
                message=str(e),
            )

        if not graph.concepts or not graph.relationships:
            return QueryKnowledgeGraphResponse(
                status="empty",
                query_type=request.query_type,
                message="Document graph is empty or has no relationships.",
            )

        # 2. Resolve Concept
        target_name = request.concept.strip().lower()
        matches = []
        for c in graph.concepts:
            if c.name.strip().lower() == target_name:
                matches.append(c)
                continue
            for alias in c.aliases:
                if alias.strip().lower() == target_name:
                    matches.append(c)
                    break
        
        if not matches:
            return QueryKnowledgeGraphResponse(
                status="not_found",
                query_type=request.query_type,
                message=f"Concept '{request.concept}' not found in graph.",
            )
        
        if len(matches) > 1:
            return QueryKnowledgeGraphResponse(
                status="ambiguous",
                query_type=request.query_type,
                message=f"Multiple concepts match '{request.concept}'. Please be more specific.",
                concepts=[{"name": c.name, "description": c.description} for c in matches[:3]]
            )

        resolved_node = matches[0]
        
        # 3. BFS Traversal
        depth_limit = max(1, min(request.depth, self.MAX_DEPTH))
        
        # Setup directions based on query_type
        # Prerequisites: concept -> depends_on -> target (so outgoing edges)
        # Dependents: concept <- depends_on <- source (so incoming edges)
        # Neighbors: both
        # 
        # RelationshipTypes for prerequisites: DEPENDS_ON, USES, EXTENDS
        PREREQ_TYPES = {RelationshipType.DEPENDS_ON, RelationshipType.USES, RelationshipType.EXTENDS}
        
        visited_nodes = {resolved_node.id}
        collected_relationships = []
        
        # Queue stores tuples of (concept_id, current_depth)
        queue = [(resolved_node.id, 0)]
        
        truncated = False

        while queue:
            current_id, current_depth = queue.pop(0)
            
            if current_depth >= depth_limit:
                continue
                
            # Find relevant edges
            for rel in graph.relationships:
                is_prereq_type = rel.relationship_type in PREREQ_TYPES
                
                # Prerequisites (Outgoing PREREQ_TYPES)
                if request.query_type == "prerequisites":
                    if rel.source_concept == current_id and is_prereq_type:
                        nxt = rel.target_concept
                        if nxt not in visited_nodes:
                            if len(visited_nodes) >= self.MAX_CONCEPTS:
                                truncated = True
                                continue
                            visited_nodes.add(nxt)
                            queue.append((nxt, current_depth + 1))
                        if rel not in collected_relationships:
                            collected_relationships.append(rel)

                # Dependents (Incoming PREREQ_TYPES)
                elif request.query_type == "dependents":
                    if rel.target_concept == current_id and is_prereq_type:
                        nxt = rel.source_concept
                        if nxt not in visited_nodes:
                            if len(visited_nodes) >= self.MAX_CONCEPTS:
                                truncated = True
                                continue
                            visited_nodes.add(nxt)
                            queue.append((nxt, current_depth + 1))
                        if rel not in collected_relationships:
                            collected_relationships.append(rel)

                # Neighbors (All edges in both directions)
                elif request.query_type == "neighbors":
                    if rel.source_concept == current_id:
                        nxt = rel.target_concept
                        if nxt not in visited_nodes:
                            if len(visited_nodes) >= self.MAX_CONCEPTS:
                                truncated = True
                                continue
                            visited_nodes.add(nxt)
                            queue.append((nxt, current_depth + 1))
                        if rel not in collected_relationships:
                            collected_relationships.append(rel)
                            
                    elif rel.target_concept == current_id:
                        nxt = rel.source_concept
                        if nxt not in visited_nodes:
                            if len(visited_nodes) >= self.MAX_CONCEPTS:
                                truncated = True
                                continue
                            visited_nodes.add(nxt)
                            queue.append((nxt, current_depth + 1))
                        if rel not in collected_relationships:
                            collected_relationships.append(rel)

        # Build response concepts
        concept_map = {c.id: c for c in graph.concepts}
        result_concepts = []
        for vid in visited_nodes:
            if vid != resolved_node.id and vid in concept_map:
                c = concept_map[vid]
                result_concepts.append({"name": c.name, "description": c.description})

        # Deterministic sorting (confidence desc, then id)
        sorted_rels = sorted(collected_relationships, key=lambda r: (-r.confidence, r.id))
        result_rels = [
            {
                "source": concept_map[r.source_concept].name,
                "target": concept_map[r.target_concept].name,
                "type": r.relationship_type.name
            }
            for r in sorted_rels
            if r.source_concept in concept_map and r.target_concept in concept_map
        ]

        return QueryKnowledgeGraphResponse(
            status="success",
            query_type=request.query_type,
            resolved_concept={"name": resolved_node.name, "description": resolved_node.description},
            concepts=sorted(result_concepts, key=lambda c: c["name"]),
            relationships=result_rels,
            truncated=truncated
        )
