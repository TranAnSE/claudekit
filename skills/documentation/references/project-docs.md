# Project Documentation Patterns

## README Structure

```markdown
## Installation

```bash
npm install my-package
```

## Quick Start

```typescript
import { Client } from 'my-package';
const client = new Client({ apiKey: 'your-key' });
const result = await client.fetch();
```

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `apiKey` | string | required | Your API key |
| `timeout` | number | 5000 | Request timeout in ms |
```

## Key Sections

1. **Title + one-liner** — what this project does
2. **Installation** — copy-pasteable setup commands
3. **Quick Start** — working example in < 10 lines
4. **Configuration** — table of options with types and defaults
5. **API Reference** — link to detailed docs
6. **Contributing** — how to contribute
7. **License** — MIT, Apache, etc.

## Documentation Coverage Report

After documenting, summarize:
- Functions documented: X/Y (Z%)
- Endpoints documented: X/Y (Z%)
- Missing: [list of undocumented items]
