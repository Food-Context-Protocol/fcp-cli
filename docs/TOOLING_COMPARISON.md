# Tooling Comparison: fcp-cli vs fcp-gemini-server

## Overview

This document compares the development tooling between fcp-cli and fcp-gemini-server to identify opportunities for alignment and improvement.

---

## Current State

### fcp-cli (Current Project)

**Test Coverage**: ✅ 100% (2,696 statements, 614 branches)

**Tools**:
- `pytest` + `pytest-asyncio` - Testing framework
- `pytest-cov` - Coverage reporting
- `ruff` - Linting and formatting
- `prek` - Pre-commit hook management
- `typer` - CLI framework
- `rich` - Terminal output

**Missing** (compared to fcp-gemini-server):
- ❌ Type checker (no `ty`, `mypy`, or `pyright`)
- ❌ Property-based testing (`hypothesis`)
- ❌ Test timeouts (`pytest-timeout`)
- ❌ Time mocking (`freezegun`)
- ❌ HTTP mocking (`respx`)
- ❌ Code quality analyzer (`sourcery`)
- ❌ Makefile for development workflows
- ❌ Test markers/categories

### fcp-gemini-server (Reference)

**Test Coverage**: ✅ 100% (with pragmatic omissions)

**Tools**:
- `pytest` + `pytest-asyncio` + `pytest-timeout` - Testing
- `pytest-cov` - Coverage
- `ruff` - Linting/formatting
- `ty` - Type checking (Rust-based, fast)
- `hypothesis` - Property-based testing
- `freezegun` - Time mocking
- `respx` - HTTP mocking
- `sourcery` - Code quality
- `prek` - Pre-commit hooks
- **Makefile** - Development workflow automation

**Test Organization**:
```python
markers = [
    "small: fast, hermetic unit tests",
    "medium: tests that may touch filesystem or heavier fixtures",
    "large: slow tests (integration/e2e)",
    "integration: tests that require external services",
    "e2e: end-to-end tests",
    "slow: explicitly slow tests",
    "property: property-based tests",
    "sdk: tests that exercise the SDK client surface",
    "network: tests that require network access",
]
```

---

## Recommended Additions to fcp-cli

### Priority 1: Essential Tools

#### 1. **Makefile** (Highest Priority)

The fcp-gemini-server uses a Makefile for standardized development workflows.

**Benefits**:
- Standardized commands across projects
- Self-documenting (`make help`)
- Easier onboarding for new developers
- Consistent with fcp-gemini-server patterns

**Suggested fcp-cli Makefile targets**:
```makefile
help              ## Show this help message (default)
install           ## Install all dependencies (uv sync)
test              ## Run all tests
test-quick        ## Run tests without coverage for speed
coverage          ## Run tests with coverage report
lint              ## Lint code with ruff
lint-fix          ## Auto-fix lint errors
format            ## Format code with ruff
format-check      ## Check formatting without changes
check             ## Run all checks (format, lint, coverage)
prek              ## Run prek hooks on all files
clean             ## Remove temporary files and caches
```

#### 2. **pytest-timeout** (High Priority)

Prevents tests from hanging indefinitely.

**Add to pyproject.toml**:
```toml
[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.0.0",
    "pytest-timeout>=2.4.0",  # Add this
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
timeout = 10  # Global timeout: 10 seconds per test
timeout_method = "thread"
```

**Why**: Some async tests can hang if network calls fail or mocks are incorrect. Timeouts prevent CI/CD pipeline hangs.

#### 3. **Test Markers** (High Priority)

Organize tests by speed and purpose.

**Add to pyproject.toml**:
```toml
[tool.pytest.ini_options]
markers = [
    "asyncio: async test marker",
    "unit: fast, isolated unit tests",
    "integration: tests involving multiple components",
    "slow: tests that take >1s to run",
    "cli: command-line interface tests",
    "network: tests that make network calls",
]
```

**Usage**:
```bash
pytest -m "unit and not slow"     # Fast tests only
pytest -m "not network"           # Skip network tests
pytest -m "cli"                   # CLI tests only
```

### Priority 2: Recommended Tools

#### 4. **ty** (Type Checker)

Rust-based type checker - fast and focused.

**Add to pyproject.toml**:
```toml
[dependency-groups]
dev = [
    "prek>=0.3.2",
    "ty>=0.0.14",  # Add this
]

[tool.ty]
# ty type checker configuration

[tool.ty.rules]
# Ignore dynamic types from external libraries
unresolved-attribute = "ignore"
# Ignore optional kwargs
missing-argument = "ignore"
```

**Why**: Type checking catches bugs early. `ty` is faster than mypy and integrates well with modern Python.

**Alternative**: If you prefer more established tools, use `mypy` or `pyright`.

#### 5. **freezegun** (Time Mocking)

Mock datetime for deterministic tests.

**Add to dependencies**:
```toml
[project.optional-dependencies]
dev = [
    # ... existing ...
    "freezegun>=1.5.5",
]
```

