# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FCP CLI is a command-line interface for the Food Context Protocol - a production CLI tool with 60+ commands for food logging, AI-powered meal suggestions, recipe management, and food safety checks. It uses a hybrid architecture combining local PydanticAI agents with HTTP REST calls to a remote FCP server.

## Development Commands

### Setup
```bash
# Install dependencies with uv (required)
uv sync --dev

# Install pre-commit hooks (enforces 100% coverage on push)
prek install
```

### Testing
```bash
# Run all tests (1,171 tests, takes ~30s)
uv run pytest

# Quick test run without coverage
uv run pytest -x -q

# Run specific test markers
uv run pytest -m unit              # Fast unit tests only
uv run pytest -m "unit and not network"  # Skip HTTP mocking tests
uv run pytest -m cli               # CLI command tests
uv run pytest -m integration       # Multi-component workflows
uv run pytest -m property          # Hypothesis property-based tests

# Run coverage with HTML report
make coverage-html

# Run single test file
uv run pytest tests/unit/test_log.py -v
```

### Code Quality
```bash
# Format code
uv run ruff format src/ tests/

# Lint and auto-fix
uv run ruff check --fix src/ tests/

# Type check (source only, not tests)
uv run ty check src/

# Run all checks (format, lint, typecheck, 100% coverage)
make check
```

### Local CLI Testing
```bash
# Run CLI locally
uv run fcp --help

# Test specific commands
uv run fcp log add "Test meal" --meal-type lunch
uv run fcp profile show
uv run fcp search query "ramen" --limit 5
```

## Architecture

### Hybrid Execution Model

The CLI uses TWO distinct execution paths:

1. **Local PydanticAI Agents** (`src/fcp_cli/agents/`)
   - Direct calls to Gemini API via google-genai SDK
   - Used for: `fcp research ask` command
   - Faster, no server dependency
   - Example: `research.py` creates Agent with tools for deep_research

2. **HTTP REST Client** (`src/fcp_cli/services/`)
   - Calls remote FCP server at api.fcp.dev
   - Used for: most other commands (log, search, profile, recipes, etc.)
   - Centralized, scalable, supports authentication
   - HTTP/2 enabled with connection pooling for performance

**Key distinction**: Agents run LLM logic locally. HTTP client delegates to server.

### Directory Structure

```
src/fcp_cli/
├── main.py                    # Typer app with 13 command groups registered
├── config.py                  # pydantic-settings config (FCP_SERVER_URL, FCP_USER_ID, FCP_AUTH_TOKEN)
├── utils.py                   # Shared utilities (run_async, image processing, validation)
├── commands/                  # 13 Typer command groups
│   ├── log.py                 # Food logging (add, list, batch with parallel processing)
│   ├── search.py              # Search food history
│   ├── profile.py             # User taste profile
│   ├── recipes.py             # Recipe management
│   ├── pantry.py              # Pantry inventory
│   ├── research.py            # AI research (calls local agent)
│   └── ...                    # 7 more command groups
├── services/                  # HTTP client layer
│   ├── fcp_client_core.py     # Core HTTP client with retry logic, connection pooling
│   ├── fcp_client_meals.py    # Meal-specific API calls
│   ├── fcp_client_recipes.py  # Recipe API calls
│   ├── fcp_client_pantry.py   # Pantry API calls
│   ├── fcp_errors.py          # Custom exceptions (FcpNotFoundError, FcpAuthError, etc.)
│   ├── models.py              # Pydantic models for API responses
│   └── logfire_service.py     # Structured logging/tracing
└── agents/                    # PydanticAI agents for local execution
    └── research.py            # Research agent with tools (deep_research, search_food_logs)

tests/
├── unit/                      # 1,157 isolated tests
│   ├── test_*.py              # Feature-based test files
│   └── services/              # Service layer tests with HTTP mocking (respx)
└── integration/               # 10 end-to-end workflow tests
    ├── test_food_logging_workflow.py
    ├── test_recipe_workflow.py
    └── test_profile_workflow.py
```

### Key Patterns

**Command Structure**: All commands in `commands/` follow this pattern:
```python
app = typer.Typer()

@app.command("add")
@demo_safe  # Decorator checks auth for write operations
def add(description: str, ...) -> None:
    """Command docstring shown in --help"""
    # 1. Create progress spinner (Rich)
    # 2. Call run_async() to wrap async service calls
    # 3. Display results with Rich tables/panels
    # 4. Handle exceptions (FcpNotFoundError, FcpServerError, etc.)
```

**Service Layer**: HTTP clients use async/await with retry logic:
- `FcpClientCore`: Base client with retry, auth headers, HTTP/2 pooling
- Specialized clients inherit: `FcpClientMeals`, `FcpClientRecipes`, `FcpClientPantry`
- All service calls return Pydantic models from `models.py`

