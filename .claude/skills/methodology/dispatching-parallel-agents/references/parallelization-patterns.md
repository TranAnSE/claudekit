# Parallelization Patterns Reference

How to decide what to parallelize and which pattern to use.

## Core Principle

Parallelize when tasks are **independent**: no shared mutable state, no ordering dependency, and results can be combined without conflict.

## Pattern 1: Independent Tasks

**When**: Two or more tasks share no state and have no ordering dependency.

**Always parallel.** This is the simplest and most common case.

### Examples

- Linting + type checking + unit tests (different tools, same codebase, read-only)
- Researching two unrelated libraries
- Generating tests for unrelated modules
- Reviewing separate files

### Structure

```
[Dispatcher]
    |--- Agent A: lint src/
    |--- Agent B: typecheck src/
    |--- Agent C: run tests
    \--- Agent D: security scan
[Collect all results]
```

### Decision Criteria

- Do they read/write the same files? No -> parallel
- Does one need output from another? No -> parallel
- Can they run in any order? Yes -> parallel

## Pattern 2: Fan-Out / Fan-In

**When**: A single task can be split into N identical subtasks, then results are merged.

### Examples

- Process each file in a directory independently
- Run the same analysis on multiple services
- Test multiple configurations
- Investigate multiple potential causes of a bug

### Structure

```
[Dispatcher: split work into N chunks]
    |--- Agent 1: process chunk 1
    |--- Agent 2: process chunk 2
    |--- Agent 3: process chunk 3
    \--- Agent N: process chunk N
[Collector: merge results from all agents]
```

### Implementation

Split items across agents (round-robin, by directory, or by type), dispatch all simultaneously, collect results, handle failures by retrying individually, then merge into unified output.

## Pattern 3: Pipeline (Sequential)

**When**: Output of step N is input to step N+1.

**Must be sequential.** Cannot parallelize.

### Examples

- Parse code -> analyze AST -> generate report
- Fetch data -> transform -> validate -> persist
- Write code -> run tests -> fix failures

### Structure

```
[Step 1: parse] --> [Step 2: analyze] --> [Step 3: report]
```

### When Pipelines Contain Parallelizable Steps

A pipeline stage itself might fan out:

```
[Step 1: identify files]
    --> [Step 2: analyze each file in parallel (fan-out/fan-in)]
    --> [Step 3: merge analysis into report]
```

## Pattern 4: Pipeline with Parallel Stages

**When**: Some pipeline stages can run in parallel, others must be sequential.

### Example: Feature Implementation

```
[Sequential: write plan]
    --> [Parallel: implement module A, implement module B, implement module C]
    --> [Sequential: integration test]
    --> [Parallel: write docs, update changelog]
    --> [Sequential: final review]
```

## Decision Matrix

| Task Characteristic | Pattern | Parallelizable? |
|---|---|---|
| No shared state, no ordering | Independent | Yes |
| Same operation on many items | Fan-out/fan-in | Yes |
| Output feeds next step | Pipeline | No |
| Mixed dependencies | Pipeline + parallel stages | Partially |
| Shared mutable state | Sequential or lock-based | No (usually) |
| Non-deterministic ordering matters | Sequential | No |

## Common Parallel Task Patterns

### File-Per-Agent

Split work by file or directory. Each agent owns its files exclusively.

```
Agent 1: src/auth/**
Agent 2: src/orders/**
Agent 3: src/users/**
```

**Best for**: code review, refactoring, test generation, documentation.

**Watch out for**: shared utilities, cross-module imports. Assign shared code to one agent or make it read-only for all.

### Test Suite Splitting

Split tests by module, type, or estimated runtime.

```
Agent 1: unit tests (fast)
Agent 2: integration tests (medium)
Agent 3: e2e tests (slow)
```

**Best for**: CI acceleration, pre-merge validation.

### Multi-Service Investigation

When debugging spans multiple services, assign one agent per service.

```
Agent 1: investigate auth service logs
Agent 2: investigate order service logs
Agent 3: investigate payment service logs
```

**Best for**: distributed system debugging, incident response.

### Research Branches

Explore multiple hypotheses or approaches simultaneously.

```
Agent 1: research approach A (Redis caching)
Agent 2: research approach B (CDN edge caching)
Agent 3: research approach C (application-level memoization)
```

**Best for**: technology evaluation, design exploration, root cause hypotheses.

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Parallelizing dependent tasks | Race conditions, wrong results | Identify dependencies first, use pipeline |
| Too many agents | Overhead exceeds benefit | 2-5 agents is typical sweet spot |
| No merge strategy | Results conflict or duplicate | Define merge/dedup logic before dispatching |
| Shared file writes | Corruption, lost changes | Assign file ownership to one agent |
| No failure handling | One failure blocks everything | Collect partial results, retry individually |

## Checklist Before Parallelizing

1. **List all tasks** that need to happen
2. **Draw dependencies** between them (which needs output from which?)
3. **Group independent tasks** into parallel batches
4. **Define the merge strategy** for collecting results
5. **Assign ownership** so no two agents write the same file
6. **Plan for failure** of individual agents
7. **Estimate whether parallelism helps** (overhead vs time saved)

## Quick Reference: Dispatch Decision

- Single atomic operation -> just do it, no parallelism
- Splittable into independent chunks -> fan-out/fan-in
- Each step depends on previous output -> pipeline (sequential)
- Mix of independent and dependent steps -> pipeline with parallel stages
- Everything independent -> run all in parallel
