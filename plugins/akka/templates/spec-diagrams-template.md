# Spec Diagrams: [FEATURE]
<!-- visualize-source: spec.md sha256=[SPEC_SHA256] -->

**Feature**: [FEATURE] | **Spec**: [link to spec.md]

## Color Conventions

Use only the colors whose categories exist in this feature. Do not invent
categories to justify using a color.

| Category | Color | Hex |
|----------|-------|-----|
| Primary / P1 stories | blue | `#2196F3` |
| Secondary / P2 stories | amber | `#FF9800` |
| Tertiary / P3+ stories | green | `#4CAF50` |
| Human actor | green | `#4CAF50` |
| External / out-of-scope system | grey dashed | `#f5f5f5` + `stroke-dasharray:5 5,stroke:#999` |
| Terminal / failure state | red | `#F44336` |
| Error / failure state | crimson | `#B71C1C` |
| Review / decision point | purple | `#9C27B0` |

## External / Out-of-Scope Systems

- Wrap external actors and systems in a subgraph labelled "External" or "Out of Scope"
- Style every external node with a dashed border:
    `style NodeId stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333`
- Use dotted arrows (`-.->`) for ALL connections to/from external nodes

---

## 1. User Journey Map

<!--
  A flowchart showing the user stories as a journey.
  - Each user story is a node, labelled with its short title
  - Arrange top-to-bottom by priority (P1 at top)
  - Show dependencies between stories with arrows (e.g., P3 depends on P1 and P2)
  - Color nodes by priority tier
  - Use rounded boxes for stories: ([Story Title])
  - Add brief edge labels showing why the dependency exists
  - This is NOT a technical diagram — focus on user value and story relationships
-->

```mermaid
flowchart TD
    %% Replace with real user stories from spec.md

    S1([P1: Story Title])
    S2([P2: Story Title])
    S3([P3: Story Title])
    S4([P4: Story Title])

    S1 -->|"enables"| S2
    S1 -->|"enables"| S3
    S2 -->|"enables"| S4
    S3 -->|"enables"| S4

    style S1 fill:#2196F3,color:#fff
    style S2 fill:#FF9800,color:#fff
    style S3 fill:#4CAF50,color:#fff
    style S4 fill:#4CAF50,color:#fff
```

---

## 2. Actor–Goal Overview

<!--
  A flowchart showing who interacts with the system and what they want to achieve.
  - Identify actors from the user stories (submitter, reviewer, admin, etc.)
  - Show the system as a central node
  - Connect actors to their goals (derived from user stories)
  - Use rounded boxes for actors: ([Actor Name])
  - Use rectangles for goals: [Goal]
  - Use dashed borders for external/out-of-scope systems
  - This is a use-case-level view — no implementation details
-->

```mermaid
flowchart LR
    %% Replace with real actors and goals from spec.md

    subgraph actors["Actors"]
        A1([Actor 1])
        A2([Actor 2])
    end

    subgraph system["System"]
        G1[Goal 1]
        G2[Goal 2]
        G3[Goal 3]
    end

    subgraph ext["External / Out of Scope"]
        E1([External System])
    end

    A1 -->|"action"| G1
    A1 -->|"action"| G2
    A2 -->|"action"| G3
    G2 -.->|"notifies"| E1

    style A1 fill:#4CAF50,color:#fff
    style A2 fill:#4CAF50,color:#fff
    style G1 fill:#2196F3,color:#fff
    style G2 fill:#2196F3,color:#fff
    style G3 fill:#FF9800,color:#fff
    style E1 stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
```

---

## 3. Entity Relationship Map

<!--
  INCLUDE ONLY if the spec defines Key Entities.
  Remove this section entirely if no entities are described.

  A diagram showing the key entities and their relationships.
  - One node per entity from the Key Entities section
  - Show relationships and cardinality where described
  - Use simple labels (has, belongs to, produces, triggers)
  - Do NOT include database columns or types — keep it conceptual
  - Use stadium-shaped nodes for entities: ([Entity Name])
-->

```mermaid
flowchart TD
    %% Replace with real entities from spec.md Key Entities section

    E1([Entity 1])
    E2([Entity 2])
    E3([Entity 3])

    E1 -->|"has many"| E2
    E1 -->|"produces"| E3
```

---

## 4. Status Lifecycle

<!--
  INCLUDE ONLY if the spec describes a status lifecycle or state progression.
  Remove this section entirely if no lifecycle is described.

  A state diagram showing how the primary entity progresses through statuses.
  - Use the statuses exactly as named in the spec
  - Color terminal success states green, terminal failure states red
  - Color intermediate states amber
  - Color decision/review states purple
  - Label transitions with the trigger (what causes the transition)
  - Use ([text]) for start/end nodes, [text] for intermediate states
-->

```mermaid
flowchart TD
    %% Replace with real status lifecycle from spec.md

    START([Initial State]) --> STATE_A[State A]
    STATE_A --> STATE_B[State B]
    STATE_B -->|"condition met"| DONE([Success])
    STATE_B -->|"condition failed"| FAILED([Failed])

    style START fill:#2196F3,color:#fff
    style STATE_A fill:#FF9800,color:#fff
    style STATE_B fill:#FF9800,color:#fff
    style DONE fill:#4CAF50,color:#fff
    style FAILED fill:#F44336,color:#fff
```