**Usage**:
```python
from freezegun import freeze_time

@freeze_time("2026-02-08 12:00:00")
def test_streak_calculation_today():
    """Test streak calculation with fixed time."""
    # Time is frozen at Feb 8, 2026 12:00
    result = calculate_streak()
    assert result == 5
```

**Why**: Time-dependent tests (streaks, "today", "yesterday") become deterministic.

#### 6. **respx** (HTTP Mocking)

Mock HTTP requests for async httpx tests.

**Add to dependencies**:
```toml
[project.optional-dependencies]
dev = [
    # ... existing ...
    "respx>=0.22.0",
]
```

**Usage**:
```python
import respx
from httpx import AsyncClient

@respx.mock
async def test_api_client_retry():
    """Test client retry logic with respx."""
    # Mock endpoint
    route = respx.get("https://api.fcp.dev/meals").mock(
        side_effect=[
            httpx.Response(500),  # First call fails
            httpx.Response(200, json={"meals": []}),  # Retry succeeds
        ]
    )

    async with AsyncClient() as client:
        response = await client.get("https://api.fcp.dev/meals")
        assert response.status_code == 200
```

**Why**: Better than manual AsyncMock for HTTP testing. Cleaner syntax, less boilerplate.

### Priority 3: Advanced Tools

#### 7. **hypothesis** (Property-Based Testing)

Generate test cases automatically.

**Add to dependencies**:
```toml
[dependency-groups]
dev = [
    # ... existing ...
    "hypothesis>=6.151.5",
]
```

**Usage**:
```python
from hypothesis import given, strategies as st

@given(st.text(min_size=1, max_size=100))
def test_dish_name_validation_properties(dish_name):
    """Test dish name validation with random strings."""
    result = validate_dish_name(dish_name)
    # Properties that should always hold
    assert isinstance(result, bool)
    if result:
        assert 1 <= len(dish_name) <= 100
```

**Why**: Finds edge cases you didn't think of. Generates hundreds of test cases automatically.

#### 8. **sourcery** (Code Quality)

AI-powered code suggestions.

**Add to dependencies**:
```toml
[dependency-groups]
dev = [
    # ... existing ...
    "sourcery>=1.43.0",
]
```

**Why**: Suggests refactorings and improvements. Optional but useful for maintaining code quality.

---

## Alignment Strategy

### Phase 1: Quick Wins (1-2 hours)

1. ✅ Create Makefile with common targets
2. ✅ Add pytest-timeout to prevent hanging tests
3. ✅ Add test markers for organization
4. ✅ Update documentation

### Phase 2: Enhanced Testing (2-4 hours)

5. ⏭️ Add freezegun for time-based tests
6. ⏭️ Add respx for HTTP mocking
7. ⏭️ Refactor tests to use new tools
8. ⏭️ Add ty type checker

### Phase 3: Advanced Features (Optional)

9. ⏭️ Add hypothesis for property-based testing
10. ⏭️ Add sourcery for code quality suggestions
11. ⏭️ Set up CI/CD with all tools integrated

---

## Pre-commit Hook Comparison

### fcp-gemini-server (Makefile-based)

```yaml
- id: format
  name: make format
  entry: make format

- id: check
  name: make lint typecheck
  entry: make lint typecheck

- id: coverage
  name: make coverage
  entry: make coverage
  stages: [pre-push]
```

**Pros**:
- Makefile provides consistent interface
- Easy to run locally: `make check`
- Self-documenting

### fcp-cli (Direct commands)

```yaml
- id: ruff
  args: [--fix]

- id: ruff-format

- id: pytest-check
  entry: uv run pytest --cov=... --cov-fail-under=100.0 tests/
  stages: [pre-push]
```

**Pros**:
- Direct tool invocation
- Slightly faster (no Make overhead)
- Explicit arguments visible

**Recommendation**: Add Makefile but keep current pre-commit hooks. Developers can use either:
- `make check` - for manual development
- Git hooks - for automatic enforcement

---

## Implementation Priority

**Must Have** (Implement Soon):
1. ✅ **Makefile** - Standardize development workflow
2. ✅ **pytest-timeout** - Prevent hanging tests
3. ✅ **Test markers** - Organize test execution

**Should Have** (Next Sprint):
4. ⏭️ **freezegun** - Deterministic time-based tests
5. ⏭️ **respx** - Better HTTP mocking
6. ⏭️ **ty** - Type checking

**Nice to Have** (Future):
7. ⏭️ **hypothesis** - Property-based testing
8. ⏭️ **sourcery** - Code quality suggestions

---

## Conclusion

The fcp-gemini-server has a more mature development toolchain with better test organization and quality tools. Adopting these tools in fcp-cli will:

1. **Improve developer experience** - Standardized Makefile commands
2. **Increase test reliability** - Timeouts prevent hanging, freezegun makes tests deterministic
3. **Better test organization** - Markers allow running test subsets
4. **Align with fcp-gemini-server** - Consistent patterns across projects
5. **Maintain 100% coverage** - All tools support the coverage goal

**Next Steps**: Start with Phase 1 (Makefile, pytest-timeout, markers) to get quick wins without major disruption.

---

**Last Updated**: 2026-02-08
**Status**: ⏭️ Ready for Implementation
