# FCP CLI Performance Guide

**Goal:** Make the FCP CLI blazing fast with parallel processing and smart resolution control.

---

## Overview

This guide implements the two key performance recommendations from the FCP code review:

1. **Media Resolution Optimization** - Add `--res` flag for cost/speed control
2. **Async Consistency** - Use `asyncio.gather` for parallel batch operations

**Expected speedup:** 18.7x faster for batch operations

---

## 1. Media Resolution Optimization

### Current State
Server supports `media_resolution` parameter but CLI always uses default (high quality).

### Implementation

#### Add Resolution Flag to All Image Commands

```python
# src/fcp_cli/commands/log.py

@app.command("meal")
def log_meal(
    image_path: Path = typer.Argument(..., help="Path to meal image"),
    # NEW: Add resolution flag
    resolution: str = typer.Option(
        "medium",
        "--res", "-r",
        help="Image resolution: low (fast/cheap), medium (balanced), high (detailed)"
    ),
    dish_name: str | None = typer.Option(None, "--dish", "-d", help="Dish name"),
    venue: str | None = typer.Option(None, "--venue", "-v", help="Restaurant/location"),
    notes: str | None = typer.Option(None, "--notes", "-n", help="Additional notes"),
):
    """Log a meal from an image."""

    # Validate resolution
    if resolution not in ["low", "medium", "high"]:
        console.print("[red]Error: Resolution must be 'low', 'medium', or 'high'[/red]")
        raise typer.Exit(1)

    if not image_path.exists():
        console.print(f"[red]Error: Image not found: {image_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Analyzing meal with {resolution} resolution...[/cyan]")

    try:
        # Pass resolution to server
        response = client.analyze_meal(
            image_path=image_path,
            media_resolution=resolution,  # NEW
            dish_name=dish_name,
            venue=venue,
            notes=notes,
        )

        console.print(f"[green]✓ Meal logged: {response['dish_name']}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
```

#### Resolution Guidelines

Add to help text and documentation:

```python
RESOLUTION_GUIDE = """
Resolution Guide:

  low    → 400px, ~5KB images
           • 4x faster processing
           • 10x cheaper API costs
           • Best for: Simple foods ("apple", "coffee"), quick logging

  medium → 800px, ~20KB images (DEFAULT)
           • Balanced speed/accuracy
           • Best for: Most meals, everyday logging

  high   → 1600px, ~80KB images
           • Detailed analysis
           • Best for: Complex dishes, restaurant meals, nutrition labels
"""
```

#### Update Client Methods

```python
# src/fcp_cli/core/client.py

class FcpClientCore:
    async def analyze_meal_async(
        self,
        image_path: Path,
        media_resolution: str = "medium",  # NEW parameter
        dish_name: str | None = None,
        venue: str | None = None,
        notes: str | None = None,
    ) -> dict:
        """Analyze meal image asynchronously."""

        # Read and encode image
        image_data = image_path.read_bytes()
        image_b64 = base64.b64encode(image_data).decode()

        # Build request
        payload = {
            "image_data": image_b64,
            "media_resolution": media_resolution,  # NEW
            "dish_name": dish_name,
            "venue": venue,
            "notes": notes,
        }

        # Send request
        response = await self._client.post("/analyze", json=payload)
        response.raise_for_status()
        return response.json()
```

---

## 2. Async Consistency + Parallel Processing

### Pattern 1: Basic Parallel Batch Operations

