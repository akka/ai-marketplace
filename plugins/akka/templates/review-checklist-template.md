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
