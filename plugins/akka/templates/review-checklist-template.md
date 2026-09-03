# Akka SDK Review Checklist

Each check is tagged with a severity:

- **[CRITICAL]** — Can cause runtime failures, data corruption, security
  vulnerabilities, or silent data loss. Must be fixed.
- **[RECOMMENDED]** — Convention or best practice that improves
  maintainability, readability, or consistency. Won't break anything if
  skipped, but following it is advised.
- **[DESIGN]** — Higher-level design concern affecting performance,
  scalability, or maintainability. Requires understanding the domain and
  usage patterns. Report as observations with reasoning, not pass/fail.

Reference: Akka SDK AI coding assistant guidelines, Developer best practices.

## A. Serialization & State Integrity

- A1 [CRITICAL]: `@TypeName` values are stable (not changed after initial deployment — check git history if accessible) — changing a value after data is persisted corrupts stored data. Ref: serialization docs — type name is used to deserialize persisted payloads.
- A2 [CRITICAL]: `applyEvent` is a pure function — transfers event data to state only; never throws, never validates — throwing in `applyEvent` breaks event replay and makes the entity unrecoverable. Ref: guidelines — "should be a pure function...should never fail."
- A3 [CRITICAL]: `emptyState()` does not call `commandContext()` — entity ID accessed via injected `EventSourcedEntityContext` if needed — `commandContext()` is not available during entity initialization.

## B. Endpoints & Security

- B1 [CRITICAL]: `@Acl` annotations are not overly permissive — check for `Acl.Principal.ALL` or `Acl.Principal.INTERNET` on endpoints that handle sensitive operations or should be internal-only. Internal endpoints should use `@Acl(allow = @Acl.Matcher(service = "*"))` which allows other services but blocks internet access. Ref: access-control docs.
- B2 [CRITICAL]: Endpoint classes have no `@Component` annotation — causes runtime error; use `@HttpEndpoint` / `@GrpcEndpoint` only. Ref: guidelines.

## C. Workflows

- C1 [CRITICAL]: Overrides `settings()` returning `WorkflowSettings` — no deprecated `definition()` override. Ref: workflows docs, guidelines.
- C2 [CRITICAL]: Step methods return `StepEffect` and call `stepEffects()`; command handlers return `Effect<T>` and call `effects()` — mixing these up causes wrong behavior or compilation errors. Ref: workflows docs.
- C3 [CRITICAL]: Steps calling LLM agents have per-step timeout >= 60 seconds — default step timeout is 5 seconds, which is too short for LLM calls. Ref: workflows docs, guidelines.

## D. Agents

- D1 [CRITICAL]: Agent class is stateless — no mutable fields — mutable state causes race conditions across concurrent requests. Ref: guidelines — "Agent classes should be stateless."

## E. Views

- E1 [CRITICAL]: `@Consume.*` annotation is on the inner `TableUpdater` subclass, NOT on the outer `View` class — wrong placement causes the view to not function. Ref: SDK samples.
- E2 [CRITICAL]: ESE views use `onEvent(Event)`, KVE views use `onUpdate(State)` — wrong handler type means the view never populates. Ref: views docs.
- E3 [CRITICAL]: Multi-row query methods return a wrapper record with `List<Row> items` and use `SELECT * AS items` — returning `QueryEffect<List<Row>>` directly is not supported. Ref: guidelines, views docs.
- E4 [CRITICAL]: View row fields are never null — views struggle with null values in queries and projections. Use `Optional<T>` for fields that may be absent, or ensure `TableUpdater` handlers set explicit defaults. See also J2. Ref: views docs.

## F. Error Handling & ComponentClient

Reference: Errors and failures, Component and service calls.

- F1 [CRITICAL]: Error handling in entities uses `effects().error()` or throws `CommandException` (or subtypes) — other exception types are not serializable across nodes and become opaque 500 errors. Ref: errors-and-failures docs.
- F2 [CRITICAL]: Custom `CommandException` subtypes used for structured error handling are `static` inner classes — non-static inner classes are not serializable. Ref: errors-and-failures docs.

