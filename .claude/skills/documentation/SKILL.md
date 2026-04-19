---
name: documentation
argument-hint: "[file or api/readme]"
description: >
  Use when generating or updating documentation — including code comments, docstrings, JSDoc, API docs, README files, or technical specifications. Trigger for keywords like "document", "docstring", "JSDoc", "README", "API docs", "explain this code", "add comments", or any request to improve code documentation. Also activate when generating project documentation or updating existing docs after code changes.
---

# Documentation

## When to Use

- Adding docstrings or JSDoc to functions/classes
- Generating or updating README files
- Documenting API endpoints
- Writing technical specifications
- Adding inline comments to complex logic

## When NOT to Use

- Generating changelogs from commits — use `git-workflows`
- Writing OpenAPI specs — use `openapi`
- Architecture design documentation — use `brainstorming` + `writing-plans`

---

## Quick Reference

| Topic | Reference | Key content |
|-------|-----------|-------------|
| Code documentation | `references/code-docs.md` | Python docstrings, TypeScript JSDoc, inline comments |
| API documentation | `references/api-docs.md` | Endpoint docs, request/response examples |
| Project documentation | `references/project-docs.md` | README, CONTRIBUTING, architecture docs |

---

## Documentation Workflow

### For Code

1. Read the code thoroughly — understand purpose and behavior
2. Identify inputs, outputs, side effects, and edge cases
3. Add docstrings/JSDoc with examples
4. Add type annotations if missing

### For APIs

1. Scan route definitions and identify endpoints
2. Document request format, response format, error responses
3. Add authentication requirements
4. Include working examples

### For Projects

1. Analyze project purpose, features, and setup
2. Write clear installation and usage instructions
3. Include working code examples
4. Keep configuration tables up to date

---

## Best Practices

1. **Document the why, not the what** — code shows what; comments explain why.
2. **Include examples** — one working example beats three paragraphs of description.
3. **Document edge cases** — what happens with null, empty, or invalid input?
4. **Keep docs adjacent to code** — docstrings over separate doc files.
5. **Update docs with code** — stale docs are worse than no docs.

## Common Pitfalls

1. **Restating the code** — `# increment i by 1` adds no value.
2. **Missing error documentation** — not documenting what exceptions a function raises.
3. **Outdated examples** — code examples that no longer compile.
4. **Over-documenting internal code** — public APIs need docs; private helpers often don't.

---

## Related Skills

- `openapi` — OpenAPI spec generation for REST APIs
- `git-workflows` — Changelog generation from commits
- `backend-frameworks` — Framework-specific documentation patterns
