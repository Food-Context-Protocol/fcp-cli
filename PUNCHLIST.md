# FCP CLI - Implementation Punchlist

**Last Updated:** February 8, 2026
**Status:** Pre-Launch Improvements

---

## 🔴 HIGH PRIORITY (Pre-Launch)

### 1. Add PostHog Analytics Integration
**Source:** Missing from foodlog-cli
**Effort:** 2 hours
**Impact:** Product analytics and usage tracking

**Why:** Track CLI command usage, user flows, and adoption metrics.

**Implementation:**
```bash
# 1. Add dependency
uv add posthog

# 2. Create service file
touch src/fcp_cli/services/posthog.py
```

**Port from foodlog-cli:**
- File: `/Users/jwegis/Projects/foodlog-cli/src/foodlog/cli/services/posthog.py`
- Update namespace: `foodlog.cli` → `fcp.cli`
- Update service name: `"foodlog-cli"` → `"fcp-cli"`

**Usage:**
```python
from fcp.cli.services.posthog import track_command

@app.command()
def meal(photo: Path):
    track_command(user_id, "log_meal", {"has_photo": True})
    # ... rest of command
```

**Configuration:**
```bash
# .env.example
POSTHOG_API_KEY=phc_...
POSTHOG_HOST=https://us.i.posthog.com
```

**Files to Modify:**
- New: `src/fcp_cli/services/posthog.py`
- Modified: All command files (add tracking calls)
- Modified: `.env.example`
- Modified: `README.md` (document POSTHOG_API_KEY)

---

### 2. Improve Error Handling and Custom Exceptions
**Source:** foodlog-cli CODE_REVIEW.md recommendations
**Effort:** 3 hours
**Impact:** Better error messages and debugging

**Current Issue:** Generic exception handling

**Improvements Needed:**
- Consistent error handling across all commands
- Better error messages for common failures
- Structured error logging

**Implementation:**

Update `src/fcp_cli/services/fcp_errors.py`:
```python
# Add more specific error types
class FcpValidationError(FcpError):
    """Input validation failed."""
    pass

class FcpTimeoutError(FcpError):
    """Request timed out."""
    pass

class FcpQuotaExceededError(FcpError):
    """User quota exceeded."""
    pass
```

Add error handler decorator:
```python
# src/fcp_cli/utils.py
def handle_fcp_errors(func):
    """Decorator to standardize error handling."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FcpAuthError:
            console.print("[red]Authentication failed. Check your auth token.[/red]")
            raise typer.Exit(1)
        except FcpRateLimitError as e:
            console.print(f"[yellow]Rate limited. Retry after {e.retry_after}s[/yellow]")
            raise typer.Exit(1)
        except FcpConnectionError:
            console.print("[red]Cannot connect to FCP server. Is it running?[/red]")
            raise typer.Exit(1)
    return wrapper
```

**Files to Modify:**
- Modified: `src/fcp_cli/services/fcp_errors.py`
- Modified: `src/fcp_cli/utils.py` (add decorator)
- Modified: All command files (use decorator)

---

## 🟡 MEDIUM PRIORITY (Week 1-2)

### 3. Async Batch Operations
**Source:** Original review recommendation #3
**Effort:** 4 hours
**Impact:** 10x performance for bulk operations

**Problem:** Sequential processing for batch operations

**Current:**
```python
# pantry.py
async def sync(file: Path):
    items = load_from_file(file)
    for item in items:  # Sequential!
        await client.add_to_pantry(item)
```

**Solution:** Parallel processing with progress tracking

**Implementation:**

Create `src/fcp_cli/async_utils.py`:
```python
import asyncio
from typing import TypeVar, Callable, List, Any
from rich.progress import Progress

T = TypeVar('T')

async def batch_execute(
    items: List[Any],
    handler: Callable[[Any], Any],
    *,
    max_concurrent: int = 10,
    show_progress: bool = True,
    description: str = "Processing"
) -> List[T]:
    """Execute async operations in batches with progress tracking."""
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_handler(item):
        async with semaphore:
            try:
                return await handler(item)
            except Exception as e:
                return {"error": str(e), "item": item}

    tasks = [bounded_handler(item) for item in items]

    if show_progress:
        with Progress() as progress:
            task = progress.add_task(f"[cyan]{description}...", total=len(tasks))
            results = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                progress.advance(task)
            return results
    else:
        return await asyncio.gather(*tasks)
```

**Commands to Update:**
1. `pantry.py` - `sync` command
2. `log.py` - `import` command (if exists)
3. `recipes.py` - batch operations
4. `profile.py` - sync operations