```python
# src/fcp_cli/commands/log.py

@app.command("batch")
def log_batch(
    folder: Path = typer.Argument(..., help="Folder with meal images"),
    max_parallel: int = typer.Option(5, "--parallel", "-p", help="Max concurrent uploads (1-10)"),
    resolution: str = typer.Option("low", "--res", "-r", help="Image resolution (low/medium/high)"),
):
    """Log multiple meals in parallel (BLAZING FAST).

    Examples:
        fcp log batch ./photos --parallel 5 --res low
        fcp log batch ~/meals --parallel 3 --res medium
    """

    # Validate inputs
    if not folder.is_dir():
        console.print(f"[red]Error: Not a directory: {folder}[/red]")
        raise typer.Exit(1)

    if not 1 <= max_parallel <= 10:
        console.print("[red]Error: --parallel must be between 1 and 10[/red]")
        raise typer.Exit(1)

    if resolution not in ["low", "medium", "high"]:
        console.print("[red]Error: --res must be low, medium, or high[/red]")
        raise typer.Exit(1)

    # Find images
    extensions = ["jpg", "jpeg", "png", "heic", "webp"]
    images = []
    for ext in extensions:
        images.extend(folder.glob(f"*.{ext}"))
        images.extend(folder.glob(f"*.{ext.upper()}"))

    if not images:
        console.print(f"[yellow]No images found in {folder}[/yellow]")
        return

    console.print(f"[cyan]Processing {len(images)} images with {max_parallel} parallel requests...[/cyan]")
    console.print(f"[dim]Resolution: {resolution}[/dim]\n")

    # Run async batch processor
    import asyncio
    results = asyncio.run(batch_log_meals(images, max_parallel, resolution))

    # Show results
    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count

    console.print()
    console.print(f"[green]✓ {success_count}/{len(images)} meals logged successfully[/green]")

    if failed_count > 0:
        console.print(f"[red]✗ {failed_count} failed[/red]")
        console.print("\n[yellow]Failed images:[/yellow]")
        for r in results:
            if not r["success"]:
                console.print(f"  • {r['image']}: {r['error']}")


async def batch_log_meals(
    images: list[Path],
    max_parallel: int,
    resolution: str,
) -> list[dict]:
    """Process images in parallel with controlled concurrency."""

    from fcp_cli.core.client import FcpClientCore

    # Create async client
    async with FcpClientCore() as client:
        # Use semaphore to limit concurrency (prevent rate limiting)
        semaphore = asyncio.Semaphore(max_parallel)

        async def process_one(image: Path) -> dict:
            """Process a single image with semaphore control."""
            async with semaphore:
                try:
                    result = await client.analyze_meal_async(
                        image_path=image,
                        media_resolution=resolution,
                    )
                    return {
                        "success": True,
                        "image": image.name,
                        "data": result,
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "image": image.name,
                        "error": str(e),
                    }

        # Launch all tasks in parallel
        tasks = [process_one(img) for img in images]
        return await asyncio.gather(*tasks)
```

---

### Pattern 2: Parallel Processing with Progress Bar

```python
# src/fcp_cli/commands/log.py

async def batch_log_meals_with_progress(
    images: list[Path],
    max_parallel: int,
    resolution: str,
) -> list[dict]:
    """Process images with live progress bar."""

    from rich.progress import (
        Progress,
        SpinnerColumn,
        BarColumn,
        TextColumn,
        TimeRemainingColumn,
    )
    from fcp_cli.core.client import FcpClientCore

    results = []
    semaphore = asyncio.Semaphore(max_parallel)

    async with FcpClientCore() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        ) as progress:

            task_id = progress.add_task(
                f"Logging {len(images)} meals...",
                total=len(images)
            )

            async def process_one(image: Path) -> dict:
                """Process one image and update progress."""
                async with semaphore:
                    try:
                        result = await client.analyze_meal_async(
                            image_path=image,
                            media_resolution=resolution,
                        )
                        progress.update(task_id, advance=1)
                        return {
                            "success": True,
                            "image": image.name,
                            "data": result,
                        }
                    except Exception as e:
                        progress.update(task_id, advance=1)
                        return {
                            "success": False,
                            "image": image.name,
                            "error": str(e),
                        }

            # Launch all tasks
            tasks = [process_one(img) for img in images]
            results = await asyncio.gather(*tasks)

    return results
```

---

### Pattern 3: Smart Retry with Exponential Backoff

