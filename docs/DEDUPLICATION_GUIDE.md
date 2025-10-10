# Case Deduplication Guide

## 🎯 The Problem You Identified

When searching for similar cases, **each case can have multiple chunks** in the vector store. For example:
- Case A might have 25 chunks (one per section/page)
- Case B might have 13 chunks
- Case C might have 24 chunks

If you ask for k=10 similar results, you might get:
- 3 chunks from Case A (pages 5, 8, 12)
- 3 chunks from Case A again!
- 2 chunks from Case B
- 2 chunks from Case C

**Result: Only 3 unique cases instead of 10!**

## ✅ The Solution

I've implemented **three modes** for handling this:

### 1. Deduplicated Search (Default) ✨

Returns **k unique cases**, showing the best match from each case.

```python
cases = analyzer.find_similar_cases_only(
    case_text="Your search...",
    k=10,
    deduplicate=True  # Default
)
# Returns 10 UNIQUE cases
```

**How it works:**
1. Retrieves k×3 chunks (30 chunks for k=10)
2. Groups chunks by case
3. Keeps only the best chunk per case
4. Returns k unique cases

**Best for:**
- Quick overview of relevant cases
- Diverse case coverage
- When you need a list of unique precedents

### 2. Non-Deduplicated Search

Returns **k chunks**, which may include multiple chunks from the same case.

```python
chunks = analyzer.find_similar_cases_only(
    case_text="Your search...",
    k=10,
    deduplicate=False
)
# Returns 10 chunks (may be from 3-4 unique cases)
```

**Best for:**
- When you want to see all relevant excerpts
- Finding specific passages
- Deep dive into specific sections

### 3. Grouped by Case (New!) 📚

Returns **k unique cases**, each with up to n relevant chunks.

```python
cases = analyzer.find_similar_cases_with_chunks(
    case_text="Your search...",
    k_cases=5,              # 5 unique cases
    max_chunks_per_case=3   # Up to 3 chunks per case
)
# Returns 5 cases with 3 chunks each = 15 total excerpts
```

**Best for:**
- Seeing multiple relevant sections per case
- Comprehensive case understanding
- Building legal arguments with multiple quotes

## 📊 Real Example from Your Data

From the demo run:

### Request: k=10 results

**Mode 1: Deduplicated (default)**
```
✓ Found 4 unique cases

1. Railway Protection Force v. Prem Chand Kumar (Page 1)
2. Union of India v. Sajib Roy (Page 1)
3. Akhtar Ali v. State of Uttarakhand (Page 3)
4. Malleeswari v. K. Suguna (Page 1)
```

**Mode 2: Non-Deduplicated**
```
✓ Found 10 chunks from 4 unique cases

1. Railway Protection Force v. Prem Chand Kumar (Page 1)
2. Railway Protection Force v. Prem Chand Kumar (Page 2) ← Same case!
3. Union of India v. Sajib Roy (Page 1)
4. Railway Protection Force v. Prem Chand Kumar (Page 3) ← Same case!
5. Akhtar Ali v. State of Uttarakhand (Page 3)
... (10 total)
```

**Mode 3: Grouped**
```
✓ Found 4 cases with 12 total chunks

1. Railway Protection Force v. Prem Chand Kumar
   - Page 1: Issue for Consideration (Score: 1.6192)
   - Page 2: Held section (Score: 1.6346)
   - Page 3: Keywords (Score: 1.6590)

2. Union of India v. Sajib Roy
   - Page 1: Issue for Consideration (Score: 1.6506)
   - Page 16: Facts section (Score: 1.7182)
   - Page 1: Held section (Score: 1.7270)
... (4 cases total)
```

## 💻 Usage

### Python API

```python
from utils.case_similarity import CaseSimilarityAnalyzer

analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Method 1: Deduplicated (default)
unique_cases = analyzer.find_similar_cases_only(
    "freedom of speech",
    k=10,
    deduplicate=True
)
print(f"Found {len(unique_cases)} unique cases")

# Method 2: Non-deduplicated
all_chunks = analyzer.find_similar_cases_only(
    "freedom of speech",
    k=10,
    deduplicate=False
)
print(f"Found {len(all_chunks)} chunks")

# Method 3: Grouped
grouped_cases = analyzer.find_similar_cases_with_chunks(
    "freedom of speech",
    k_cases=5,
    max_chunks_per_case=3
)
for case in grouped_cases:
    print(f"{case['case_title']}: {len(case['chunks'])} chunks")
```

### REST API

```bash
# Method 1: Deduplicated
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k": 10,
    "deduplicate": true
  }'

# Method 2: Non-deduplicated
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k": 10,
    "deduplicate": false
  }'

# Method 3: Grouped
curl -X POST http://localhost:5001/api/find-similar-cases-with-chunks \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech",
    "k_cases": 5,
    "max_chunks_per_case": 3
  }'
```