**Example Usage:**
```python
from fcp.cli.async_utils import batch_execute

@app.command()
def sync(file: Path, max_concurrent: int = typer.Option(10)):
    """Sync pantry items from file."""
    items = _load_items(file)

    async def sync_one(item):
        async with FcpClient() as client:
            return await client.add_to_pantry(**item)

    results = run_async(batch_execute(
        items,
        sync_one,
        max_concurrent=max_concurrent,
        description="Syncing pantry"
    ))

    _display_results(results)
```

**Files to Modify:**
- New: `src/fcp_cli/async_utils.py`
- Modified: `src/fcp_cli/commands/pantry.py`
- Modified: `src/fcp_cli/commands/log.py`
- Modified: `src/fcp_cli/commands/recipes.py`
- Modified: `src/fcp_cli/commands/profile.py`

---

### 4. Media Resolution CLI Exposure
**Source:** Original review recommendation #4
**Effort:** 2 hours
**Impact:** Cost optimization and performance control

**Problem:** No user control over image resolution for AI processing

**Solution:** Add `--resolution` flag to all media-processing commands

**Implementation:**

Create resolution enum in `src/fcp_cli/utils.py`:
```python
from enum import Enum

class MediaResolution(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    def __str__(self):
        return self.value
```

**Commands to Update:**

| Command | Current Status | Action |
|---------|---------------|--------|
| `fcp log meal <photo>` | ✅ Check | Verify implementation |
| `fcp recipe extract <image>` | ✅ Check | Verify implementation |
| `fcp pantry scan <photo>` | ❌ Missing | Add flag |
| `fcp discover ingredients <photo>` | ❌ Missing | Add flag |
| `fcp profile taste-from-photo` | ❌ Missing | Add flag |

**Example Implementation:**
```python
@app.command()
def meal(
    photo: Path,
    resolution: MediaResolution = typer.Option(
        MediaResolution.MEDIUM,
        help="Image resolution: low (fast/cheap), medium (balanced), high (accurate/expensive)"
    )
):
    """Log a meal from a photo."""
    async with FcpClient() as client:
        result = await client.log_meal_from_photo(
            photo=photo,
            media_resolution=resolution.value
        )
```

**Documentation Update:**
Add to README.md:
```markdown
## Media Resolution Options

Control cost and speed of image processing:

- `--resolution low` - Fast, cheaper ($0.01), 80% accuracy
- `--resolution medium` - Balanced ($0.03), 90% accuracy (default)
- `--resolution high` - Slow, expensive ($0.10), 98% accuracy

Example:
```bash
fcp log meal photo.jpg --resolution low   # Quick scan
fcp recipe extract photo.jpg --resolution high  # Detailed extraction
```
```

**Files to Modify:**
- Modified: `src/fcp_cli/utils.py` (add enum)
- Modified: `src/fcp_cli/commands/log.py` (verify/add)
- Modified: `src/fcp_cli/commands/recipes.py` (verify/add)
- Modified: `src/fcp_cli/commands/pantry.py` (add)
- Modified: `src/fcp_cli/commands/discover.py` (add)
- Modified: `src/fcp_cli/commands/profile.py` (add)
- Modified: `README.md` (document)

---

### 5. Add Configuration File Support
**Source:** Best practice from foodlog-cli analysis
**Effort:** 3 hours
**Impact:** Better UX for power users

**Problem:** All config via environment variables

**Solution:** Support `~/.fcp/config.yaml` for persistent settings

**Implementation:**

Create `src/fcp_cli/config_file.py`:
```python
from pathlib import Path
import yaml
from dataclasses import dataclass

@dataclass
class FcpConfig:
    server_url: str = "http://localhost:8080"
    user_id: str = "demo"
    media_resolution: str = "medium"
    max_concurrent: int = 10
    timeout: int = 30

    @classmethod
    def load(cls) -> "FcpConfig":
        """Load config from file or environment."""
        config_file = Path.home() / ".fcp" / "config.yaml"

        if config_file.exists():
            with open(config_file) as f:
                data = yaml.safe_load(f)
                return cls(**data)

        # Fallback to environment variables
        return cls(
            server_url=os.getenv("FCP_SERVER_URL", "http://localhost:8080"),
            user_id=os.getenv("FCP_USER_ID", "demo"),
        )

    def save(self):
        """Save config to file."""
        config_file = Path.home() / ".fcp" / "config.yaml"
        config_file.parent.mkdir(exist_ok=True)

        with open(config_file, "w") as f:
            yaml.dump(asdict(self), f)
```