**Configuration**: Uses `pydantic-settings` with `.env` file support:
- `FCP_SERVER_URL` - Server endpoint (default: http://localhost:8080)
- `FCP_USER_ID` - User identifier (default: "demo")
- `FCP_AUTH_TOKEN` - Optional JWT for authenticated operations

**Async Wrapper**: Commands are sync (Typer requirement). Use `run_async()` from `utils.py` to call async service methods.

**Image Processing**: `log batch` command supports parallel image uploads:
- Auto-resolution detection (low/medium/high) based on file size
- Concurrent uploads with configurable parallelism (--parallel N)
- Base64 encoding with validation

## Testing Philosophy

**100% Coverage is Non-Negotiable**: This project proves AI-era testing achieves 100% branch coverage (614/614 branches). The pre-push hook ENFORCES this via `fail_under = 100.0` in coverage config.

### Critical Testing Rules

1. **Never use `# pragma: no cover`** - If you think code is untestable, refactor it
2. **Test exception handlers** - All try/except blocks must have tests triggering the exception
3. **Mock HTTP calls** - Use `respx` to mock httpx calls in service tests
4. **Use pytest markers** - Tag tests with `@pytest.mark.unit`, `@pytest.mark.cli`, etc.
5. **Integration tests** - Add workflow tests in `tests/integration/` for multi-step user journeys

### Common Test Patterns

**CLI Command Test** (uses CliRunner):
```python
@pytest.mark.cli
def test_log_add_success(runner, mock_fcp_client):
    result = runner.invoke(app, ["add", "Pizza", "--meal-type", "lunch"])
    assert result.exit_code == 0
    assert "Successfully logged" in result.stdout
```

**Service Test with HTTP Mocking** (uses respx):
```python
@pytest.mark.network
async def test_add_meal(respx_mock):
    respx_mock.post("http://localhost:8080/meals").mock(return_value=httpx.Response(200, json={...}))
    client = FcpClientMeals()
    result = await client.add_meal("Pizza", meal_type="lunch")
    assert result.id == "meal-123"
```

**Exception Handler Test**:
```python
def test_command_handles_connection_error(runner, mock_fcp_client):
    mock_fcp_client.add_meal.side_effect = FcpConnectionError("Connection failed")
    result = runner.invoke(app, ["add", "Pizza"])
    assert result.exit_code == 1
    assert "Connection failed" in result.stdout
```

## Common Development Workflows

### Adding a New Command

1. Create command function in appropriate file in `commands/`
2. Register with `@app.command("name")`
3. Add `@demo_safe` decorator if command requires auth
4. Implement using `run_async()` for service calls
5. Add tests in `tests/unit/test_<command_group>.py`
6. Add exception handler tests in `tests/unit/test_exception_handlers.py`
7. Run `make check` to verify 100% coverage maintained

### Adding Service Method

1. Add async method to appropriate client in `services/`
2. Define Pydantic response model in `services/models.py`
3. Add HTTP mocking test using `respx` in `tests/unit/services/`
4. Test error cases (404, 500, network errors)
5. Verify coverage with `make coverage`

### Modifying Existing Code

1. Read existing tests FIRST to understand behavior
2. Make code changes
3. Update tests to match new behavior
4. Run affected tests: `uv run pytest tests/unit/test_<file>.py -v`
5. Run full test suite: `uv run pytest`
6. Pre-push hook will enforce 100% coverage before allowing push

## Important Files

- **pyproject.toml**: Dependencies, pytest config, coverage config (fail_under=100.0), ruff rules
- **.pre-commit-config.yaml**: Hooks for ruff format/lint + 100% coverage enforcement on pre-push
- **docs/TESTING.md**: Comprehensive testing philosophy and strategy documentation
- **Makefile**: Convenient commands for common tasks (make help to see all)

## External Dependencies

- **Typer**: CLI framework (all commands use Typer decorators)
- **Rich**: Terminal formatting (Progress, Table, Panel, Console)
- **httpx**: HTTP client with HTTP/2 support (async)
- **pydantic-ai**: Local agent framework (research command)
- **google-genai**: Gemini API SDK (used by agents)
- **respx**: HTTP mocking for tests (mocks httpx calls)
- **pytest**: Test framework with asyncio support
- **ruff**: Linting and formatting
- **ty**: Type checker (source code only, not tests)

## Development Tips

- **Speed up test runs**: Use `-x` (stop on first failure), `-q` (quiet), or `-m unit` (skip slow tests)
- **Debug failing tests**: Add `-vv` for verbose output, `--tb=short` for shorter tracebacks
- **Image testing**: Place test images in `tests/fixtures/` and reference in tests
- **Auth testing**: Set `FCP_AUTH_TOKEN` env var or use `@demo_safe` decorator bypass in tests
- **Parallel batch testing**: Use `tests/fixtures/batch/` with multiple test images
