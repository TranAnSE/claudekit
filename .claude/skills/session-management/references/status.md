# Status Checking

## Project Status

Show current project state:

```bash
git status
git log --oneline -5
```

### Output Format

```markdown
## Project Status

### Git
- Branch: `feature/xyz`
- Status: Clean / X modified files

### Tasks
- In Progress: X
- Pending: Y
- Completed: Z

### Recent Commits
1. [commit message]
2. [commit message]

### Open PRs
- #123: [title]
```

Combines git state, TodoWrite tasks, and recent activity into a single snapshot.
