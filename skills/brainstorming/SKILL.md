---
name: brainstorming
argument-hint: "[topic]"
description: >
  Use when the user wants to design, explore, or ideate on ANY new feature, architecture decision, or unclear requirement. Activate for keywords like "brainstorm", "design", "explore", "what if", "how should we", "options for", "trade-offs", or any open-ended question about implementation approach. Also trigger when requirements are vague, ambiguous, or when multiple valid solutions exist -- err on the side of brainstorming before jumping into code.
---

# Brainstorming

## When to Use

- Designing new features with unclear requirements
- Exploring architecture decisions
- Refining user requirements
- Breaking down complex problems
- When multiple valid approaches exist

## When NOT to Use

- Executing already-approved plans -- use `executing-plans` instead
- Simple bug fixes with obvious solutions -- jump straight to fixing
- Mechanical refactoring where the approach is already clear

---

## Startup Mode (for new product / standalone ideas)

**Activation**: user's topic is a new product or standalone initiative, not a feature inside an existing codebase.

**Detection signals**:

- Keywords: "is this worth building", "should I build", "startup idea", "product idea", "I have an idea for"
- No existing codebase context; user is describing a concept pre-code

**Gate question** (first clarifier, always):

> Is this (a) a feature inside an existing codebase, or (b) a new product / standalone idea?
> - (b) → Startup Mode replaces Phase 1 (Understanding)
> - (a) → normal Phase 1

**Six forcing questions** (asked one at a time, per existing conventions):

1. **Demand reality** — "How do you *know* people want this? Give me evidence, not intuition."
2. **Status quo** — "What do people do today to solve this? Why isn't that enough?"
3. **Desperate specificity** — "Who is your very first user? Name, role, where you find them — be concrete."
4. **Narrowest wedge** — "What's the smallest thing you could ship this week that delivers real value to that one user?"
5. **Observation** — "Have you watched someone struggle with this problem? What did you see?"
6. **Future-fit** — "If this works, what does v3 look like in two years? Does that excite you enough to commit?"

**Output gate** (after Q6) — produce a traffic-light assessment per question (🟢/🟡/🔴) plus a recommendation:

- 5-6 green → proceed to Phase 2 (Exploration)
- 2-4 green → proceed but flag red/yellow items as design-time risks
- 0-1 green → pause; suggest more user-discovery work before designing

**After Startup Mode**: continue with the existing Phase 2 (Exploration) and Phase 3 (Design Presentation). YAGNI, multiple-choice questioning, and design-doc output are unchanged.

---

## Three-Phase Process

### Phase 1: Understanding

**Goal**: Clarify requirements through sequential questioning.

**Rules**:
- Ask only ONE question per message
- If a topic needs more exploration, break it into multiple questions
- Prefer multiple-choice questions over open-ended when possible
- Wait for user response before next question

**Example**:
```
BAD: "What authentication method do you want, and should we support SSO,
      and what about password requirements?"

GOOD: "Which authentication method should we use?
       a) Username/password only
       b) OAuth (Google, GitHub)
       c) Both options"
```

### Phase 2: Exploration

**Goal**: Present alternatives with clear trade-offs.

**Process**:
1. Present 2-3 different approaches
2. Lead with the recommended option
3. Explain trade-offs for each
4. Let user choose direction

**Format**:
```markdown
## Approach 1: [Name] (Recommended)
[Description]
- Pros: [Benefits]
- Cons: [Drawbacks]

## Approach 2: [Name]
[Description]
- Pros: [Benefits]
- Cons: [Drawbacks]

Which approach aligns better with your goals?
```

### Phase 3: Design Presentation

**Goal**: Present validated design in digestible chunks.

**Rules**:
- Break design into 200-300 word sections
- Validate incrementally after each section
- Cover: architecture, components, data flow, error handling, testing
- Be flexible - allow user to request clarification or changes

**Sections to Cover**:
1. Architecture overview
2. Component breakdown
3. Data flow
4. Error handling
5. Testing considerations

---

## Core Principles

### YAGNI Ruthlessly

Remove unnecessary features aggressively:
- Question every "nice to have"
- Start with minimal viable design
- Add complexity only when justified
- "We might need this later" = remove it

