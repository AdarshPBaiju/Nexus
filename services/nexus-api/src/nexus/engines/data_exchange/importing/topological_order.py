"""
nexus.engines.data_exchange.importing.topological_order - Dependency graph resolver.
"""

from __future__ import annotations

from typing import Mapping, Sequence


class TopologicalImportResolver:
    """Computes dependency execution order for multi-entity import sets."""

    @classmethod
    def resolve_order(
        cls,
        dependencies: Mapping[str, Sequence[str]],
    ) -> list[str]:
        """
        Kahn's algorithm for topological sorting of entity import dependencies.
        dependencies map: entity -> list of prerequisites that must be imported first.
        """
        all_nodes = set(dependencies.keys())
        for prereqs in dependencies.values():
            all_nodes.update(prereqs)

        in_degree: dict[str, int] = dict.fromkeys(all_nodes, 0)
        adj_list: dict[str, list[str]] = {node: [] for node in all_nodes}

        for node, prereqs in dependencies.items():
            in_degree[node] = len(prereqs)
            for prereq in prereqs:
                adj_list[prereq].append(node)

        queue = [n for n, deg in in_degree.items() if deg == 0]
        order: list[str] = []

        while queue:
            curr = queue.pop(0)
            order.append(curr)
            for neighbor in adj_list[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(all_nodes):
            raise ValueError("Cyclic dependency detected in multi-entity import schema.")

        return order
