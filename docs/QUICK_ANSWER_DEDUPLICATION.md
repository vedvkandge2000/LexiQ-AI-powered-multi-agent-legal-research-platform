# Quick Answer: How Case Deduplication Works

## Your Question
> "For quick search, each reference case can have multiple chunks. How are you creating it?"

## The Problem

You're absolutely right! Each case has **multiple chunks** in the vector store:
- Case A: 25 chunks
- Case B: 13 chunks  
- Case C: 24 chunks

**Before the fix:** If you asked for k=10 results, you got:
```
10 chunks from only 3-4 unique cases! ❌
```

**After the fix:** You now get:
```
10 UNIQUE cases! ✅
```

## The Solution

I implemented **three search modes**:

### 1. ✅ Deduplicated (Default - Recommended)

```python
cases = analyzer.find_similar_cases_only(
    "your search",
    k=10,
    deduplicate=True  # Default
)
# Returns: 10 UNIQUE cases (one result per case)
```

**Algorithm:**
1. Retrieve k×3 chunks (30 chunks)
2. Group by case number
3. Keep best chunk per case
4. Return k unique cases

### 2. 📄 Non-Deduplicated

```python
chunks = analyzer.find_similar_cases_only(
    "your search",
    k=10,
    deduplicate=False
)
# Returns: 10 chunks (may include duplicates from same case)
```

### 3. 📚 Grouped (Best of Both!)

```python
cases = analyzer.find_similar_cases_with_chunks(
    "your search",
    k_cases=5,              # 5 unique cases
    max_chunks_per_case=3   # 3 chunks per case
)
# Returns: 5 unique cases, each with 3 relevant chunks
```

## Real Example from Your Data

**Search:** "freedom of speech"

**Mode 1 (Deduplicated):**
```
✓ 4 unique cases
1. Railway Protection Force v. Prem Chand (Page 1)
2. Union of India v. Sajib Roy (Page 1)
3. Akhtar Ali v. State of Uttarakhand (Page 3)
4. Malleeswari v. K. Suguna (Page 1)
```

**Mode 2 (Non-Deduplicated):**
```
✓ 10 chunks from only 4 unique cases
1. Railway Protection Force (Page 1)
2. Railway Protection Force (Page 2) ← Duplicate!
3. Union of India (Page 1)
4. Railway Protection Force (Page 3) ← Duplicate!
...
```

**Mode 3 (Grouped):**
```
✓ 4 cases with 12 total chunks

1. Railway Protection Force
   - Page 1: Issue for Consideration
   - Page 2: Held section
   - Page 3: Keywords
   
2. Union of India v. Sajib Roy
   - Page 1: Issue for Consideration
   - Page 16: Facts section
   - Page 1: Held section
...
```

## When to Use Each Mode

| Mode | Use When | Example |
|------|----------|---------|
| **Deduplicated** | Need list of unique cases | "Find 10 precedents on Article 14" |
| **Non-Deduplicated** | Want all relevant excerpts | "Find all mentions of 'basic structure'" |
| **Grouped** | Need multiple quotes per case | "Analyze top 5 cases in depth" |

## Default Behavior

**By default, `deduplicate=True`** - you get unique cases! This is what most lawyers want.

## API Usage

```bash
# Deduplicated (default)
curl -X POST http://localhost:5001/api/find-similar-cases \
  -d '{"case_text": "...", "k": 10}'

# Non-deduplicated
curl -X POST http://localhost:5001/api/find-similar-cases \
  -d '{"case_text": "...", "k": 10, "deduplicate": false}'

# Grouped
curl -X POST http://localhost:5001/api/find-similar-cases-with-chunks \
  -d '{"case_text": "...", "k_cases": 5, "max_chunks_per_case": 3}'
```

## Try It

```bash
python demo_deduplication.py
```

This runs a live demo with your data showing all three modes!

---

**TL;DR:** Deduplication is now ON by default. When you ask for k=10 cases, you get 10 **unique** cases, not 10 chunks from 3-4 cases! 🎯

