# Context Loading

## Load Components

Load specific parts of the project into context for focused work.

### By Category

| Category | What It Loads |
|----------|---------------|
| `api` | API routes and endpoints |
| `models` | Data models and types |
| `services` | Business logic services |
| `utils` | Utility functions |
| `tests` | Test files |
| `config` | Configuration files |
| `auth` | Authentication related |
| `db` | Database related |

### By Path

```bash
/load src/services/user.ts      # Specific file
/load src/auth/                  # Directory
```

### Flags

| Flag | Description |
|------|-------------|
| `--all` | Load all key components |
| `--shallow` | Load only file summaries |
| `--deep` | Load full file contents |
| `--related` | Include related files |

### Output

```markdown
## Loaded Context

### Files Loaded (N)
- `path/to/file.ts` - [purpose]

### Key Components
- [Component]: [description]

### Ready For
- [suggested actions based on loaded context]
```