## 🎯 When to Use Each Mode

### Use **Deduplicated** (Mode 1) when:
- ✅ Lawyer needs a list of relevant precedents
- ✅ Building a case citation list
- ✅ Getting overview of legal landscape
- ✅ Need diverse case coverage

### Use **Non-Deduplicated** (Mode 2) when:
- ✅ Looking for specific passages
- ✅ Need all relevant excerpts
- ✅ Deep research into particular issues
- ✅ Don't mind seeing same case multiple times

### Use **Grouped** (Mode 3) when:
- ✅ Need comprehensive view per case
- ✅ Building legal arguments with multiple quotes
- ✅ Want to see different sections of same case
- ✅ Preparing detailed case analysis

## 📈 Performance Considerations

### Deduplicated Mode
- **Speed:** Slightly slower (retrieves 3x chunks)
- **Accuracy:** High (ensures k unique cases)
- **Best for:** Production use

### Non-Deduplicated Mode
- **Speed:** Fastest (direct retrieval)
- **Accuracy:** May have duplicates
- **Best for:** Quick searches, deep dives

### Grouped Mode
- **Speed:** Slowest (retrieves many chunks)
- **Accuracy:** Very comprehensive
- **Best for:** Detailed analysis

## 🔧 Technical Details

### How Deduplication Works

```python
# Internal algorithm:
1. Request k*3 chunks (e.g., 30 for k=10)
2. Iterate through chunks:
   - Use case_number as unique identifier
   - If case not seen before → Add it
   - If case seen but this chunk has better score → Replace it
   - Stop when we have k unique cases
3. Return k unique cases with their best chunks
```

### Scoring

- Lower scores = Better similarity (FAISS distance)
- Best chunk = Chunk with lowest score for that case
- Cases are ranked by their best chunk's score

## 📝 Response Format

### Deduplicated
```json
{
  "case_title": "Case Name",
  "citation": "AIR 2025 SC 123",
  "case_number": "Civil Appeal No. 123",
  "page_number": 15,
  "section": "Held",
  "s3_url": "https://...",
  "similarity_score": 1.6192,
  "content_preview": "..."
}
```

### Grouped
```json
{
  "case_title": "Case Name",
  "citation": "AIR 2025 SC 123",
  "case_number": "Civil Appeal No. 123",
  "s3_url": "https://...",
  "best_score": 1.6192,
  "chunks": [
    {
      "page_number": 15,
      "section": "Held",
      "chunk_id": 5,
      "similarity_score": 1.6192,
      "content_preview": "..."
    },
    {
      "page_number": 20,
      "section": "Analysis",
      "chunk_id": 8,
      "similarity_score": 1.6534,
      "content_preview": "..."
    }
  ]
}
```

## 🎓 Examples

### Example 1: Lawyer Needs Case List

```python
# Lawyer: "Find me 10 cases on Article 14"
cases = analyzer.find_similar_cases_only(
    "Article 14 equality arbitrary state action",
    k=10,
    deduplicate=True  # Get 10 unique cases
)

for case in cases:
    print(f"- {case['case_title']} ({case['citation']})")
```

### Example 2: Finding Specific Quote

```python
# Lawyer: "Find all mentions of 'basic structure'"
chunks = analyzer.find_similar_cases_only(
    "basic structure doctrine",
    k=20,
    deduplicate=False  # Get all relevant excerpts
)

for chunk in chunks:
    print(f"{chunk['case_title']} - Page {chunk['page_number']}")
    print(chunk['content_preview'])
```

### Example 3: Building Argument

```python
# Lawyer: "Need comprehensive analysis of top 5 cases"
cases = analyzer.find_similar_cases_with_chunks(
    "freedom of speech reasonable restrictions",
    k_cases=5,
    max_chunks_per_case=4
)

for case in cases:
    print(f"\n{case['case_title']}")
    print(f"Relevant sections:")
    for chunk in case['chunks']:
        print(f"  - Page {chunk['page_number']}: {chunk['section']}")
```

## 🚀 Try It Now

```bash
# Run the demo
python demo_deduplication.py

# Test in your code
from utils.case_similarity import CaseSimilarityAnalyzer

analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Compare all three modes
result1 = analyzer.find_similar_cases_only("your query", k=10, deduplicate=True)
result2 = analyzer.find_similar_cases_only("your query", k=10, deduplicate=False)
result3 = analyzer.find_similar_cases_with_chunks("your query", k_cases=5, max_chunks_per_case=3)

print(f"Deduplicated: {len(result1)} unique cases")
print(f"Non-deduplicated: {len(result2)} chunks")
print(f"Grouped: {len(result3)} cases with {sum(len(c['chunks']) for c in result3)} chunks")
```

---

**Summary:** Deduplication ensures you get k unique cases instead of k chunks that might be from the same few cases. Use `deduplicate=True` (default) for most use cases! 🎯

