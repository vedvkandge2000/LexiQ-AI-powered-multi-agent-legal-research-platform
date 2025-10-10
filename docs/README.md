# LexiQ Documentation

Complete documentation for the LexiQ legal research platform.

## 📚 Documentation Index

### Getting Started

1. **[QUICKSTART.md](QUICKSTART.md)** - Get started in 3 steps
   - Installation
   - Basic usage
   - First query

2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete system overview
   - Architecture
   - All features
   - File structure

### User Guides

3. **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - Complete usage guide
   - All features explained
   - Code examples
   - Integration patterns

4. **[USER_OPTIONS_GUIDE.md](USER_OPTIONS_GUIDE.md)** - Control parameters
   - Search modes
   - Number of cases
   - API parameters

5. **[EXAMPLE_SESSION.md](EXAMPLE_SESSION.md)** - Real usage examples
   - Interactive sessions
   - API examples
   - Output samples

### Feature Documentation

6. **[CASE_SIMILARITY_README.md](CASE_SIMILARITY_README.md)** - Case similarity feature
   - How it works
   - API reference
   - Use cases

7. **[DEDUPLICATION_GUIDE.md](DEDUPLICATION_GUIDE.md)** - Search modes explained
   - Deduplicated vs non-deduplicated
   - Grouped search
   - When to use each

8. **[QUICK_ANSWER_DEDUPLICATION.md](QUICK_ANSWER_DEDUPLICATION.md)** - Quick deduplication reference
   - TL;DR version
   - Simple examples

9. **[RETRIEVAL_README.md](RETRIEVAL_README.md)** - Retrieval system
   - How search works
   - Vector store
   - Performance

10. **[PAGE_NUMBER_UPDATE.md](PAGE_NUMBER_UPDATE.md)** - Page number feature
    - How page tracking works
    - Re-processing guide

### Implementation Details

11. **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - What was built
    - All components
    - Features delivered
    - Technical details

12. **[FINAL_SUMMARY.md](FINAL_SUMMARY.md)** - Final summary
    - Complete feature list
    - Ready-to-use checklist

13. **[RETRIEVAL_SUMMARY.md](RETRIEVAL_SUMMARY.md)** - Retrieval system summary
    - Quick reference
    - Key features

14. **[USER_CONTROL_SUMMARY.md](USER_CONTROL_SUMMARY.md)** - User controls
    - What users can control
    - How to change settings

## 🎯 Quick Navigation

### I want to...

**Get started quickly**
→ [QUICKSTART.md](QUICKSTART.md)

**Understand the system**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**Learn how to use it**
→ [USAGE_GUIDE.md](USAGE_GUIDE.md)

**Control search parameters**
→ [USER_OPTIONS_GUIDE.md](USER_OPTIONS_GUIDE.md)

**Understand search modes**
→ [DEDUPLICATION_GUIDE.md](DEDUPLICATION_GUIDE.md)

**See examples**
→ [EXAMPLE_SESSION.md](EXAMPLE_SESSION.md)

**Build an integration**
→ [CASE_SIMILARITY_README.md](CASE_SIMILARITY_README.md)

## 📖 Reading Order

### For New Users:
1. QUICKSTART.md
2. USAGE_GUIDE.md
3. USER_OPTIONS_GUIDE.md
4. EXAMPLE_SESSION.md

### For Developers:
1. PROJECT_SUMMARY.md
2. CASE_SIMILARITY_README.md
3. RETRIEVAL_README.md
4. IMPLEMENTATION_COMPLETE.md

### For Integrators:
1. CASE_SIMILARITY_README.md
2. USER_OPTIONS_GUIDE.md
3. DEDUPLICATION_GUIDE.md

## 🔍 By Topic

### Search & Retrieval
- RETRIEVAL_README.md
- RETRIEVAL_SUMMARY.md
- DEDUPLICATION_GUIDE.md
- QUICK_ANSWER_DEDUPLICATION.md

### Case Analysis
- CASE_SIMILARITY_README.md
- USAGE_GUIDE.md
- EXAMPLE_SESSION.md

### User Interface
- USER_OPTIONS_GUIDE.md
- USER_CONTROL_SUMMARY.md
- EXAMPLE_SESSION.md

### Technical Details
- PROJECT_SUMMARY.md
- IMPLEMENTATION_COMPLETE.md
- PAGE_NUMBER_UPDATE.md
- FINAL_SUMMARY.md

## 📁 Other Resources

- **[../examples/](../examples/)** - Demo scripts
- **[../tests/](../tests/)** - Test scripts
- **[../README.md](../README.md)** - Project overview

---

**Need help?** Start with [QUICKSTART.md](QUICKSTART.md) or [USAGE_GUIDE.md](USAGE_GUIDE.md)

# .gitignore Instructions

## Ignored Files and Directories

1. **Virtual Environment**
   - `venv/` is excluded to keep dependencies isolated. Activate using `source venv/bin/activate`.

2. **Environment Variables**
   - `.env` and `.env.d/` store sensitive info like API keys. NEVER commit these.

3. **Compiled Python Files**
   - Patterns like `*.pyc` and `__pycache__/` ignore Python bytecode files.

4. **IDE Specific Settings**
   - `.cursor/` for IDE settings; these are machine-specific.

5. **Log Files**
   - Patterns `**/*.log` for ignoring runtime logs.

6. **System Files**
   - `.DS_Store` (macOS) as it holds no code-related information.

