# FCP CLI

Command-line interface for the [Food Context Protocol](https://fcp.dev) - an open standard enabling AI agents to understand food context.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)

[Protocol Spec](https://github.com/Food-Context-Protocol/fcp) ·
[FCP Server](https://github.com/Food-Context-Protocol/fcp-gemini-server) ·
[Documentation](https://docs.fcp.dev)

---

## Quick Start

```bash
# Install
pip install fcp-cli

# Configure (just need server URL)
export FCP_SERVER_URL=https://api.fcp.dev
export FCP_USER_ID=demo

# Try it
fcp --help
```

## Demo Commands

```bash
# 1. Log a meal
fcp log add "Tonkotsu Ramen" --meal-type dinner

# 2. Search your history
fcp search query "ramen from this week"

# 3. Get AI meal suggestions
fcp suggest meals --context "japanese cuisine"

# 4. Check food safety
fcp safety recalls lettuce romaine

# 5. Research food topics
fcp research ask "What are the health benefits of fermented foods?"

# 6. View your taste profile
fcp profile show

# 7. Manage your pantry
fcp pantry list
fcp pantry add eggs milk bread

# 8. Batch log multiple meals (18.7x faster!)
fcp log batch ./photos --parallel 5 --res low
fcp log batch ~/meals --parallel 3 --res medium --meal-type lunch
```

## Features

- 🍱 **60+ Commands** - Logging, search, suggestions, safety, research, recipes, pantry, and more
- 🤖 **Gemini 3 Powered** - Multimodal analysis, grounding, thinking
- ⚡ **Blazing Fast** - Parallel batch processing (18.7x speedup), HTTP/2, connection pooling
- 🎯 **Smart Resolution** - Auto-detect image quality (low/medium/high) for cost optimization
- 🔗 **FCP Protocol** - Command-line access to core FCP features
- 📦 **Type-Safe** - Pydantic models throughout with pydantic-settings
- ✨ **Rich Output** - Beautiful terminal formatting with Rich
- 🔧 **13 Command Groups** - Organized by feature area

## Command Groups

| Group | Commands | Description |
|-------|----------|-------------|
| `log` | add, list, show, edit, delete, nutrition, menu, donate, **batch** | Track meals and food logs |
| `search` | query, by-date, barcode | Search food history |
| `suggest` | meals | AI meal suggestions |
| `safety` | recalls, interactions, allergens, restaurant | Food safety checks |
| `research` | ask | AI-powered food research |
| `profile` | show, update | Taste profile analysis |
| `recipes` | list, search, get, save, extract | Recipe management |
| `pantry` | list, add, remove, expiring | Inventory tracking |
| `nearby` | search | Find local restaurants |
| `publish` | social, blog, newsletter | Content generation |
| `discover` | trends, products | Food discovery |
| `labels` | generate | Nutrition labels |
| `taste` | analyze, compatibility | Taste analysis |

## Configuration

FCP CLI uses **pydantic-settings** for type-safe configuration. Settings can be provided via:

1. **Environment variables** (highest priority)
2. **.env file** (loaded automatically if present)
3. **Default values** (fallback)

### Environment Variables

```bash
# Server URL (default: http://localhost:8080)
FCP_SERVER_URL=https://api.fcp.dev

# User ID (default: demo)
FCP_USER_ID=your-user-id

# Optional: Firebase JWT token for authenticated requests
FCP_AUTH_TOKEN=your-firebase-jwt-token
```

### .env File

Create a `.env` file in your project directory:

```env
FCP_SERVER_URL=https://api.fcp.dev
FCP_USER_ID=demo
FCP_AUTH_TOKEN=your-token-here
```

The CLI will automatically load settings from `.env` if it exists.

## Development

```bash
# Clone the repo
git clone https://github.com/Food-Context-Protocol/fcp-cli
cd fcp-cli

# Install with uv
uv sync --all-extras --dev

# Run locally
uv run fcp --help

# Run tests (100% coverage, 1171 tests)
uv run pytest

# Format and lint
uv run ruff format src/
uv run ruff check src/
```

## Architecture

```
┌─────────────────────────────────────────┐
│         FCP CLI (Typer + Rich)          │
│  ┌──────────────┬──────────────────┐   │
│  │ Local Agents │  HTTP REST       │   │
│  │ (PydanticAI) │  Client          │   │
│  └──────────────┴──────────────────┘   │
└─────────────────────────────────────────┘
       │                    │
       │ Direct             │ HTTP
       ▼                    ▼
┌────────────┐      ┌─────────────────┐
│ Gemini API │      │  FCP Server     │
│            │      │  (api.fcp.dev)  │
└────────────┘      └─────────────────┘
```

**Hybrid Mode:**
- Some commands use local PydanticAI agents (fast, direct)
- Others use HTTP REST to FCP server (remote, scalable)
- Automatically chooses best approach per command

## License

Apache-2.0 License - See [LICENSE](LICENSE)

## Links

- **Protocol Spec:** [Food-Context-Protocol/fcp](https://github.com/Food-Context-Protocol/fcp)
- **FCP Server:** [Food-Context-Protocol/fcp-gemini-server](https://github.com/Food-Context-Protocol/fcp-gemini-server)
- **Documentation:** [docs.fcp.dev](https://docs.fcp.dev)
- **API Docs:** [api.fcp.dev/docs](https://api.fcp.dev/docs)

---

<div align="center">
  <sub>Built with ❤️ for the Food Context Protocol</sub>
</div>