## G. Payload & State Size

Reference: Developer best practices — Payload and state size.

- G1 [CRITICAL]: Entity/workflow request and response payloads are under 1 MB — exceeding this fails cluster replication. Ref: dev-best-practices docs — hard limit table.
- G2 [CRITICAL]: Entity state and events stay under 1 MB — larger state becomes "isolated" and cannot replicate across regions or be consumed by other services. Ref: dev-best-practices docs — "1 MB Replication Ceiling."
- G3 [CRITICAL]: Timed action parameters are under 1 KB — use entity ID references for larger payloads. Ref: dev-best-practices docs — hard limit table.
- G4 [CRITICAL]: No `byte[]`, `Base64`-encoded strings, or large text blobs stored in entity state, events, or workflow state — store large assets in an external blob store and keep only a reference (URL/ID) in state. Ref: dev-best-practices docs — "Large Assets."

## H. Code Quality & Safety

- H1 [CRITICAL]: No blocking I/O in entity command handlers, entity event handlers, or workflow step handlers — blocks the component thread, causing timeouts and degraded throughput.
- H2 [CRITICAL]: No shared mutable state in components — causes race conditions and data corruption.
- H3 [CRITICAL]: No hardcoded secrets, API keys, or endpoints in source files — security vulnerability.
- H4 [CRITICAL]: HTTP calls use the SDK-provided client — inject `akka.javasdk.http.HttpClientProvider` in the constructor and reuse the `httpClientFor(...)` result; no hand-built HTTP clients (`HttpClient.newHttpClient()`, `HttpClient.newBuilder()`, `new OkHttpClient()`, Apache `HttpClients.create*`) in service code. Every hand-built client owns its own selector thread and executor; created per request they accumulate until the service runs out of threads. The SDK client also handles routing, encryption, and authentication for service-to-service calls. Grep the whole codebase for this check. Ref: component-and-service-calls docs.

## I. PII & Data Sanitization

Reference: Data sanitization documentation.

- I1 [CRITICAL]: No logging of entity state or events that may contain PII without sanitization — check for `logger.info/debug/warn/error` calls that log full state objects, command payloads, or event payloads containing user data.
- I2 [CRITICAL]: No PII in exception messages — `effects().error()` messages and thrown exceptions do not include user-provided data verbatim (e.g., `"Invalid email: " + email`).
- I3 [CRITICAL]: Agent prompts do not embed raw PII — user data passed to agent system/user messages should go through `Sanitizer#sanitize` or be covered by the runtime's automatic sanitization.
- I4 [CRITICAL]: Endpoint error responses do not echo back PII — e.g., `"User john@example.com not found"` should be `"User not found"`.

## J. Serialization Conventions

- J1 [RECOMMENDED]: All sealed interface subtypes (ESE events, workflow step input variants) have `@TypeName("...")` on each variant record — essential for maintainability and correct routing. Note: plain records (entity state, KVE state, workflow state) do NOT need `@TypeName` — it is only required for sealed interface subtypes where the runtime must distinguish between variants. Ref: serialization docs — type name, event-sourced-entities docs, views docs, ai-coding-assistant-guidelines.
- J2 [RECOMMENDED]: Optional fields use `Optional<T>` rather than nullable fields.
- J3 [RECOMMENDED]: State transitions return new record instances via immutable `with*()` methods.
- J4 [RECOMMENDED]: When using Protobuf serialization instead of Jackson, Event Sourced Entity and Consumer classes have the `@ProtoEventTypes` annotation listing all event types — unlisted message types will fail the stream and stall the consumer/view until a supporting version is deployed. Ref: serialization docs — protobuf serialization.

## K. Architecture & Conventions

