import json

from typing import Any

from utils.database import get_connection


ALLOWED_RELATIONSHIP_TYPES = {
    "prerequisite",
    "depends_on",
    "related",
    "part_of",
}


def validate_graph_data(
    graph_data: dict[str, Any],
) -> None:
    """
    Validates the structure of an AI-generated knowledge graph.
    """

    if not isinstance(graph_data, dict):
        raise ValueError("graph_data must be a dictionary")

    concepts = graph_data.get("concepts")
    relationships = graph_data.get("relationships", [])

    if not isinstance(concepts, list):
        raise ValueError(
            "graph_data['concepts'] must be a list"
        )

    if not concepts:
        raise ValueError(
            "Knowledge graph must contain at least one concept"
        )

    if not isinstance(relationships, list):
        raise ValueError(
            "graph_data['relationships'] must be a list"
        )

    concept_keys = set()

    for concept in concepts:
        if not isinstance(concept, dict):
            raise ValueError(
                "Each concept must be a dictionary"
            )

        concept_key = concept.get("concept_key")
        name = concept.get("name")

        if not concept_key or not isinstance(
            concept_key,
            str,
        ):
            raise ValueError(
                "Every concept needs a valid concept_key"
            )

        if not name or not isinstance(name, str):
            raise ValueError(
                f"Concept {concept_key} must have a valid name"
            )

        if concept_key in concept_keys:
            raise ValueError(
                f"Duplicate concept_key found: {concept_key}"
            )

        concept_keys.add(concept_key)

    for relationship in relationships:
        if not isinstance(relationship, dict):
            raise ValueError(
                "Each relationship must be a dictionary"
            )

        from_key = relationship.get("from_concept")
        to_key = relationship.get("to_concept")
        relationship_type = relationship.get(
            "relationship_type"
        )

        if from_key not in concept_keys:
            raise ValueError(
                f"Unknown from_concept: {from_key}"
            )

        if to_key not in concept_keys:
            raise ValueError(
                f"Unknown to_concept: {to_key}"
            )

        if relationship_type not in ALLOWED_RELATIONSHIP_TYPES:
            raise ValueError(
                f"Invalid relationship type: {relationship_type}"
            )

        if from_key == to_key:
            raise ValueError(
                f"Self relationship is not allowed: {from_key}"
            )

    validate_no_prerequisite_cycle(graph_data)


def validate_no_prerequisite_cycle(
    graph_data: dict[str, Any],
) -> None:
    """
    Detects cycles among prerequisite relationships.

    A prerequisite graph must be a DAG:
    Directed Acyclic Graph.
    """

    concepts = graph_data["concepts"]
    relationships = graph_data.get("relationships", [])

    concept_keys = {
        concept["concept_key"]
        for concept in concepts
    }

    adjacency = {
        concept_key: []
        for concept_key in concept_keys
    }

    indegree = {
        concept_key: 0
        for concept_key in concept_keys
    }

    for relationship in relationships:
        if relationship["relationship_type"] not in {
            "prerequisite",
            "depends_on",
        }:
            continue

        from_key = relationship["from_concept"]
        to_key = relationship["to_concept"]

        adjacency[from_key].append(to_key)
        indegree[to_key] += 1

    queue = [
        concept_key
        for concept_key, degree in indegree.items()
        if degree == 0
    ]

    visited_count = 0

    while queue:
        current = queue.pop(0)
        visited_count += 1

        for neighbour in adjacency[current]:
            indegree[neighbour] -= 1

            if indegree[neighbour] == 0:
                queue.append(neighbour)

    if visited_count != len(concept_keys):
        raise ValueError(
            "Knowledge graph contains a prerequisite cycle"
        )


