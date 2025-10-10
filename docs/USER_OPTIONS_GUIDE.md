# User Options Guide - How to Change Modes

## 🎯 Overview

You can now **choose the search mode and number of cases** in all interfaces!

## 🖥️ Interactive CLI (case_analyzer.py)

### Option 3: Quick Search - Choose Your Mode!

When you select "Quick search" from the main menu:

```bash
python case_analyzer.py

# Select option 3: Quick search for similar cases
```

You'll see:

```
🔍 Quick Search
----------------------------------------------------------------------

Search Mode:
1. Unique Cases (deduplicated) - One result per case
2. All Chunks - May include multiple chunks from same case
3. Grouped by Case - Multiple relevant chunks per case

Select mode (1-3, default 1): 
```

### Mode 1: Unique Cases (Deduplicated) ✅

```
Select mode (1-3, default 1): 1
Enter search text: freedom of speech Article 19
How many results? (default 10): 15

✓ Found 15 unique cases
1. Case A (Page 5)
2. Case B (Page 12)
3. Case C (Page 3)
...
```

**Gets:** 15 **unique cases** (one per case)

### Mode 2: All Chunks

```
Select mode (1-3, default 1): 2
Enter search text: freedom of speech Article 19
How many results? (default 10): 15

✓ Found 15 chunks
1. Case A (Page 5)
2. Case A (Page 8)   ← Same case, different page
3. Case B (Page 12)
4. Case A (Page 15)  ← Same case again
...
```

**Gets:** 15 **chunks** (may include multiple chunks from same case)

### Mode 3: Grouped by Case 📚

```
Select mode (1-3, default 1): 3
Enter search text: freedom of speech Article 19
How many unique cases? (default 5): 10
Max chunks per case? (default 3): 5

✓ Found 10 cases with 47 total chunks

1. Case A
   Relevant Chunks (5):
   1. Page 5, Section: Introduction
      Similarity: 1.6234
   2. Page 8, Section: Analysis
      Similarity: 1.6457
   ...

2. Case B
   Relevant Chunks (5):
   ...
```

**Gets:** 10 unique cases, each with up to 5 relevant chunks

### Options for Case Analysis (Options 1 & 2)

When analyzing a case with Claude:

```
How many similar cases to retrieve? (default 5, max 20): 10

Response Detail Level:
1. Concise (max_tokens=1000)
2. Balanced (max_tokens=2000)
3. Comprehensive (max_tokens=3000)
Select level (1-3, default 2): 3
```

**Controls:**
- Number of cases: 1-20 (capped for performance)
- Response detail: Short, Medium, or Long

## 🔌 REST API

### Endpoint 1: `/api/find-similar-cases`

```bash
# Deduplicated (unique cases)
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k": 15,
    "deduplicate": true
  }'

# Non-deduplicated (all chunks)
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k": 15,
    "deduplicate": false
  }'
```

### Endpoint 2: `/api/find-similar-cases-with-chunks`

```bash
# Grouped by case
curl -X POST http://localhost:5001/api/find-similar-cases-with-chunks \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k_cases": 10,
    "max_chunks_per_case": 5
  }'
```

### Endpoint 3: `/api/analyze-case-text`

```bash
# Control number of cases and detail level
curl -X POST http://localhost:5001/api/analyze-case-text \
  -H "Content-Type: application/json" \
  -d '{
    "case_description": "My case details...",
    "k": 10
  }'

# Note: max_tokens is set in the analyzer initialization
# You can modify it by passing it to analyze_case_from_text()
```

## 🐍 Python API

### Quick Search with Mode Selection

```python
from utils.case_similarity import CaseSimilarityAnalyzer

analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

search_text = "freedom of speech Article 19"

# Mode 1: Deduplicated (unique cases)
unique_cases = analyzer.find_similar_cases_only(
    search_text,
    k=15,
    deduplicate=True  # ← Control deduplication
)
print(f"Found {len(unique_cases)} unique cases")

# Mode 2: Non-deduplicated (all chunks)
all_chunks = analyzer.find_similar_cases_only(
    search_text,
    k=15,
    deduplicate=False  # ← Get all chunks
)
print(f"Found {len(all_chunks)} chunks")

# Mode 3: Grouped by case
grouped = analyzer.find_similar_cases_with_chunks(
    search_text,
    k_cases=10,              # ← Number of unique cases
    max_chunks_per_case=5    # ← Chunks per case
)
print(f"Found {len(grouped)} cases with multiple chunks")
```

### Case Analysis with Custom Parameters

```python
# Control number of cases and response length
result = analyzer.analyze_case_from_text(
    case_description="My case details...",
    k=10,              # ← Number of similar cases
    max_tokens=3000,   # ← Response length
    temperature=0.3    # ← Creativity level
)

print(result["analysis"])
```

## 🎨 Parameter Guide

### Number of Cases (k)

| Value | Use Case | Speed |
|-------|----------|-------|
| 3-5 | Quick overview | ⚡ Fast |
| 5-10 | Standard research | 🚀 Normal |
| 10-20 | Comprehensive | 🐢 Slower |

**Recommendation:** 5-10 for most use cases

### Response Detail (max_tokens)

| Level | Tokens | Use Case |
|-------|--------|----------|
| Concise | 1000 | Quick answers |
| Balanced | 2000 | Standard analysis |
| Comprehensive | 3000 | Detailed research |

**Recommendation:** Balanced (2000) for most cases

### Chunks Per Case (max_chunks_per_case)

| Value | Use Case |
|-------|----------|
| 1-2 | Overview of each case |
| 3-4 | Standard depth |
| 5+ | Comprehensive excerpts |

**Recommendation:** 3 for balanced view

## 💡 Usage Patterns

### Pattern 1: Quick Case List
```
Mode: Deduplicated
k: 10
Use: "Give me 10 similar cases"
```

### Pattern 2: Deep Dive
```
Mode: Non-deduplicated
k: 20
Use: "Find all relevant passages"
```

### Pattern 3: Comprehensive Analysis
```
Mode: Grouped
k_cases: 5
max_chunks: 5
Use: "Analyze top 5 cases in detail"
```

### Pattern 4: Case Analysis
```
k: 10
max_tokens: 2000
Use: "Analyze my case against 10 precedents"
```

## 🚀 Try It Now

```bash
# Start interactive mode
python case_analyzer.py

# Select option 3: Quick search
# Choose your mode when prompted!
```

## 📝 Examples

### Example 1: Lawyer Wants List of Cases

```
Select mode: 1 (Unique Cases)
How many results: 15
Result: 15 different cases
```

### Example 2: Research Assistant Needs Excerpts

```
Select mode: 2 (All Chunks)
How many results: 30
Result: 30 chunks (might be 8-10 unique cases with multiple excerpts)
```

### Example 3: Preparing Legal Brief

```
Select mode: 3 (Grouped)
How many cases: 5
Chunks per case: 4
Result: 5 cases, each with 4 relevant excerpts = 20 total quotes
```

## 🎯 Quick Reference

| What You Want | Mode | Parameters |
|---------------|------|------------|
| List of cases | 1 | k=10-15 |
| All excerpts | 2 | k=20-30 |
| Detailed per case | 3 | k_cases=5, max_chunks=3-5 |
| Case analysis | N/A | k=5-10, detail=Balanced |

## 🔧 Default Values

If you just press Enter without typing:

- **Mode:** 1 (Deduplicated)
- **k:** 5 or 10 (depending on context)
- **Detail level:** 2 (Balanced)
- **Chunks per case:** 3

These are sensible defaults for most use cases!

---

**Everything is now user-controlled!** Choose your mode and parameters for each search. 🎉