Add `config` command:
```python
# src/fcp_cli/commands/config.py
app = typer.Typer()

@app.command("show")
def show():
    """Show current configuration."""
    config = FcpConfig.load()
    # Display config

@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Config key"),
    value: str = typer.Argument(..., help="Config value")
):
    """Set a configuration value."""
    config = FcpConfig.load()
    setattr(config, key, value)
    config.save()
```

**Files to Modify:**
- New: `src/fcp_cli/config_file.py`
- New: `src/fcp_cli/commands/config.py`
- Modified: `src/fcp_cli/config.py` (use FcpConfig)
- Modified: `pyproject.toml` (add pyyaml dependency)

---

## 🟢 LOW PRIORITY (Month 1)

### 6. Add Progress Bars for Long Operations
**Effort:** 2 hours
**Impact:** Better UX during long-running commands

**Implementation:** Use Rich progress bars

**Example:**
```python
from rich.progress import Progress, SpinnerColumn, TextColumn

@app.command()
def extract(video: Path):
    """Extract recipe from video."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Analyzing video...", total=None)
        result = await client.extract_recipe_from_video(video)
```

**Files to Modify:**
- All command files with long-running operations

---

### 7. Offline Mode / Response Caching
**Effort:** 4 hours
**Impact:** Faster repeated queries, offline access

**Implementation:**

Create `src/fcp_cli/cache.py`:
```python
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta

class ResponseCache:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or Path.home() / ".fcp" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, max_age: timedelta = timedelta(hours=1)):
        """Get cached response if not expired."""
        cache_file = self.cache_dir / self._hash(key)

        if not cache_file.exists():
            return None

        with open(cache_file) as f:
            data = json.load(f)

        cached_at = datetime.fromisoformat(data["cached_at"])
        if datetime.now() - cached_at > max_age:
            return None

        return data["response"]

    def set(self, key: str, response: Any):
        """Cache response."""
        cache_file = self.cache_dir / self._hash(key)

        with open(cache_file, "w") as f:
            json.dump({
                "cached_at": datetime.now().isoformat(),
                "response": response
            }, f)

    def _hash(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()
```

**Usage:**
```python
cache = ResponseCache()

@app.command()
def get(recipe_id: str, use_cache: bool = typer.Option(True)):
    """Get recipe by ID."""
    cache_key = f"recipe:{recipe_id}"

    if use_cache:
        cached = cache.get(cache_key)
        if cached:
            console.print("[dim](from cache)[/dim]")
            return cached

    result = await client.get_recipe(recipe_id)
    cache.set(cache_key, result)
    return result
```

**Files to Modify:**
- New: `src/fcp_cli/cache.py`
- Modified: `src/fcp_cli/commands/recipes.py`
- Modified: Other read-heavy commands

---

### 8. Shell Completion Enhancement
**Source:** foodlog-cli has this feature
**Effort:** 1 hour
**Impact:** Better developer experience

**Current:** Basic Typer completion

**Enhancement:** Document and test completion for all shells

**Files to Update:**
- `README.md` - Add shell completion section
- Test completion on Bash, Zsh, Fish

**Documentation to Add:**
```markdown
## Shell Completion

FCP CLI supports tab completion for all shells:

```bash
# Install completion (auto-detects shell)
fcp --install-completion

# Manual installation
fcp --show-completion bash >> ~/.bashrc
fcp --show-completion zsh >> ~/.zshrc
fcp --show-completion fish >> ~/.config/fish/completions/fcp.fish
```

After installation, restart your shell or source your profile.
```

---

## 📚 DOCUMENTATION IMPROVEMENTS

### 9. Add Architecture Documentation
**Source:** foodlog-cli has excellent ARCHITECTURE.md
**Effort:** 2 hours
**Impact:** Easier onboarding for contributors

**Port from foodlog-cli:**
- Create `ARCHITECTURE.md` documenting:
  - System overview
  - Directory structure
  - Key components
  - Data flow
  - Design decisions

**Files to Create:**
- New: `ARCHITECTURE.md`

---

### 10. Add Developer Setup Guide
**Source:** foodlog-cli has docs/DEV_SETUP.md
**Effort:** 1 hour
**Impact:** Faster contributor onboarding

**Create:** `docs/DEV_SETUP.md` with:
- Development environment setup
- API key configuration
- Running tests
- Contributing guidelines

**Files to Create:**
- New: `docs/` directory
- New: `docs/DEV_SETUP.md`

---