- K1 [RECOMMENDED]: DDD 3-layer structure exists (`domain/`, `application/`, `api/` or equivalent with clear roles)
- K2 [RECOMMENDED]: `domain/` package has zero `akka.*` imports
- K3 [RECOMMENDED]: Business logic (validation, calculations, state transitions) lives in domain objects, not in entity command handlers
- K4 [RECOMMENDED]: Naming conventions followed: `{Purpose}Agent`, `{Domain}Entity`, `{Domain}{ByField}View`, `{Process}Workflow`, `{Domain}Endpoint`, `{Domain}Consumer`
- K5 [RECOMMENDED]: Commands use imperative naming (e.g., `ShoppingCartEntity.Checkout`)
- K6 [RECOMMENDED]: Events represent facts in past tense (`TransferInitiated`, `ItemAdded`), not commands (`DoTransfer`, `AddItem`)
- K7 [RECOMMENDED]: View row records are public, named `Entry` or `{Domain}Entry`
- K8 [RECOMMENDED]: Read-only command handlers (queries that don't change state) use `ReadOnlyEffect` — makes intent explicit and prepares the application for multi-region deployments where read-only effects can be served locally. Ref: guidelines.

## L. Endpoint Conventions

- L1 [RECOMMENDED]: Every HTTP/gRPC endpoint class has an `@Acl` annotation — without `@Acl`, Akka denies all requests by default, making the endpoint unreachable.
- L2 [RECOMMENDED]: Response types are API-specific (in `api/` package) — uses `toApi` conversion methods rather than exposing domain types directly
- L3 [RECOMMENDED]: Synchronous style — returns response directly via `.invoke()`, not `CompletionStage` / `.invokeAsync()`
- L4 [RECOMMENDED]: Methods that create or update state return `HttpResponses.created()` or `HttpResponses.ok()` using `akka.javasdk.http.HttpResponses` factory
- L5 [RECOMMENDED]: When accessing request context (headers, JWT claims), prefer extending `AbstractHttpEndpoint` / `AbstractGrpcEndpoint` and using `requestContext()` method — constructor injection of `RequestContext` also works
- L6 [RECOMMENDED]: Void-like entity command handlers return `akka.Done` on success, `effects().error()` for validation

## M. Workflow & Agent Conventions

- M1 [RECOMMENDED]: Failing steps have compensation via `.failoverTo(WorkflowClass::compensateStep)` — not all workflows need compensation, but saga-style workflows should have it
- M2 [RECOMMENDED]: AI steps have explicit retry limits (e.g., `maxRetries(2)`) to avoid excessive LLM costs
- M3 [RECOMMENDED]: Step transitions use method references (`WorkflowClass::step`), not string names
- M4 [RECOMMENDED]: Long-running workflows have a safety-net timeout or monitor step to detect being stuck
- M5 [RECOMMENDED]: Session ID strategy is explicit — UUID for new interactions, workflow ID for orchestrated flows
- M6 [RECOMMENDED]: `MemoryProvider` configured intentionally per agent (`.none()`, `.limitedWindow()`, etc.)
- M7 [RECOMMENDED]: Default model defined in config (not hardcoded per-request)
- M8 [RECOMMENDED]: Structured responses use `responseConformsTo(Class)` (preferred over `responseAs`)
- M9 [RECOMMENDED]: Agents with JSON parsing or tool calls have `.onFailure(ex -> fallback)` error handling
- M10 [RECOMMENDED]: Workflow steps that invoke an Agent have a sufficient timeout — either set a per-step `stepTimeout` (>= 60 seconds) or increase the `defaultStepTimeout` in workflow settings. Default 5-second timeout is insufficient for LLM round-trips. Ref: workflows docs, guidelines.

## N. Consumer & Idempotency Conventions

- N1 [RECOMMENDED]: Commands that mutate state carry a `commandId` deduplication token where duplicate delivery is possible — needed when callers may retry. Ref: dev-best-practices docs.
- N2 [RECOMMENDED]: If command deduplication is used, the processed command ID collection in entity state is bounded (e.g., last 1000 IDs) to prevent unbounded state growth. Ref: dev-best-practices docs.
- N3 [RECOMMENDED]: Consumer operations are inherently idempotent (full-replacement updates) OR events carry pre-calculated absolute values (event enrichment). Ref: dev-best-practices docs.
- N4 [RECOMMENDED]: Consumers that call external services use deterministic deduplication tokens — e.g., `UUID.nameUUIDFromBytes((entityId + sequenceNumber).getBytes())`. Ref: dev-best-practices docs.
- N5 [RECOMMENDED]: Workflow compensation steps are infallible — they handle the case where the original operation never succeeded.
- N6 [RECOMMENDED]: KVE/Workflow consumers use `@DeleteHandler` when custom deletion behavior is needed (automatic row deletion is the default). Ref: views docs.
- N7 [RECOMMENDED]: When large assets are needed at runtime, they are loaded just-in-time — via an injected storage client or `ContentLoader` for agent multimodal content.
- N8 [RECOMMENDED]: No events embedding entire entity state (fat events) — only changed data or enrichment fields needed by downstream consumers.
- N9 [RECOMMENDED]: If the service handles PII, sanitization is enabled in `application.conf` (`akka.javasdk.sanitization`). Ref: sanitization docs.

## O. Testing Conventions

- O1 [RECOMMENDED]: Entity tests use `EventSourcedTestKit.of("id", EntityClass::new)` with explicit entity IDs
- O2 [RECOMMENDED]: KVE tests use `KeyValueEntityTestKit`, timed action tests use `TimedActionTestKit`
- O3 [RECOMMENDED]: View tests use event publishing + `Awaitility.await()` for async projection polling
- O4 [RECOMMENDED]: Endpoint integration tests use `httpClient` (not `componentClient`)
- O5 [RECOMMENDED]: Agent tests use `TestModelProvider` registered via `testKitSettings()` — no real LLM calls
- O6 [RECOMMENDED]: Agent mock responses use `JsonSupport.encodeToString(mockObject)` (not raw JSON strings)
- O7 [RECOMMENDED]: Integration test class names end with `IntegrationTest` suffix

## P. Error Handling Conventions

- P1 [RECOMMENDED]: `ComponentClient` call results are handled — return values from `.invoke()` are checked or used, not silently discarded.
- P2 [RECOMMENDED]: `CommandException` from `ComponentClient` calls is caught and mapped to appropriate HTTP responses in endpoints — the default behavior surfaces a raw 400 with the error message.
- P3 [RECOMMENDED]: Unexpected exceptions from component calls are handled gracefully — by default they become generic 500 errors with only a correlation ID.

## Q. Design Review

These checks assess higher-level design decisions that affect performance,
scalability, and maintainability. They require understanding the domain and
intended usage patterns — not just reading code mechanically.

**Entity design**

- Q1 [DESIGN]: No hot entity / God entity — check for entities that accumulate events from many different sources or that every request touches (e.g., a global counter, a singleton aggregator). Entities process commands sequentially per ID; a single high-traffic entity becomes a throughput bottleneck.
- Q2 [DESIGN]: Entity granularity is appropriate — entities are not too coarse (one entity per tenant holding all data, leading to large state and contention) or too fine (one entity per trivial change, adding overhead). Granularity should match the consistency boundary.
- Q3 [DESIGN]: Entity state does not grow without bound — check for lists, maps, or collections in entity state that only append and never trim or evict. Unbounded growth eventually hits the 10 MB state limit or degrades serialization performance.

**Event design**

- Q4 [DESIGN]: Events are right-sized — not too chatty (dozens of tiny events per operation, increasing replay overhead) and not too coarse (one event capturing many unrelated changes, preventing consumers from reacting selectively).

**Workflow design**

- Q5 [DESIGN]: Independent workflow steps are executed in parallel where possible — check for sequential steps that have no data dependency on each other (e.g., calling 3 independent validation agents one after another instead of concurrently).
- Q6 [DESIGN]: Workflows are appropriately scoped — a single workflow should not orchestrate too many unrelated concerns. Large workflows should be decomposed into smaller, composable workflows.
- Q7 [DESIGN]: Workflows are used where needed — check for workflows that perform no external calls or coordination and could be a simple entity state machine instead. Workflows add overhead that isn't justified for purely local state transitions.

**View & query design**

- Q8 [DESIGN]: Common query patterns have supporting views — if callers are reading entities one by one to assemble a list or search result, a view should provide that query directly.
- Q9 [DESIGN]: Views are not over-indexed — too many views consuming events from the same entity add processing overhead for every event. Each view should serve a distinct query need.

**Component interaction design**

- Q10 [DESIGN]: No deep synchronous call chains — check for patterns where an endpoint calls entity A, which triggers entity B, which triggers entity C. Deep chains increase latency and fragility. Prefer async decoupling via topics/consumers for non-essential downstream effects.
- Q11 [DESIGN]: No circular component dependencies — component A should not call B which calls back to A (directly or transitively). This creates deadlock risk and tight coupling.
- Q12 [DESIGN]: Consumers delegate complex work to workflows — consumers that make multiple external calls or complex multi-step transformations per event should delegate to a workflow for durability and retry guarantees, rather than doing it all inline.
- Q13 [DESIGN]: Aggregate boundaries are clear — related state that must be consistent together lives within the same entity. State spread across multiple entities with no clear boundary leads to complex distributed transactions or eventual consistency issues that may not be intentional.

**Component selection**

Reference: "Choosing a component type" in `akka-context/sdk/components/index.html.md`; its decision helpers carry stable anchors (`cs1-*` through `cs11-*`) cited below. Also the Component Architecture table in plan.md (if present).

- Q14 [DESIGN]: Component choices match the plan's Component Architecture table and the decision guide — close-call choices are justified against the rejected alternative; deviations from the plan are recorded with a reason.
- Q15 [DESIGN]: Entity type fits the need — no Key Value Entity with a hand-maintained history list (needs Event Sourced); no Event Sourced Entity whose only event is a whole-state `StateChanged` (Key Value is enough); audit and ledger requirements are event-sourced. Ref: `cs1-entity-type`.
- Q16 [DESIGN]: No View whose only query is a lookup by entity id (read the entity directly via `ComponentClient`); no read-your-own-write through a View in the same request that made the write. Ref: `cs2-view-or-entity-read`.
- Q17 [DESIGN]: No single-step Workflow that only calls one component (use a Consumer or a direct call); no consumer chain forming an implicit multi-step process that needs compensation or a status (use a Workflow). Ref: `cs3-workflow-or-choreography`, `cs4-consumer-or-direct-call`.
- Q18 [DESIGN]: State is durable only where required — entity/workflow state is reserved for values that must survive restarts, be audited, or drive reactions; values derivable from their inputs are computed per request; nothing is a component that could be a plain domain class. Ref: `cs8-durable-or-in-memory`, `cs10-component-or-plain-class`.
- Q19 [DESIGN]: No HTTP calls from the service to its own endpoints (use `ComponentClient`); outbound third-party calls are placed by failure semantics — workflow step (durable, retried), consumer (reactive, idempotent), endpoint (request-scoped), or agent tool — never inside entities. Ref: `cs9-in-process-or-network`, `cs11-third-party-calls`.

## R. Multi-Region Readiness (optional section)

Reference: Multi-region operations, Regions setup (selecting primary), State model, Views,
Consuming and producing, Timers, Developer best practices.

**Applicability: this section is opt-in.** Most Akka services run in a single region, where
none of the risks below exist. Run Section R only when multi-region deployment is confirmed;
otherwise skip it and say so in one line. Never infer multi-region deployment from the code
alone, and never raise an R finding as a failure on a project whose region topology you could
not confirm. The review command defines the gating signals.

**Primary selection mode.** Several checks depend on the mode, set per service in the service
descriptor (`replication.replicatedRead.primarySelectionMode`):

- `request-region` (the runtime default): each entity instance selects its primary where its
  writes occur. A write in a non-primary region moves the primary there.
- `pinned-region`: one project-wide primary. Writes in other regions are forwarded to it.

Workflows always keep their primary in the region that created them, in both modes. A third
mode, `none`, rejects all writes; it is only a transition step between the other two. Find the
mode in the service descriptor if the project has one. If it cannot be found, review against
`request-region` and state that assumption. If descriptors in the repository set different
modes, review against each mode that is used in production and mark mode-specific findings with
the mode.

Two checks elsewhere already cover multi-region concerns and are NOT repeated here: **G2**
(1 MB ceiling; oversized state becomes "isolated" and never replicates) and **K8**
(`ReadOnlyEffect` on read-only handlers). R6 below extends K8 with what a plain `Effect` does
in each mode.

**Replication safety**

- R1 [CRITICAL]: Consumer side effects are region-safe. A Consumer of entity events runs in EVERY region and processes every replicated event there, so a side effect fires once per region. This includes calls to other services, emails, writes to an external store, `@Produce.ToTopic` publishes, and non-idempotent writes to entities of the same service (for example a counter incremented per event). A region added later processes the full event history, so unguarded side effects also fire again for every past event. For Consumers of entity events, guard side effects with `messageContext().hasLocalOrigin()`, or make them idempotent with a deterministic token. `hasLocalOrigin()` is NOT a guard for Consumers of topics or service streams (`@Consume.FromTopic`, `@Consume.FromServiceStream`): those messages carry no origin region, and `hasLocalOrigin()` returns true for them in every region. For topics, rely on the broker's regional or global scope (R13) or on idempotency. For service streams, make the side effect idempotent. A View updating its own table in every region is correct: do not flag it. Extends N3, N4. Ref: consuming-producing docs, multi-region replication.
- R2 [CRITICAL]: `applyEvent` and View `TableUpdater` handlers compute no region-local values. Each region applies the replicated events itself, so a clock, random value, UUID, external lookup or region value (`selfRegion()`, `hasLocalOrigin()`, `originRegion()` used to compute state) in these handlers gives different state or rows in each region. Capture such values in the command handler and store them in the event. Extends A2. This does NOT apply to Key Value Entity command handlers: a KVE replicates its state, so `Instant.now()` or `UUID.randomUUID()` there is fine. Ref: state-model docs; views docs, multi-region replication.
- R3 [CRITICAL]: Recorded data-residency requirements use replication filters. State replicates to all enabled regions by default, including regions added later. If the spec, constitution or user input records that some data must not leave a region, the entity uses `@EnableReplicationFilter` and sets the filter with `updateReplicationFilter` (Event Sourced and Key Value Entities). Views in excluded regions receive no rows for filtered entities. If no such requirement is recorded, report N/A: do not infer one from the code. Ref: event-sourced-entities and key-value-entities docs, replication filters.
- R4 [CRITICAL]: Timers are not scheduled from code that runs in every region. Timers are region-local and not replicated. A Consumer that calls `timers().createSingleTimer(...)` registers a separate timer in each region, and each one fires; the same timer name does not deduplicate across regions. Guard the scheduling with `messageContext().hasLocalOrigin()`, or make the timer's target idempotent. A timer scheduled from an endpoint, a Workflow step or a TimedAction is registered once, in the region that ran that code. Extends R1.
- R5 [CRITICAL]: Under `request-region`, write paths tolerate a failed primary selection. The first write to a new entity, and every write that moves an entity's primary, needs an acknowledgement from every other region within 5 seconds. While any region is restarting or unreachable, these writes fail in all regions with a generic `Unexpected error` (HTTP 500 to an HTTP caller, an error to a component client). The runtime does not retry them. This happens for minutes after every deploy, rolling restart or region add, even with more than one instance per region. Writes to an entity whose primary is already the local region are not affected. Check the callers of Event Sourced and Key Value Entity writes that may create an entity or come from more than one region: endpoints retry these errors with backoff or return a retryable status, and the commands are safe to retry (a retried create may meet "already exists"). A Consumer's failed message is redelivered, so its commands must be idempotent (N3). A Workflow step retries per its recovery strategy: check that a strategy with few retries does not fail over to compensation for this transient error. Otherwise, use `pinned-region` (R11). Not applicable under `pinned-region`. Ref: regions/setup docs, "all regions must be available when the first write request is made".

**Consistency and routing**

- R6 [RECOMMENDED]: The `ReadOnlyEffect` / `Effect` choice on read paths matches the primary selection mode. `ReadOnlyEffect` (K8) is served from the local region and may be stale. A plain `Effect` counts as a write: under `pinned-region` it is forwarded to the primary, and under `request-region` it moves the primary to the local region, so the next write elsewhere must move it back and is exposed to R5. Use a plain `Effect` on a read only where the read must observe the latest write, and note why in the code. Flag read handlers that return a plain `Effect` with no stated consistency need.
- R7 [RECOMMENDED]: Write-then-read flows tolerate replication lag. Replication is asynchronous: tens of milliseconds between nearby regions, longer when the inter-region network degrades. Endpoint and workflow logic does not assume that an immediate `ReadOnlyEffect` read in another region returns the value just written. Either read in the region that wrote, use a plain `Effect` (R6), or handle eventual consistency explicitly.
- R8 [RECOMMENDED]: Timeouts account for cross-region hops. Under `pinned-region`, writes from non-primary regions are forwarded to the primary; under `request-region`, a write that moves the primary waits for the other regions (R5); Workflow commands are forwarded to the creating region (R9). Workflow step timeouts and `ComponentClient` call expectations allow for inter-region round-trips, not only local latency. Under `request-region`, a step that creates an entity needs a timeout above 5 seconds plus the round-trip, so that the R5 error arrives before the step times out. See also C3, M10.
- R9 [RECOMMENDED]: Workflows are started in the region where their commands arrive. A Workflow's primary stays in the region that created it, in both modes. Commands sent to it from another region are forwarded there, pay the cross-region round-trip, and fail while that region is unavailable. Pause timeouts and step timers fire only in the creating region. Status and other read-only handlers return `ReadOnlyEffect` so they are served locally.
- R10 [RECOMMENDED]: An entity is not written concurrently from more than one region under `request-region`. Code signal: a constant entity ID written from a component that runs in every region (a Consumer, an endpoint served in every region, a TimedAction), for example a global counter or a heartbeat entity. Each write from the other region moves the primary back and forth, and concurrent writes then fail with the R5 error; on a two-region test, more than half of such writes failed. Key such entities by region, route writes for one entity to one region (for example by user home region), or use `pinned-region`. The SDK has no multi-writer (CRDT) entity type.

**Design**

- R11 [DESIGN]: The primary selection mode is set explicitly and fits the access pattern. The runtime defaults to `request-region` when the service descriptor has no `replication` block, while `akka project settings down-region` treats such a service as `pinned-region`, so the effective mode is easy to misread. `request-region` suits geo-homed data written from one region per entity; `pinned-region` suits controlled failover and entities written from many regions, and avoids R5. Confirm the descriptor states the mode and that it matches how users write the data. Ref: regions/setup docs, selecting primary.
- R12 [DESIGN]: No single write-hot region under `pinned-region`. With a pinned primary, every write for every entity is handled in one region. Check that write volume and latency from distant regions are acceptable, or that `request-region` suits better.
- R13 [DESIGN]: Broker topic scope (regional or global) is intentional. A Consumer or View reading from a broker topic may consume in every region or in just one, depending on how the broker is configured. Confirm the configuration matches the intended once-per-region or once-overall processing. Ref: consuming-producing docs, multi-region replication.
- R14 [DESIGN]: Adding a region later is planned for. A new region serves requests before its data has been copied: reads return empty state and "not found" for a short time after it reports Ready. Its Consumers process the full event history (R1), its Views are rebuilt, pending timers are not copied to it, and routes created while the project had one region keep that region's hostname. Confirm the design tolerates this, or document the steps for adding a region.
- R15 [DESIGN]: Long-lived timers tolerate the loss of their region. Pending timers are durable within their own region but are not replicated, so they do not fail over: if that region is lost, they fire only when it returns. Workflow pause timeouts and step timeouts are such timers, in the creating region. For flows that depend on a timer firing hours or days later (reminders, long workflow pauses, deadlines), confirm the design can recover (for example a sweeper or a reconciliation view that re-establishes missed deadlines), or accept the exposure explicitly. See also R4.