### One Question at a Time

Sequential questioning produces better results:
- Gives user time to think deeply
- Prevents overwhelming with choices
- Creates natural conversation flow
- Allows follow-up on unclear points

### Multiple-Choice Preference

When possible, provide structured options:
- Reduces cognitive load
- Surfaces your understanding
- Makes decisions concrete
- Still allow "Other" option

---

## Output Format

**Save location**: After design validation, write the design document to:

```
docs/claudekit/specs/YYYY-MM-DD-<topic>-design.md
```

Create the `docs/claudekit/specs/` directory if it does not exist. Use today's date (YYYY-MM-DD) and a short, kebab-case topic slug.

Document to timestamped markdown:

```markdown
# Design: [Feature Name]
Date: [YYYY-MM-DD]

## Summary
[2-3 sentences]

## Architecture
[Architecture decisions]

## Components
[Component breakdown]

## Data Flow
[How data moves through system]

## Error Handling
[Error scenarios and handling]

## Testing Strategy
[Testing approach]

## Open Questions
[Any remaining unknowns]
```

---

## Post-Design Workflow

After design is validated:
1. Commit design document to version control
2. Optionally proceed to implementation
3. Use `writing-plans` skill for detailed task breakdown
4. Use `executing-plans` skill for implementation

---

## MCP Integration

This skill leverages MCP servers for enhanced brainstorming:

### Sequential Thinking (Primary)
```
Use Sequential Thinking for structured exploration:
- Track design options as thought sequences
- Build confidence in recommendations incrementally
- Allow for revisions as user provides feedback
- Document reasoning chain for design decisions
```

### Memory
```
Persist design decisions across sessions:
- Store design concepts as entities
- Create relations between components
- Recall user preferences from previous sessions
- Build project design knowledge over time
```

### Context7
```
For informed technology choices:
- Fetch current library documentation
- Compare capabilities accurately
- Ground recommendations in real data
```

---

## Stack-Specific Brainstorming Examples

These show what Phase 2 (Exploration) output looks like for different domains:

### FastAPI endpoint design

```markdown
## Approach 1: REST + JWT Bearer Auth (Recommended)
POST /api/orders with Pydantic v2 validation, async SQLAlchemy.
- Pros: Simple, cacheable, great OpenAPI docs via FastAPI
- Cons: Multiple round-trips for nested resources

## Approach 2: GraphQL + API Key Auth
Single /graphql endpoint with Strawberry, API key in header.
- Pros: Flexible queries, single round-trip for nested data
- Cons: Caching harder, team unfamiliar with Strawberry

**Decision**: REST — team knows it, OpenAPI auto-docs save time,
nested resources not needed for this feature.
```

### React data table component

```markdown
## Approach 1: TanStack Table + URL Params (Recommended)
Server component fetches data, client component for interactions.
Sort/filter state in URL search params (shareable links).
- Pros: Bookmarkable state, SSR-friendly, no global store needed
- Cons: URL parsing boilerplate

## Approach 2: Zustand Store + SWR
Client-only with SWR for fetching, Zustand for table state.
- Pros: Simple state management, familiar pattern
- Cons: Not SSR-friendly, state lost on refresh

**Decision**: TanStack Table + URL params — users need to share
filtered views, and it works with Next.js App Router.
```

### Database multi-tenancy

```markdown
## Approach 1: Shared Table + tenant_id + RLS (Recommended)
Single `orders` table with `tenant_id` column, PostgreSQL RLS policies.
- Pros: Simple migrations, single connection pool, no schema sprawl
- Cons: Must never forget WHERE tenant_id = ? (RLS prevents this)

## Approach 2: Schema-per-tenant
Each tenant gets own PostgreSQL schema, selected via search_path.
- Pros: Strong isolation, easy per-tenant backup/restore
- Cons: Migration complexity grows linearly with tenants

**Decision**: Shared table + RLS — we have <100 tenants, RLS gives
isolation guarantees without migration pain.
```

---

## Related Skills

- `writing-plans` -- After brainstorming produces a validated design, use writing-plans to create a detailed implementation plan
- `sequential-thinking` -- For complex problems that benefit from structured step-by-step reasoning during the brainstorming process
