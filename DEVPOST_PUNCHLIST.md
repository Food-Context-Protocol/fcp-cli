# FCP CLI - Devpost Submission Checklist

**Deadline:** February 9, 2026 at 5:00 PM PT
**Submission:** Gemini 3 API Hackathon on Devpost

---

## ⚠️ CLI-SERVER ALIGNMENT STATUS

**See:** `CLI_SERVER_ALIGNMENT.md` for full analysis

**Current State:**
- ✅ CLI exposes 29/42 (69%) of server MCP tools
- ✅ 100% coverage of core features (nutrition, inventory, recipes, safety)
- ❌ Missing 13 advanced/niche tools

**Missing from CLI:**
1. Audio meal logging (`nutrition.log_meal_from_audio`)
2. Publishing (blog/social posts)
3. Business intelligence (economic gaps, festival planning)
4. Connectors (Drive, Calendar sync)
5. Trend analysis, image prompts, product lookup

**Decision Required:**
- **Option A:** Accept 69% coverage - CLI provides essential command-line access, server has full suite (RECOMMENDED for time)
- **Option B:** Add all 13 missing commands (~3-5 hours work)
- **Option C:** Add only demo-impressive features (audio, publishing, trends) (~1-2 hours)

**Recommendation:** Option A - Update video script to say "CLI provides command-line access to core FCP features" instead of claiming all 40+ tools.

---

## 🎯 MUST DO (< 1 Hour Total)

### 1. Fix Error Handling for Demo ⚡ (20 min)
**Why:** Can't have ugly stack traces in video demo
**Status:** ❌ Not started

**Implementation:**
```python
# Add to src/fcp_cli/utils.py
def demo_safe(func):
    """Decorator for demo-safe error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            console.print("\n[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            if "--debug" in sys.argv:
                raise  # Show full trace in debug mode
            raise typer.Exit(1)
    return wrapper

# Apply to all @app.command() functions
@app.command()
@demo_safe
def meal(...):
    ...
```

**Apply to:** Top 5-7 demo commands only
- `log meal`
- `search query`
- `suggest meal`
- `safety recalls`
- `research ask`

---

### 2. Add Demo Examples to --help ⚡ (20 min)
**Why:** Judges will run `fcp --help` first
**Status:** ❌ Not started

**Quick Polish:**
```python
# Update main commands only
@app.command(help="Log a meal to your food diary")
def meal(
    dish: str = typer.Argument(..., help="Dish name (e.g., 'Spicy Ramen')"),
    venue: str = typer.Option(None, "--venue", "-v", help="Restaurant name"),
):
    """
    Log a meal to your food diary with AI-powered nutrition analysis.

    Examples:
        fcp log meal "Tonkotsu Ramen" --venue "Ippudo NYC"
        fcp log meal "Margherita Pizza"
    """
```

**Update these commands:**
- `fcp log meal`
- `fcp search query`
- `fcp suggest meal`
- `fcp safety recalls`

---

### 3. Update README for Video Demo ⚡ (10 min)
**Why:** Will show README in video
**Status:** ❌ Not started

**Add to README.md:**
```markdown
# FCP CLI

Command-line interface for the [Food Context Protocol](https://fcp.dev) - an open standard enabling AI agents to understand food context.

## Quick Start

```bash
# Install
pip install fcp-cli  # (or: git clone + make install)

# Configure (just need server URL)
export FCP_SERVER_URL=https://api.fcp.dev
export FCP_USER_ID=demo

# Try it
fcp --help
```

## Demo Commands

```bash
# 1. Log a meal
fcp log meal "Spicy Ramen" --venue "Ippudo"

# 2. Search your history
fcp search query "ramen"

# 3. Get AI meal suggestions
fcp suggest meal --style "japanese"

# 4. Check food safety
fcp safety recalls --query "lettuce"

# 5. Research food topics
fcp research ask "Benefits of fermented foods?"
```

## Features

- 🍱 **60+ Commands** - Logging, search, suggestions, safety, research, recipes, pantry, and more
- 🤖 **Gemini 3 Powered** - Multimodal analysis, grounding, thinking
- 🔗 **FCP Protocol** - Command-line access to core FCP features
- 📦 **Type-Safe** - Pydantic models throughout
- ✨ **Rich Output** - Beautiful terminal formatting
- 🔧 **13 Command Groups** - Organized by feature area

## Links

- **Protocol:** https://github.com/Food-Context-Protocol/fcp
- **Server:** https://github.com/Food-Context-Protocol/fcp-gemini-server
- **Docs:** https://fcp.dev/docs
```

