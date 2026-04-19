# Checkpoints

## Save Checkpoint

```bash
/checkpoint save [name]
```

Creates a git stash with metadata in `.claude/checkpoints/[name].json`:

```json
{
  "name": "feature-auth",
  "created": "2026-04-19T14:30:00Z",
  "git_stash": "stash@{0}",
  "files_in_context": ["src/auth/login.ts", "src/auth/token.ts"],
  "current_task": "Implementing JWT refresh",
  "notes": "User-provided notes"
}
```

## List Checkpoints

```bash
/checkpoint list
```

## Restore Checkpoint

```bash
/checkpoint restore [name]
```

Applies git stash, loads metadata, summarizes restored context.

## Delete Checkpoint

```bash
/checkpoint delete [name]
```

## Auto-Checkpoint Triggers

Suggest checkpoints before:
- Major refactoring
- Context switches
- Risky operations
- Natural breakpoints in complex work
