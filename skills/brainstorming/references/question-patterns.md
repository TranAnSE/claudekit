# Brainstorming Question Patterns

Quick-reference catalog of effective question types for brainstorming sessions. Use these to systematically explore a problem space before jumping to solutions.

---

## Clarifying Questions

**Purpose:** Ensure you understand the actual problem before solving it. Most failed implementations stem from unclear requirements.

**When to use:** At the start of every brainstorming session, and whenever the request contains ambiguous terms.

| # | Question | Context |
|---|----------|---------|
| 1 | What exactly should happen when a user does X? | Use when the described behavior has multiple valid interpretations. Forces concrete scenario thinking. |
| 2 | Who is the primary user of this feature, and what's their current workflow? | Use when the requester assumes you know the audience. Different users need different solutions. |
| 3 | What does success look like? How will you know this is working? | Use to surface acceptance criteria early. Prevents building the wrong thing correctly. |
| 4 | Can you walk me through a specific example from start to finish? | Use when the description is abstract. Concrete examples reveal hidden requirements. |

---

## Constraint Questions

**Purpose:** Identify boundaries that shape the solution space. Constraints eliminate options early and prevent wasted effort.

**When to use:** After clarifying the goal, before exploring solutions. Especially important when the requester says "just build X."

| # | Question | Context |
|---|----------|---------|
| 1 | What's the timeline? Is there a hard deadline or a target? | Use always. A 2-day solution looks nothing like a 2-month solution. |
| 2 | What can't change? Are there existing systems, APIs, or schemas we must preserve? | Use when modifying an existing system. Reveals integration constraints. |
| 3 | What's the performance budget? Expected load, response time, data volume? | Use for any feature touching data pipelines, APIs, or user-facing flows. |
| 4 | Are there compliance, security, or accessibility requirements? | Use for anything involving user data, payments, or public-facing UI. Easy to forget, expensive to retrofit. |

---

## Alternative Questions

**Purpose:** Expand the solution space. The first idea is rarely the best idea.

**When to use:** After constraints are clear but before committing to an approach. Especially when the requester has already proposed a specific solution.

| # | Question | Context |
|---|----------|---------|
| 1 | What if we solved this without building anything new? Could an existing tool or configuration handle it? | Use to challenge the assumption that code is needed. Sometimes a config change or third-party tool is enough. |
| 2 | What's the simplest version that still delivers value? | Use to find the MVP. Strips away nice-to-haves and focuses on the core need. |
| 3 | Have you considered [opposite approach]? What would that look like? | Use to break anchoring bias. If they propose a push model, ask about pull. If sync, ask about async. |
| 4 | What would we do if we had to ship this today? | Use to identify which parts are truly essential vs. which are aspirational. |

---

## Prioritization Questions

**Purpose:** Sequence work effectively when there's more to do than time allows.

**When to use:** When the feature has multiple components, when scope is growing, or when the team is debating what to build first.

| # | Question | Context |
|---|----------|---------|
| 1 | Which of these capabilities is most important to the first user? | Use to rank features by user impact rather than technical convenience. |
| 2 | What's the MVP — the smallest thing we can ship and learn from? | Use when scope is expanding. Forces a shippable first increment. |
| 3 | What can wait for v2 without blocking the core experience? | Use to defer non-essential work explicitly rather than letting it creep in. |
| 4 | If we could only ship one of these this week, which one? | Use when the team can't agree on priority. Forces a direct comparison. |

---

## Technical Questions

**Purpose:** Ground the discussion in implementation reality. Surface architecture decisions that affect the solution.

**When to use:** Once the goal and constraints are clear, before writing a plan. Essential for features that touch multiple systems.

| # | Question | Context |
|---|----------|---------|
| 1 | What's the data model? What entities exist, and how do they relate? | Use for any feature involving persistent state. Data model drives everything. |
| 2 | How does authentication and authorization work for this? Who can see/do what? | Use for any feature with access control. Auth is often assumed but rarely specified. |
| 3 | What's the expected scale — users, requests/sec, data size? | Use to choose between simple and scalable approaches. Over-engineering is as wasteful as under-engineering. |
| 4 | What existing code or patterns should this follow? Are there conventions to match? | Use to maintain consistency. New code that ignores existing patterns creates maintenance burden. |

---

## Using This Reference

1. **Don't ask all questions** — pick the 3-5 most relevant for the situation
2. **Start with clarifying** — always ensure you understand the problem
3. **Adapt the phrasing** — these are templates, not scripts
4. **Listen for gaps** — the questions the requester struggles to answer reveal the areas that need more thought
5. **Document answers** — capture decisions as they're made so you don't re-ask later