---

### 4. Test Demo Flow ⚡ (10 min)
**Why:** Must work in video
**Status:** ❌ Not started

**Demo Script (90 seconds):**
```bash
# Server must be running: https://api.fcp.dev or localhost:8080

# Show help
fcp --help

# Log meals
fcp log meal "Tonkotsu Ramen" --venue "Ippudo"
fcp log meal "Margherita Pizza"

# Search
fcp search query "ramen"

# AI suggestions
fcp suggest meal --style "japanese"

# Safety check
fcp safety recalls --query "lettuce"

# Research
fcp research ask "What are the health benefits of fermented foods?"
```

**Verify:**
- No crashes
- Output looks good
- < 90 seconds total

---

## ❌ SKIP FOR DEVPOST

**Don't waste time on:**
- ❌ Analytics (no PostHog, no Sentry)
- ❌ Test coverage (not judged on tests)
- ❌ CI/CD (not needed for demo)
- ❌ Documentation (README is enough)
- ❌ Async batch operations (demo uses single commands)
- ❌ Configuration files (env vars work fine)
- ❌ Progress bars (demo is quick)
- ❌ Caching (not needed)

---

## ✅ Checklist

### Tonight (50 min)
- [ ] Add `demo_safe` decorator (20 min)
- [ ] Update --help examples (20 min)
- [ ] Update README (10 min)

### Tomorrow Morning (10 min)
- [ ] Test demo script 3x (10 min)
- [ ] Time the demo (< 90 sec)

### Before Submission
- [ ] Demo script works flawlessly
- [ ] README looks good
- [ ] No crashes during demo
- [ ] CLI mentioned in video (show `fcp --help`)

---

## 🎬 CLI in Video Script

**Duration:** 15-20 seconds of 3-minute video

**Show:**
1. Terminal with `fcp --help` (5 sec)
2. Run 2-3 demo commands (10 sec)
3. Show rich output formatting (5 sec)

**Say (OPTION A - Recommended):**
> "FCP CLI provides command-line access to core FCP features. With 60+ commands across 13 groups, developers can log meals, search history, get AI suggestions, and check food safety - all powered by Gemini 3 from the terminal."

**Say (OPTION B - If all 42 tools added):**
> "FCP CLI provides full 1-1 access to all 40+ server MCP tools. From meal logging to recipe extraction to food safety - everything the server can do, the CLI exposes via command-line."

**Current reality:** Use Option A (69% coverage of server tools)

---

## 🔗 Integration with Server

**CLI connects to:** https://api.fcp.dev (or localhost:8080 for dev)

**Environment:**
```bash
FCP_SERVER_URL=https://api.fcp.dev
FCP_USER_ID=demo
```

**Make sure:**
- Server is deployed and running
- api.fcp.dev is accessible
- Demo user works

---

## 📊 Success Criteria

- [ ] CLI mentioned in video
- [ ] README shows clear examples
- [ ] Demo commands work without errors
- [ ] Links to main fcp-gemini-server repo
- [ ] Part of Food-Context-Protocol GitHub org

---

## ⏰ Time Budget

| Task | Time | When |
|------|------|------|
| Error handling | 20 min | Tonight |
| Help text | 20 min | Tonight |
| README | 10 min | Tonight |
| Test demo | 10 min | Tomorrow |
| **TOTAL** | **60 min** | |

---

## 🎯 CLI's Role in Submission

**Primary:** Show FCP as a complete ecosystem
- ✅ Protocol spec (fcp repo)
- ✅ Reference server (fcp-gemini-server) - **40+ MCP tools**
- ✅ **CLI tool** (fcp-cli) - **60+ commands, 69% server coverage** ← You are here
- ✅ SDKs (python-sdk, typescript-sdk)

**In Video:**
- Brief mention (15-20 sec)
- Show it works
- Highlight developer experience
- **Say:** "CLI provides command-line access to **core FCP features**" (not "all 40+ tools")

**Coverage:**
- ✅ 100% of nutrition, inventory, recipes, safety features
- ✅ All demo-worthy commands work
- ❌ Some advanced features (publishing, connectors) are server-only

**Not the star** - Server is the main demo, CLI is supporting evidence of ecosystem completeness.

---

**Last Updated:** February 8, 2026
**Deadline:** February 9, 2026 at 5:00 PM PT
**Total CLI Work:** < 1 hour