def save_knowledge_graph(
    graph_key: str,
    topic: str,
    subject: str,
    academic_level: str,
    graph_data: dict[str, Any],
    version: int = 1,
) -> int:
    """
    Validates and saves a complete knowledge graph.

    Returns:
        graph_id
    """

    graph_key = graph_key.strip()
    topic = topic.strip()
    subject = subject.strip()
    academic_level = academic_level.strip()

    if not graph_key:
        raise ValueError("graph_key cannot be empty")

    if not topic:
        raise ValueError("topic cannot be empty")

    if not subject:
        raise ValueError("subject cannot be empty")

    if not academic_level:
        raise ValueError(
            "academic_level cannot be empty"
        )

    validate_graph_data(graph_data)

    conn = get_connection()

    try:
        existing = conn.execute(
            """
            SELECT id
            FROM knowledge_graphs
            WHERE graph_key = ?
            """,
            (graph_key,),
        ).fetchone()

        if existing is not None:
            raise ValueError(
                f"Knowledge graph already exists: {graph_key}"
            )

        cursor = conn.execute(
            """
            INSERT INTO knowledge_graphs (
                graph_key,
                topic,
                subject,
                academic_level,
                graph_data,
                version,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'validated')
            """,
            (
                graph_key,
                topic,
                subject,
                academic_level,
                json.dumps(graph_data),
                version,
            ),
        )

        graph_id = cursor.lastrowid

        concept_id_by_key = {}

        for concept in graph_data["concepts"]:
            concept_cursor = conn.execute(
                """
                INSERT INTO concepts (
                    graph_id,
                    concept_key,
                    name,
                    description,
                    concept_type,
                    importance,
                    metadata
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    graph_id,
                    concept["concept_key"],
                    concept["name"],
                    concept.get("description", ""),
                    concept.get(
                        "concept_type",
                        "general",
                    ),
                    concept.get(
                        "importance",
                        0.5,
                    ),
                    json.dumps(
                        concept.get(
                            "metadata",
                            {},
                        )
                    ),
                ),
            )

            concept_id_by_key[
                concept["concept_key"]
            ] = concept_cursor.lastrowid

        for relationship in graph_data.get(
            "relationships",
            [],
        ):
            from_concept_id = concept_id_by_key[
                relationship["from_concept"]
            ]

            to_concept_id = concept_id_by_key[
                relationship["to_concept"]
            ]

            conn.execute(
                """
                INSERT INTO concept_relationships (
                    graph_id,
                    from_concept_id,
                    to_concept_id,
                    relationship_type,
                    confidence
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    graph_id,
                    from_concept_id,
                    to_concept_id,
                    relationship["relationship_type"],
                    relationship.get(
                        "confidence",
                        1.0,
                    ),
                ),
            )

        conn.commit()

        return graph_id

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_knowledge_graph(
    graph_id: int,
) -> dict[str, Any] | None:
    """
    Loads a graph and its concepts/relationships.
    """

    conn = get_connection()

    try:
        graph_row = conn.execute(
            """
            SELECT *
            FROM knowledge_graphs
            WHERE id = ?
            """,
            (graph_id,),
        ).fetchone()

        if graph_row is None:
            return None

        concept_rows = conn.execute(
            """
            SELECT *
            FROM concepts
            WHERE graph_id = ?
            ORDER BY id
            """,
            (graph_id,),
        ).fetchall()

        relationship_rows = conn.execute(
            """
            SELECT
                cr.id,
                cr.relationship_type,
                cr.confidence,
                fc.concept_key AS from_concept,
                tc.concept_key AS to_concept
            FROM concept_relationships cr
            JOIN concepts fc
                ON fc.id = cr.from_concept_id
            JOIN concepts tc
                ON tc.id = cr.to_concept_id
            WHERE cr.graph_id = ?
            ORDER BY cr.id
            """,
            (graph_id,),
        ).fetchall()

        return {
            "graph": dict(graph_row),
            "concepts": [
                dict(row)
                for row in concept_rows
            ],
            "relationships": [
                dict(row)
                for row in relationship_rows
            ],
        }

    finally:
        conn.close()


def get_graph_by_key(
    graph_key: str,
) -> dict[str, Any] | None:
    """
    Finds a graph by its unique graph key.
    """

    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT *
            FROM knowledge_graphs
            WHERE graph_key = ?
            """,
            (graph_key,),
        ).fetchone()

        if row is None:
            return None

        return dict(row)

    finally:
        conn.close()


def get_prerequisite_concepts(
    graph_id: int,
    concept_id: int,
) -> list[dict[str, Any]]:
    """
    Returns the direct prerequisite concepts
    required by a given concept.

    Relationship direction:

        prerequisite
              ↓
        target concept

    Example:

        Electric Field
              ↓
        Electric Flux

    Calling this function for Electric Flux
    returns Electric Field.
    """

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                prerequisite.id AS concept_id,
                prerequisite.concept_key,
                prerequisite.name,
                prerequisite.description,
                prerequisite.concept_type,
                prerequisite.importance,
                cr.relationship_type,
                cr.confidence
            FROM concept_relationships cr
            JOIN concepts prerequisite
                ON prerequisite.id = cr.from_concept_id
            JOIN concepts target
                ON target.id = cr.to_concept_id
            WHERE cr.graph_id = ?
              AND target.id = ?
              AND cr.relationship_type = 'prerequisite'
            ORDER BY cr.id
            """,
            (
                graph_id,
                concept_id,
            ),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        conn.close()


def get_dependent_concepts(
    graph_id: int,
    concept_id: int,
) -> list[dict[str, Any]]:
    """
    Returns the concepts that directly depend
    on the given concept.

    Example:

        Electric Field
              ↓
        Electric Flux

    Calling this function for Electric Field
    returns Electric Flux.
    """

    conn = get_connection()

    try:
        rows = conn.execute(
            """
            SELECT
                dependent.id AS concept_id,
                dependent.concept_key,
                dependent.name,
                dependent.description,
                dependent.concept_type,
                dependent.importance,
                cr.relationship_type,
                cr.confidence
            FROM concept_relationships cr
            JOIN concepts prerequisite
                ON prerequisite.id = cr.from_concept_id
            JOIN concepts dependent
                ON dependent.id = cr.to_concept_id
            WHERE cr.graph_id = ?
              AND prerequisite.id = ?
              AND cr.relationship_type = 'prerequisite'
            ORDER BY cr.id
            """,
            (
                graph_id,
                concept_id,
            ),
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        conn.close()