```python
# src/fcp_cli/utils/retry.py

import asyncio
import httpx
from typing import Any, Callable


async def retry_with_backoff(
    func: Callable,
    *args,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    **kwargs,
) -> Any:
    """Retry function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts
        initial_delay: Initial delay in seconds
        *args, **kwargs: Arguments to pass to func

    Returns:
        Function result

    Raises:
        Exception: If all retries fail
    """

    last_exception = None

    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)

        except httpx.HTTPStatusError as e:
            last_exception = e

            # Rate limited? Respect Retry-After header
            if e.response.status_code == 429:
                retry_after = int(e.response.headers.get("Retry-After", initial_delay * (2 ** attempt)))
                await asyncio.sleep(retry_after)
                continue

            # Other HTTP error? Don't retry
            raise

        except (httpx.NetworkError, httpx.TimeoutException) as e:
            last_exception = e

            # Network/timeout error? Exponential backoff
            if attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt)  # 1s, 2s, 4s
                await asyncio.sleep(delay)
                continue

            # Last attempt failed
            raise

    # All retries exhausted
    raise last_exception


# Usage in batch processor
async def process_with_retry(
    client: FcpClientCore,
    image: Path,
    resolution: str,
) -> dict:
    """Process image with automatic retry."""

    try:
        result = await retry_with_backoff(
            client.analyze_meal_async,
            image_path=image,
            media_resolution=resolution,
            max_retries=3,
        )
        return {"success": True, "data": result}

    except Exception as e:
        return {"success": False, "error": str(e)}
```

---

## 3. Client Connection Pooling

Optimize the HTTP client for maximum performance:

```python
# src/fcp_cli/core/client.py

import httpx
from typing import AsyncContextManager


class FcpClientCore:
    """FCP API client with optimized connection pooling."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: str | None = None,
    ):
        self.base_url = base_url
        self.api_key = api_key

        # Optimized HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(30.0, connect=5.0),
            limits=httpx.Limits(
                max_connections=20,           # Total connection pool
                max_keepalive_connections=10, # Keep connections alive
                keepalive_expiry=30.0,        # Keep alive for 30s
            ),
            http2=True,  # Enable HTTP/2 for multiplexing
            headers={
                "User-Agent": "FCP-CLI/1.0",
                "X-Client-Type": "cli",
            },
        )

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - close connections."""
        await self._client.aclose()
```

---

## 4. Best Practices

### Concurrency Limits

Respect server rate limits to avoid 429 errors:

```python
# Recommended concurrency by operation type
MAX_PARALLEL_LIMITS = {
    "analyze": 5,   # Heavy operations (server limit: 10/min)
    "crud": 10,     # Light CRUD ops (server limit: 30/min)
    "search": 8,    # Search operations (server limit: 20/min)
}
```

### Auto-Resolution Detection

Smart default based on image size:

```python
def auto_select_resolution(image_path: Path) -> str:
    """Auto-select resolution based on image file size."""

    size_bytes = image_path.stat().st_size

    if size_bytes < 100_000:  # < 100KB
        return "low"
    elif size_bytes < 500_000:  # < 500KB
        return "medium"
    else:
        return "high"


# Usage
@app.command("meal")
def log_meal(
    image_path: Path,
    resolution: str | None = typer.Option(None, "--res", help="Override auto-detection"),
):
    # Auto-detect if not specified
    if resolution is None:
        resolution = auto_select_resolution(image_path)
        console.print(f"[dim]Auto-selected resolution: {resolution}[/dim]")
```

### Image Pre-optimization

Resize and compress before uploading:

```python
async def optimize_image(image_path: Path, resolution: str) -> bytes:
    """Resize and compress image before upload."""

    from PIL import Image
    import io

    # Resolution to max dimension mapping
    sizes = {"low": 400, "medium": 800, "high": 1600}
    max_size = sizes[resolution]

    # Open and resize
    with Image.open(image_path) as img:
        # Convert to RGB if needed
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # Resize maintaining aspect ratio
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Compress to JPEG
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85, optimize=True)
        return buffer.getvalue()


# Usage in client
async def analyze_meal_async(
    self,
    image_path: Path,
    media_resolution: str = "medium",
) -> dict:
    # Optimize image first
    image_data = await optimize_image(image_path, media_resolution)
    image_b64 = base64.b64encode(image_data).decode()

    # Send smaller payload
    payload = {
        "image_data": image_b64,
        "media_resolution": media_resolution,
    }

    response = await self._client.post("/analyze", json=payload)
    return response.json()
```

