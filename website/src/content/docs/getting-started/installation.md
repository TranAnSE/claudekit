---
title: Installation
description: How to install Claude Kit in your project.
---

# Installation

Claude Kit installs in under 2 minutes. Choose your preferred method below.

## Prerequisites

- [Claude Code](https://claude.ai/code) installed and authenticated
- Git (for cloning the repository)

## Method 1: Clone and Copy (Recommended)

```bash
# Clone Claude Kit
git clone https://github.com/duthaho/claudekit.git

# Copy the .claude folder to your project
cp -r claudekit/.claude /path/to/your-project/

# Navigate to your project
cd /path/to/your-project

# Start Claude Code
claude
```

## Method 2: Download ZIP

1. Go to [github.com/duthaho/claudekit](https://github.com/duthaho/claudekit)
2. Click **Code** > **Download ZIP**
3. Extract the ZIP file
4. Copy the `.claude` folder to your project root

## Method 3: Git Submodule

Track Claude Kit updates via Git:

```bash
# Add as submodule
git submodule add https://github.com/duthaho/claudekit.git .claudekit

# Create symlink to .claude folder
ln -s .claudekit/.claude .claude

# Commit the changes
git add .claudekit .claude
git commit -m "Add Claude Kit"
```

To update later:

```bash
git submodule update --remote .claudekit
```

## Verify Installation

```bash
cd your-project
claude
```

Skills trigger automatically based on your conversation. Try asking Claude to brainstorm a feature or debug an error — the relevant skills will activate.

## Folder Structure

After installation, your project should have:

```
your-project/
├── .claude/
│   ├── CLAUDE.md          # Project instructions
│   ├── agents/            # 20 specialized subagents
│   │   ├── code-reviewer.md
│   │   ├── debugger.md
│   │   └── ...
│   ├── modes/             # 7 behavioral modes
│   │   ├── brainstorm.md
│   │   ├── implementation.md
│   │   └── ...
│   ├── skills/            # 43 knowledge modules
│   │   ├── brainstorming/
│   │   ├── testing/
│   │   ├── languages/
│   │   └── ...
│   ├── mcp/               # MCP server configs
│   └── settings.json      # Claude Code settings
└── ... (your project files)
```

## Troubleshooting

### Skills not triggering

Make sure the `.claude` folder is in your project root (same level as `package.json` or `pyproject.toml`).

### Permission errors

On Unix systems, ensure the files are readable:

```bash
chmod -R 644 .claude/
```

### Claude Code not finding CLAUDE.md

Restart Claude Code after adding the `.claude` folder:

```bash
# Exit Claude Code (Ctrl+C or /exit)
# Restart
claude
```

## Next Steps

1. [Configuration](/claudekit/getting-started/configuration/) — Customize for your project
2. [Workflows](/claudekit/workflows/planning-and-building/) — See how skills work together
