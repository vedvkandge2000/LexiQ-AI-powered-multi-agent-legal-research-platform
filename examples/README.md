# LexiQ Examples

Demo scripts and examples for LexiQ.

## 📂 Demo Scripts

### 1. demo_deduplication.py

**Purpose:** Demonstrates the three search modes and how deduplication works.

**Run:**
```bash
python examples/demo_deduplication.py
```

**Shows:**
- Mode 1: Deduplicated search (unique cases)
- Mode 2: Non-deduplicated search (all chunks)
- Mode 3: Grouped search (multiple chunks per case)
- Real comparison with your data

**Duration:** ~30 seconds

---

### 2. demo_retrieval.py

**Purpose:** Demonstrates the complete retrieval and query system.

**Run:**
```bash
python examples/demo_retrieval.py
```

**Shows:**
- Basic queries
- Retrieval with metadata
- Search-only mode
- Batch queries
- Query customization

**Duration:** Interactive (user-paced)

---

## 🚀 Quick Examples

### Example 1: Simple Search

```python
from utils.case_similarity import CaseSimilarityAnalyzer

analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Get 10 unique cases
cases = analyzer.find_similar_cases_only(
    "freedom of speech Article 19",
    k=10,
    deduplicate=True
)

for case in cases:
    print(f"{case['case_title']} - Page {case['page_number']}")
```

### Example 2: Case Analysis

```python
from utils.case_similarity import CaseSimilarityAnalyzer

analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Analyze a case
result = analyzer.analyze_case_from_text(
    case_description="""
    Case: Client challenges state law requiring pre-approval
    of online content. Issue: Does this violate Article 19(1)(a)?
    """,
    k=5
)

print(result['analysis'])
```

### Example 3: Grouped Search

```python
# Get 5 cases with 3 relevant chunks each
grouped_cases = analyzer.find_similar_cases_with_chunks(
    "Article 14 equality",
    k_cases=5,
    max_chunks_per_case=3
)

for case in grouped_cases:
    print(f"\n{case['case_title']}")
    for chunk in case['chunks']:
        print(f"  Page {chunk['page_number']}: {chunk['section'][:50]}...")
```

### Example 4: REST API

```bash
# Start the API
python case_api.py

# In another terminal:
curl -X POST http://localhost:5001/api/analyze-case-text \
  -H "Content-Type: application/json" \
  -d '{
    "case_description": "Your case details...",
    "k": 5
  }'
```

---

## 📚 More Examples

See [../docs/USAGE_GUIDE.md](../docs/USAGE_GUIDE.md) for more examples.

See [../docs/EXAMPLE_SESSION.md](../docs/EXAMPLE_SESSION.md) for interactive examples.

---

## 🧪 Testing

For test scripts, see [../tests/](../tests/)

