---
name: writing-skills
description: >
  Use when creating new skills for this Claude Code kit, editing existing skills, or verifying skills work before deployment. Trigger for keywords like "create a skill", "new skill", "write a skill", "edit skill", "improve skill", "skill format", or when the user wants to add a new capability to the kit. Also activate when auditing skill quality or checking that descriptions trigger correctly.
---

# Writing Skills

## When to Use

- Creating a new skill from scratch
- Editing or improving an existing skill
- Auditing skill quality and trigger accuracy
- Adding stack-specific examples to methodology skills

## When NOT to Use

- Using an existing skill (just invoke it)
- Writing commands (see `.claude/commands/`)
- Writing agents (see `.claude/agents/`)

---

## Skill File Structure

Every skill lives in `.claude/skills/<name>/SKILL.md` with this format:

```markdown
---
name: <skill-name>
description: >
  <trigger description — when Claude should activate this skill>
---

# <Skill Title>

## When to Use
- [concrete scenarios]

## When NOT to Use
- [anti-patterns, common misapplications]

---

## Core Content
[patterns, code examples, templates]

---

## Common Pitfalls
[mistakes to avoid]

---

## Related Skills
- `other-skill` — how it relates
```

---

## The Description Field

The `description` field is the **most important part** — it determines when Claude activates the skill. It's a trigger description, not a summary.

### Good descriptions

```yaml
# Specific trigger conditions with keywords
description: >
  Trigger this skill whenever writing new features, fixing bugs, or
  changing any behavior in production code. Activate for keywords like
  "implement", "add feature", "fix bug". This skill should be the
  default for ALL implementation work.
```

### Bad descriptions

```yaml
# Too vague — when does this trigger?
description: A skill about testing.

# Too narrow — misses common scenarios
description: Use only when the user says "write a unit test".
```

### Description checklist

- [ ] Lists concrete trigger keywords
- [ ] Describes scenarios, not just topics
- [ ] Includes "also trigger when..." for edge cases
- [ ] Mentions what the skill is NOT for (helps avoid false positives)

---

## Naming Conventions

| Type | Convention | Examples |
|------|-----------|----------|
| Methodology | Gerund (verb-ing) | `brainstorming`, `writing-plans`, `systematic-debugging` |
| Language/Framework | Noun | `python`, `nestjs`, `react`, `postgresql` |
| Pattern | Noun/compound | `error-handling`, `state-management`, `api-client` |

This matches Anthropic's own naming convention for superpowers skills.

---

## Code Example Guidelines

### Methodology skills: always dual-stack

Methodology skills (brainstorming, TDD, debugging, etc.) must include both Python and TypeScript examples:

```markdown
### TypeScript
\`\`\`typescript
describe('calculateTotal', () => {
  it('should sum item prices', () => {
    expect(calculateTotal(items)).toBe(30);
  });
});
\`\`\`

### Python
\`\`\`python
def test_calculate_total_sums_item_prices():
    items = [{"price": 10}, {"price": 20}]
    assert calculate_total(items) == 30
\`\`\`
```

### Framework skills: single-stack with depth

Framework skills (nestjs, fastapi, react) use only their stack but go deeper:

```markdown
- Module/DI patterns
- Request validation
- Authentication guards
- Database integration
- Testing patterns
- Error handling
- Deployment
```

### Quality checklist for examples

- [ ] Real code, not pseudocode
- [ ] Includes import statements where relevant
- [ ] Shows the test AND the implementation
- [ ] Includes verification command (`pytest -v`, `npm test`)
- [ ] Matches the kit's code conventions (PEP 8, strict TS)

---

## Skill Quality Checklist

Before committing a new or updated skill:

1. **Trigger accuracy** — Does the description match real usage scenarios?
2. **When to Use / When NOT to Use** — Are both sections specific and non-overlapping with other skills?
3. **Actionable patterns** — Does it tell you WHAT to do, not just WHAT things are?
4. **Code examples** — Real, copy-pasteable code (not theory or pseudocode)?
5. **Verification commands** — Does it show how to verify the patterns work?
6. **Pitfalls section** — Does it warn about common mistakes?
7. **Related Skills** — Does it link to complementary skills with brief explanations?
8. **Line count** — 200-350 lines is the sweet spot. Under 150 is too thin; over 400 is too bloated.

---

## Registering a New Skill

After writing the skill file:

1. **CLAUDE.md** — Add to the skill table under the appropriate category
2. **Description in system** — The description in YAML frontmatter is what Claude Code uses for triggering

### CLAUDE.md skill table format

```markdown
| **Category** | Skills |
|--------------|--------|
| **Languages** | python, typescript, javascript |
| **Methodology - Planning** | brainstorming, writing-plans, executing-plans |
```

---

## Updating Existing Skills

When improving an existing skill:

1. **Read current content first** — understand what's there
2. **ADD, don't rewrite** — preserve existing discipline/rigor
3. **Stack-specific examples** — add Python alongside TS (or vice versa)
4. **Test the trigger** — does the description still match after changes?
5. **Update Related Skills** — if the new content creates new connections

---

## Related Skills

- `writing-plans` — Plan format for multi-step implementation tasks
- `verification-before-completion` — Verify skills work before committing
- `writing-concisely` — Keep skills concise and scannable
