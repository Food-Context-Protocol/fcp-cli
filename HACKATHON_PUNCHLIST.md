# FCP CLI - Hackathon Punchlist

**Hackathon Launch:** Tomorrow (February 9, 2026)
**Focus:** Essential demo-ready features only

---

## ⚡ CRITICAL FOR DEMO (Must Ship)

### 1. Demo-Ready Error Messages
**Why:** Can't have ugly stack traces during demo
**Effort:** 20 minutes
**Status:** ❌ Not started

**Quick Fix:**
```python
# Add to utils.py
def safe_execute(func):
    """Catch all errors and show friendly messages."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            console.print(f"[red]Error:[/red] {str(e)}")
            console.print("[dim]Tip: Check 'fcp --help' for usage[/dim]")
            raise typer.Exit(1)
    return wrapper
```

**Apply to all commands**

---

### 2. README Demo Script
**Why:** Judges need to quickly understand what it does
**Effort:** 15 minutes
**Status:** ❌ Not started

**Add to README.md:**
```markdown
## 🎥 Quick Demo

```bash
# 1. Log a meal
fcp log meal "Spicy Ramen" --venue "Ippudo"

# 2. Analyze nutrition
fcp profile show

# 3. Get meal suggestions
fcp suggest meal

# 4. Search your history
fcp search query "ramen"

# 5. Check food safety
fcp safety recalls --query "romaine lettuce"
```

**Demo time: < 2 minutes**
```

---

## 🎯 NICE TO HAVE (If Time Permits)

### 3. Async Batch Demo
**Why:** Show off performance
**Effort:** 1 hour
**Status:** ❌ Not started

**Implementation:** Only for `pantry sync` command (most impressive)

**Demo Script:**
```bash
# Create test file with 100 items
fcp pantry sync pantry.json

# Show progress bar syncing 100 items in ~5 seconds
```

**Skip if no time** - not critical for judges

---

### 4. --help Text Polish
**Why:** Judges will run `--help` first
**Effort:** 30 minutes
**Status:** ❌ Not started

**Quick Polish:**
```python
# Make sure every command has:
@app.command(help="Clear, one-line description of what this does")
def command(
    arg: str = typer.Argument(..., help="What this argument is for"),
):
    """
    Longer description with example:

    Example:
        fcp log meal "Pizza" --venue "Papa Johns"
    """
```

**Priority Commands:**
- `fcp log` - Most used
- `fcp search` - Demo worthy
- `fcp suggest` - AI feature

---

## ❌ SKIP FOR HACKATHON

These are great but NOT needed for demo:

- ❌ Configuration file support (use env vars)
- ❌ Offline caching (demo with internet)
- ❌ 100% test coverage (functional is enough)
- ❌ Mutation testing (overkill for hackathon)
- ❌ CI/CD pipeline (manual testing OK)
- ❌ Architecture docs (code works, that's enough)
- ❌ Pre-commit hooks (format manually)

---

## 📋 Pre-Demo Checklist

### Day Before (Tonight)

- [ ] **1. Error handling** (20 min)
  - Add safe_execute decorator
  - Apply to top 5 commands
  - Test error messages look good

- [ ] **2. Polish README** (15 min)
  - Add demo script section
  - Add clear quick start
  - Add example output screenshots

- [ ] **3. Test demo flow** (15 min)
  - Run through entire demo
  - Make sure no crashes
  - Time the demo (< 2 min)

**Total Time:** 50 minutes

### Day Of (Morning)

- [ ] **4. Help text** (30 min)
  - Polish --help for main commands
  - Add examples to docstrings

- [ ] **5. Final test** (10 min)
  - Fresh terminal
  - Run demo script
  - Time it again

**Total Time:** 40 minutes

---

## 🎤 Demo Script (2 Minutes)

```bash
# Terminal 1: Start server
cd fcp-gemini-server
make run

# Terminal 2: Demo CLI (2 min)
clear

# 1. Show help (5 sec)
fcp --help

# 2. Log meals (15 sec)
fcp log meal "Tonkotsu Ramen" --venue "Ippudo NYC"
fcp log meal "Margherita Pizza"

# 3. View history (10 sec)
fcp log list --limit 5

# 4. Get AI suggestions (30 sec)
fcp suggest meal --style "japanese"

# 5. Search (10 sec)
fcp search query "ramen"

# 6. Safety check (20 sec)
fcp safety recalls --query "lettuce"

# 7. Show taste profile (15 sec)
fcp profile show

# 8. Research agent (35 sec)
fcp research ask "What are the health benefits of fermented foods?"
```

**Total:** ~2 minutes

---

## 🚨 Things That MUST Work

1. ✅ `fcp log` commands (add, list, search)
2. ✅ `fcp suggest meal`
3. ✅ `fcp search query`
4. ✅ `fcp safety` commands
5. ✅ `fcp research ask`
6. ✅ Error handling (no ugly crashes)
7. ✅ Help text is clear

## 🤷 Things That Can Be Broken

- Pantry batch operations
- Recipe extraction
- Profile taste analysis
- Nearby food search
- Label generation
- Publishing features

**Judges won't test everything - focus on the hero features**

---

## 📊 Success Metrics

### What Judges Care About

1. **Does it work?** (demo doesn't crash)
2. **Is it useful?** (solves real problem)
3. **Is it impressive?** (AI/Gemini features)
4. **Is it polished?** (nice output, good errors)

### What Judges Don't Care About

- Test coverage numbers
- CI/CD setup
- Architecture docs
- Code comments
- Repository pattern
- Pre-commit hooks

---

## ⏱️ Time Budget

| Task | Time | Priority |
|------|------|----------|
| Error handling | 20 min | 🔴 MUST |
| README demo | 15 min | 🔴 MUST |
| Demo testing | 15 min | 🔴 MUST |
| Help text polish | 30 min | 🟡 SHOULD |
| Async batch demo | 1 hour | 🟢 NICE |
| **TOTAL MUST** | **50 min** | |
| **TOTAL SHOULD** | **1h 20m** | |
| **TOTAL NICE** | **2h 20m** | |

**Recommendation:** Do MUST items tonight (50 min), SHOULD items tomorrow morning (30m)

---

## ✅ Done When

- [ ] Demo script runs without crashing
- [ ] README has clear quick start
- [ ] Error messages are friendly
- [ ] Help text is clear
- [ ] Demo takes < 2 minutes
- [ ] You've practiced the demo 3x

---

## 🎯 The Goal

**NOT:** Perfect, production-ready CLI
**YES:** Demo-ready CLI that impresses judges

**Ship it, win it, polish later!** 🚀

---

**Last Updated:** February 8, 2026
**Demo:** Tomorrow morning
**Time Remaining:** ~12 hours
