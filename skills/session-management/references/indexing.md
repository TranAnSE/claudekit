# Project Indexing

## Generate Index

Scan the project and create `PROJECT_INDEX.md`:

### Excluded Directories
`node_modules/`, `.git/`, `__pycache__/`, `dist/`, `build/`, `.next/`, `venv/`, `.venv/`, coverage, cache

### File Categories
- **Entry Points**: Main files, index files, app entry
- **API/Routes**: Endpoint definitions
- **Models/Types**: Data structures, schemas
- **Services**: Business logic
- **Utilities**: Helper functions
- **Tests**: Test files
- **Configuration**: Config files, env templates

### Output Format

```markdown
# Project Index: [Name]

Generated: [timestamp]

## Quick Navigation
| Category | Key Files |
|----------|-----------|
| Entry Points | [list] |
| API Routes | [list] |

## Directory Structure
[tree view]

## Key Files
### Entry Points
- `[path]` - [description]

## Dependencies
### External
- [package]: [purpose]

## Architecture Notes
[patterns observed]
```