### 11. Add Code Review Document
**Source:** foodlog-cli has CODE_REVIEW.md
**Effort:** 1 hour (after improvements implemented)
**Impact:** Quality assurance documentation

**Create:** `CODE_REVIEW.md` documenting:
- Architecture assessment
- Code quality metrics
- Testing coverage
- Recommendations implemented

**Files to Create:**
- New: `CODE_REVIEW.md`

---

## 🧪 TESTING IMPROVEMENTS

### 12. Increase Test Coverage
**Source:** foodlog-cli has 100% coverage
**Effort:** 8 hours
**Impact:** Production confidence

**Current:** Unknown coverage

**Target:** 90%+ coverage

**Areas to Test:**
- All command happy paths
- Error handling scenarios
- Edge cases (empty inputs, large files, etc.)
- Network failures
- Rate limiting
- Authentication failures

**Implementation:**
```bash
# Add coverage tools
uv add --dev pytest-cov

# Run with coverage
pytest --cov=fcp_cli --cov-report=html --cov-report=term

# View coverage
open htmlcov/index.html
```

**Files to Modify:**
- New: `tests/` comprehensive test suite
- Modified: `pyproject.toml` (add coverage config)
- Modified: `.github/workflows/ci.yml` (add coverage reporting)

---

### 13. Add Mutation Testing
**Source:** foodlog-cli uses mutmut
**Effort:** 2 hours
**Impact:** Test quality assurance

**Implementation:**
```bash
# Add mutmut
uv add --dev mutmut

# Create config
# mutmut_config.py
def pre_mutation(context):
    # Skip certain files
    if "test_" in context.filename:
        context.skip = True
```

**Files to Modify:**
- New: `mutmut_config.py`
- Modified: `Makefile` (add mutation test target)

---

## 🔧 TOOLING & CI/CD

### 14. Add Pre-commit Hooks
**Source:** foodlog-cli has comprehensive hooks
**Effort:** 1 hour
**Impact:** Consistent code quality

**Port from foodlog-cli:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Files to Create:**
- New: `.pre-commit-config.yaml`

---

### 15. Add GitHub Actions CI
**Source:** foodlog-cli has robust CI
**Effort:** 2 hours
**Impact:** Automated testing and quality checks

**Implementation:**
```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.13"

      - name: Install uv
        run: pip install uv

      - name: Install dependencies
        run: uv sync

      - name: Run tests
        run: uv run pytest --cov

      - name: Run linter
        run: uv run ruff check .

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

**Files to Create:**
- New: `.github/workflows/ci.yml`

---

## 📊 SUMMARY

### By Priority

| Priority | Items | Total Hours |
|----------|-------|-------------|
| 🔴 High | 2 | 5h |
| 🟡 Medium | 5 | 14h |
| 🟢 Low | 3 | 7h |
| 📚 Docs | 3 | 4h |
| 🧪 Testing | 2 | 10h |
| 🔧 Tooling | 2 | 3h |
| **TOTAL** | **17** | **43h** |

### Quick Wins (< 2 hours each)

1. ✅ Shell completion docs (1h)
2. ✅ Pre-commit hooks (1h)
3. ✅ Dev setup guide (1h)
4. ✅ Progress bars (2h)
5. ✅ Media resolution (2h)
6. ✅ PostHog integration (2h)

### High Impact (Must Do)

1. ✅ PostHog analytics
2. ✅ Async batch operations
3. ✅ Error handling improvements
4. ✅ Test coverage to 90%+

### Nice to Have (Month 1)

1. Configuration file support
2. Response caching
3. Architecture docs
4. Mutation testing

---

## 🎯 Recommended Implementation Order

### Week 1 (8 hours)
1. PostHog analytics (2h)
2. Error handling improvements (3h)
3. Pre-commit hooks (1h)
4. Media resolution (2h)

### Week 2 (8 hours)
1. Async batch operations (4h)
2. Configuration file support (3h)
3. Dev setup guide (1h)

### Week 3-4 (12 hours)
1. Test coverage improvements (8h)
2. CI/CD setup (2h)
3. Architecture docs (2h)

### Month 1 (15 hours)
1. Progress bars (2h)
2. Response caching (4h)
3. Mutation testing (2h)
4. Shell completion enhancement (1h)
5. Code review document (1h)
6. Buffer (5h)

---

## ✅ Done When

- [ ] All HIGH priority items completed
- [ ] Test coverage > 90%
- [ ] CI/CD pipeline green
- [ ] Documentation complete
- [ ] All quick wins implemented
- [ ] PostHog tracking live in production

---

**Last Updated:** February 8, 2026
**Next Review:** After Week 1 completion
