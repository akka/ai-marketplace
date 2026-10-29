# Diagrams: [FEATURE]
<!-- visualize-source: plan.md sha256=[PLAN_SHA256] spec.md sha256=[SPEC_SHA256] -->

**Feature**: [FEATURE] | **Plan**: [link to plan.md]

## Color Conventions

Use only the colors whose flow types exist in this feature. Do not invent
flow categories to justify using a color.

| Flow Type | Color | Hex |
|-----------|-------|-----|
| Submission / happy-path | blue | `#2196F3` |
| Validation / processing | amber | `#FF9800` |
| Safety / blocking / rejection | red | `#F44336` |
| Human-review / approval (HITL) | purple | `#9C27B0` |
| Routing / delivery / success | green | `#4CAF50` |
| Error / failure | crimson | `#B71C1C` |

## External / Out-of-Scope Systems

- Wrap external actors and systems in a subgraph labelled "External" or "Out of Scope"
- Style every external node with a dashed border:
    `style NodeId stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333`
- Use dotted arrows (`-.->`) for ALL connections to/from external nodes
- Do NOT use dotted arrows for internal indirect connections — use a comment instead
  (this disambiguates "external" from "event-driven internal")

## Message Broker / Topic Nodes

Mandatory when `@Produce.ToTopic` or `@Consume.FromTopic` is used:

- Represent every topic as an explicit named node — NEVER collapse topic into an arrow label
- Flowchart shape: cylinder → `TOPIC_ID[(topic-name)]`
- Flowchart grouping: place in a subgraph labelled "Message Broker" or "Topics"
- Flowchart style: `fill:#FFF9C4,stroke:#F9A825,color:#333`
- Producer edge: solid arrow `-->` labelled "publish"
- Consumer edge: solid arrow `-->` labelled "subscribe"
- Sequence diagram: declare as participant, e.g. `participant T as validated-content`
  - Producer sends: `->> T: publish(Payload)`
  - Consumer reads: `T -->> Consumer: message`

## Sequence Numbers

Add ①②③… on flowchart edge labels to show execution order.
Use `linkStyle N stroke:#RRGGBB,stroke-width:2px` to color edges by flow.
`linkStyle` indices are 0-based and match the order edges are declared in the diagram.

---

## 1. Component Dependencies

<!--
  Flowchart showing every component and how they depend on / call each other.
  - One node per class/component (use short names)
  - Group by package with subgraph blocks
  - Color edges by flow type (see Color Conventions above)
  - Sequence numbers ①②… on connections show runtime call order
  - External / out-of-scope: dashed border node + dotted arrow (-.->)
  - Internal indirect / event-driven: solid arrow with an italic comment label
-->

```mermaid
flowchart TD
    %% Replace with real component graph for this feature

    subgraph ext["External / Out of Scope"]
        Client([Client])
        DS[(Downstream System)]
    end

    subgraph api["API Layer"]
        EP[YourEndpoint]
    end

    subgraph application["Application Layer"]
        WF[YourWorkflow]
        AG[YourAgent]
        VW[YourView]
    end

    Client -.->|"① POST /resource"| EP
    EP     -->|"② start"| WF
    WF     -->|"③ invoke"| AG
    WF     -->|"④ projects to"| VW
    WF    -.->|"⑤ deliver"| DS

    linkStyle 0,1 stroke:#2196F3,stroke-width:2px
    linkStyle 2,3 stroke:#FF9800,stroke-width:2px
    linkStyle 4   stroke:#4CAF50,stroke-width:2px

    style Client stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
    style DS     stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333
```

---

## 2. Sequence Diagram

<!--
  End-to-end sequence diagram showing the primary flows.
  - Use `rect rgb(R,G,B)` blocks to color each flow section.
  - Match colors to Color Conventions above.
  - Include at least: happy path, HITL / review flow (if applicable), and one error path.
  - Label participants with short role names.
  - Valid arrow types: ->> (solid), -->> (dotted async), -> (solid open), --> (dotted open)
  - Do NOT use -.>> — it is invalid in Mermaid sequence diagrams. Use -->> for dotted arrows.
-->

```mermaid
sequenceDiagram
    %% Replace with real sequence for this feature

    participant C  as Client
    participant EP as YourEndpoint
    participant WF as YourWorkflow
    participant AG as YourAgent
    participant DS as Downstream

    rect rgb(33,150,243)
        Note over C,WF: Submission Flow
        C  ->> EP: POST /resource {payload}
        EP ->> WF: start(request)
        WF -->> EP: resourceId
        EP -->> C: 201 {resourceId, SUBMITTED}
    end

    rect rgb(255,152,0)
        Note over WF,AG: Processing Flow
        WF ->> AG: invoke(payload)
        AG -->> WF: AgentResult(passed=true, confidence=0.92)
    end

    rect rgb(76,175,80)
        Note over WF,DS: Delivery Flow
        WF ->> DS: deliver(payload, target)
        DS -->> WF: deliveryConfirmation
        WF -->> WF: status → COMPLETED
    end

    rect rgb(183,28,28)
        Note over WF,C: Error Path
        WF ->> AG: invoke(badPayload)
        AG -->> WF: GuardrailException
        WF -->> WF: status → FAILED
    end
```

---

## 3. Workflow State Machines

<!--
  INCLUDE ONLY if the feature uses one or more Akka Workflows.
  Remove this section entirely if no Workflow is used.

  REPEAT the subsection below once per Workflow class — one state machine per workflow.
  Title each subsection with the workflow class name: "### 3.N WorkflowClassName"

  Per diagram:
  - Show every status value as a node.
  - Color nodes by flow category (see Color Conventions above):
      Entry / initial state   → blue
      Processing states       → amber
      HITL / review states    → purple
      Terminal success        → green
      Terminal failure        → red/crimson
  - Label transitions with the trigger (step name or command).
  - Use ([text]) for start/end nodes, [text] for intermediate states.
-->

### 3.1 YourWorkflow

```mermaid
flowchart TD
    %% Replace with real workflow state machine — one block per Workflow class

    START([START]) --> STATE_A

    STATE_A --> STATE_B
    STATE_B --> STATE_C
    STATE_C -->|"low confidence"| AWAITING_REVIEW
    STATE_C -->|"high confidence"| STATE_D
    AWAITING_REVIEW -->|"APPROVE"| STATE_D
    AWAITING_REVIEW -->|"REJECT"| REJECTED

    STATE_D --> COMPLETED

    STATE_A --> FAILED
    STATE_B --> FAILED
    STATE_C --> FAILED
    STATE_D --> FAILED

    style START           fill:#2196F3,color:#fff
    style STATE_A         fill:#FF9800,color:#fff
    style STATE_B         fill:#FF9800,color:#fff
    style STATE_C         fill:#FF9800,color:#fff
    style AWAITING_REVIEW fill:#9C27B0,color:#fff
    style STATE_D         fill:#FF9800,color:#fff
    style COMPLETED       fill:#4CAF50,color:#fff
    style REJECTED        fill:#B71C1C,color:#fff
    style FAILED          fill:#B71C1C,color:#fff
```