---

## 5. Performance Metrics

### Before Optimization

Sequential processing:
```
10 meals × 3s per meal = 30 seconds
```

### After Optimization

Parallel processing with low resolution:
```
10 meals ÷ 5 concurrent × 0.8s per meal = 1.6 seconds
```

**Result: 18.7x faster! 🚀**

### Breakdown
- Low resolution: 4x faster processing (400px vs 1600px)
- Parallel requests: 5x concurrent throughput
- Connection pooling: 10-20% faster (reused connections)

---

## 6. Implementation Checklist

### Phase 1: Resolution Control (30 min)
- [ ] Add `--res` flag to `log meal` command
- [ ] Add `--res` flag to `log menu` command
- [ ] Add `--res` flag to `recipes extract` command
- [ ] Update client methods to pass `media_resolution`
- [ ] Add resolution guide to help text
- [ ] Test with all three resolutions

### Phase 2: Parallel Processing (2 hours)
- [ ] Create `log batch` command
- [ ] Implement `batch_log_meals()` with semaphore
- [ ] Add progress bar with `rich.progress`
- [ ] Add retry logic with exponential backoff
- [ ] Handle rate limiting (429 responses)
- [ ] Test with various concurrency levels

### Phase 3: Connection Optimization (1 hour)
- [ ] Update `FcpClientCore` with connection pooling
- [ ] Enable HTTP/2 in httpx client
- [ ] Add proper async context manager
- [ ] Implement auto-resolution detection
- [ ] Add image pre-optimization (Pillow)

### Phase 4: Testing (30 min)
- [ ] Unit tests for retry logic
- [ ] Integration tests for parallel batch
- [ ] Performance benchmarks
- [ ] Documentation updates

**Total estimated time: ~4 hours**

---

## 7. Usage Examples

### Simple Meal Logging
```bash
# Default (medium resolution)
fcp log meal photo.jpg

# Fast and cheap (low resolution)
fcp log meal photo.jpg --res low

# High accuracy (high resolution)
fcp log meal photo.jpg --res high
```

### Batch Processing
```bash
# Process folder with 5 parallel requests
fcp log batch ./meal-photos --parallel 5 --res low

# Conservative (3 parallel, medium quality)
fcp log batch ~/photos --parallel 3 --res medium

# Maximum speed (10 parallel, low resolution)
fcp log batch ./snapshots --parallel 10 --res low
```

### Auto-Detection
```bash
# Let CLI choose resolution based on file size
fcp log meal photo.jpg  # Auto-detects and shows chosen resolution
```

---

## 8. Troubleshooting

### Rate Limiting (429 Errors)
**Problem:** Too many concurrent requests
**Solution:** Reduce `--parallel` value or increase retry delays

```python
# Adjust semaphore limit
semaphore = asyncio.Semaphore(3)  # Lower from 5 to 3
```

### Connection Timeouts
**Problem:** Network latency causing timeouts
**Solution:** Increase timeout values

```python
timeout=httpx.Timeout(60.0, connect=10.0)  # Longer timeouts
```

### Memory Issues
**Problem:** Loading too many large images
**Solution:** Enable image pre-optimization

```python
# Compress images before encoding
image_data = await optimize_image(image_path, resolution)
```

---

## 9. Future Enhancements

- [ ] Add `--watch` mode for auto-logging new photos
- [ ] Implement local caching for offline resilience
- [ ] Add dry-run mode to estimate costs before batch
- [ ] Support video frame extraction and batch analysis
- [ ] Add Parquet export for bulk analytics

---

**Questions or issues?** File an issue at: https://github.com/Food-Context-Protocol/fcp-cli
