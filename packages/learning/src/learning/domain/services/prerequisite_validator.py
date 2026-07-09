from ..entities import Concept
from ..exceptions import CyclicPrerequisiteError
from ..value_objects import ConceptId


class PrerequisiteValidator:
    """
    Domain service responsible for ensuring prerequisite relationships do not form cycles.
    """

    @staticmethod
    def ensure_no_cycles(
        target_concept_id: ConceptId, new_prerequisite_id: ConceptId, all_concepts: list[Concept]
    ) -> None:
        """
        Validates that adding `new_prerequisite_id` to `target_concept_id` does not create a cycle.
        `all_concepts` should be the subset of concepts connected to this graph, 
        provided by a repository.
        """
        if target_concept_id == new_prerequisite_id:
            raise CyclicPrerequisiteError("A concept cannot be a prerequisite of itself.")

        # Build adjacency list
        graph: dict[ConceptId, list[ConceptId]] = {
            c.id: [p.required_concept_id for p in c.prerequisites] for c in all_concepts
        }

        # Simulating the addition
        if target_concept_id in graph:
            graph[target_concept_id].append(new_prerequisite_id)
        else:
            graph[target_concept_id] = [new_prerequisite_id]

        if new_prerequisite_id not in graph:
            graph[new_prerequisite_id] = []

        # DFS to find cycles starting from target_concept_id
        visited: set[ConceptId] = set()
        stack: set[ConceptId] = set()

        def dfs(node: ConceptId) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False

            visited.add(node)
            stack.add(node)

            for neighbor in graph.get(node, []):
                if dfs(neighbor):
                    return True

            stack.remove(node)
            return False

        if dfs(target_concept_id):
            raise CyclicPrerequisiteError(
                f"Adding prerequisite {new_prerequisite_id} creates a cycle."
            )
