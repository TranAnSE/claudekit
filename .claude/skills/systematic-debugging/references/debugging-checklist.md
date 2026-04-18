# Systematic Debugging Checklist

Step-by-step process for debugging any issue. Follow the steps in order — skipping ahead is the most common cause of wasted debugging time.

---

## Step 1: Reproduce

**Goal:** Confirm you can trigger the bug on demand.

- [ ] **Get the exact steps** — What did the user do? What input? What sequence?
- [ ] **Reproduce it yourself** — If you can't reproduce it, you can't verify a fix
- [ ] **Find the minimal reproduction** — Strip away everything that isn't necessary to trigger the bug
- [ ] **Document the environment**
  - OS and version
  - Language/runtime version
  - Dependency versions
  - Environment variables or config that matters
- [ ] **Note what you expect vs. what actually happens**

**If you can't reproduce:**
- Check if it's environment-specific (OS, browser, node version)
- Check if it's state-dependent (specific data, race condition, cache)
- Add logging and wait for it to happen again

---

## Step 2: Gather Evidence

**Goal:** Collect all available information before forming theories.

- [ ] **Read the error message carefully** — The answer is often in the message. Read the full text, not just the first line.
- [ ] **Read the full stack trace** — Identify which line in YOUR code is the entry point (ignore framework internals at first)
- [ ] **Check logs** — Application logs, server logs, browser console
- [ ] **Check timestamps** — When did it start? Does it correlate with a deployment, config change, or data change?
- [ ] **Check recent changes**
  ```bash
  git log --oneline -20
  git diff HEAD~5..HEAD -- path/to/suspect/area/
  ```
- [ ] **Check monitoring/metrics** — Error rates, latency, resource usage
- [ ] **Search for the error** — Has someone on the team seen this before? Check issues, Slack, docs.

---

## Step 3: Form Hypotheses

**Goal:** Generate candidate explanations ranked by likelihood.

- [ ] **What changed recently?** — The most common cause of new bugs is new code
- [ ] **What assumptions might be wrong?** — About input format, data state, timing, permissions
- [ ] **List 2-3 hypotheses** — Write them down explicitly:
  1. [Most likely] ...
  2. [Possible] ...
  3. [Less likely but worth checking] ...
- [ ] **For each hypothesis, define what evidence would confirm or refute it**

**Common root causes to consider:**
- Null/undefined where a value was expected
- Off-by-one or boundary condition
- Race condition or timing issue
- Stale cache or state
- Environment difference (local vs. prod)
- Dependency version mismatch
- Incorrect assumption about API contract

---

## Step 4: Test Hypotheses

**Goal:** Confirm or eliminate each hypothesis with evidence.

- [ ] **Start with the most likely hypothesis**
- [ ] **Add targeted logging** — Log the specific values your hypothesis predicts will be wrong
  ```python
  # Python
  import logging
  logger = logging.getLogger(__name__)
  logger.debug(f"Value at suspect point: {value!r}, type: {type(value)}")
  ```
  ```javascript
  // JavaScript
  console.log('Value at suspect point:', JSON.stringify(value), typeof value);
  ```
- [ ] **Use git bisect for regressions** — Find the exact commit that introduced the bug
  ```bash
  git bisect start
  git bisect bad          # Current commit is broken
  git bisect good v1.2.0  # This version was working
  # Test each commit bisect offers, mark good/bad
  ```
- [ ] **Isolate components** — Test each component in isolation to narrow the scope
- [ ] **Use a debugger for complex state issues**

### Debugger Quick Reference

| Language | Tool | Start Command |
|----------|------|--------------|
| Python | pdb | `import pdb; pdb.set_trace()` or `breakpoint()` |
| Python | logging | `logging.basicConfig(level=logging.DEBUG)` |
| Python | traceback | `import traceback; traceback.print_exc()` |
| JavaScript | debugger | `debugger;` statement in code |
| JavaScript | console | `console.log()`, `console.trace()`, `console.table()` |
| JavaScript | Chrome DevTools | Open DevTools > Sources > set breakpoint |
| TypeScript | Node inspect | `node --inspect -r ts-node/register script.ts` |

---

## Step 5: Fix and Verify

**Goal:** Apply the minimal correct fix and prove it works.

- [ ] **Make the smallest fix possible** — Fix the bug, not the whole file. One concern per commit.
- [ ] **Write a regression test** — A test that fails without your fix and passes with it
  ```python
  def test_handles_empty_input_without_crash():
      """Regression test for bug #123 — empty input caused TypeError."""
      result = process(input_data="")
      assert result == expected_default
  ```
- [ ] **Verify the fix resolves the original reproduction**
- [ ] **Run the full test suite** — Confirm no side effects
- [ ] **Check related code paths** — Is the same bug pattern present elsewhere?
  ```bash
  # Search for similar patterns
  grep -rn "similar_pattern" src/
  ```
- [ ] **Test edge cases around the fix** — Boundary values, null inputs, concurrent access

---

## Step 6: Document and Prevent

**Goal:** Prevent this class of bug from recurring.

- [ ] **Write a clear commit message** explaining what was wrong and why the fix works
- [ ] **Update documentation** if the bug revealed a misunderstanding
- [ ] **Consider systemic fixes:**
  - Could a type system catch this? (Add types)
  - Could a linter rule catch this? (Add rule)
  - Could input validation catch this? (Add validation)
  - Could monitoring catch this sooner? (Add alert)

---

## Quick Reference: Debugging Anti-Patterns

| Anti-Pattern | What to Do Instead |
|-------------|-------------------|
| Changing random things until it works | Form a hypothesis, test it, iterate |
| Debugging in production | Reproduce locally first |
| Reading code for hours without running it | Add a log statement and run it |
| Fixing the symptom, not the cause | Ask "why?" until you reach the root |
| Not writing a regression test | Always write one before closing the bug |
| Debugging alone for too long | Ask for help after 30 minutes of no progress |
