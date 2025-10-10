# LexiQ Case Similarity Analyzer

## Overview

The **Case Similarity Analyzer** is the core feature of LexiQ that helps lawyers find relevant precedents for their current cases. Upload a case PDF or describe your case in text, and get AI-powered analysis with similar precedents, direct quotes, and strategic recommendations.

## 🎯 Key Features

### ✅ Fixed Issues
- **PDF Links in Responses**: Now properly includes S3 PDF links in all responses
- **Metadata Enrichment**: Added section names, chunk IDs, and case numbers
- **Chain-of-Thought**: Explains WHY each precedent is relevant
- **Direct Quotes**: Includes highlighted passages from cited cases

### ✨ Core Capabilities

1. **Accept Lawyer's Case**
   - Upload PDF of current case
   - Type case description (facts, legal issues, parties)

2. **Find Similar Precedents**
   - Semantic search across Supreme Court cases
   - Ranked by relevance/similarity

3. **AI-Powered Analysis**
   - Natural language summary
   - List of matching cases with citations
   - Direct quotes from relevant passages
   - Explanation of relevance (chain-of-thought)
   - Strategic recommendations

4. **Complete References**
   - Case titles and citations
   - PDF links to full cases
   - Section/page references
   - Case numbers

## 🚀 Quick Start

### Option 1: Interactive CLI

```bash
python case_analyzer.py
```

Then choose:
1. Analyze case from text description
2. Analyze case from PDF file
3. Quick search (no AI analysis)

### Option 2: Python Script

```python
from utils.case_similarity import CaseSimilarityAnalyzer

# Initialize
analyzer = CaseSimilarityAnalyzer(vector_store_dir="data/vector_store")
analyzer.initialize()

# Analyze from text
case_description = """
Case Title: ABC v. State
Facts: [Your case facts]
Legal Issues: [Issues to be decided]
"""

result = analyzer.analyze_case_from_text(case_description, k=5)
print(result["analysis"])  # Full markdown analysis

# Analyze from PDF
result = analyzer.analyze_case_from_pdf("path/to/case.pdf", k=5)
print(result["analysis"])
```

### Option 3: REST API

```bash
# Start API server
python case_api.py

# Analyze case from text
curl -X POST http://localhost:5001/api/analyze-case-text \
  -H "Content-Type: application/json" \
  -d '{
    "case_description": "Your case details...",
    "k": 5
  }'

# Analyze case from PDF
curl -X POST http://localhost:5001/api/analyze-case-pdf \
  -F "file=@current_case.pdf" \
  -F "k=5"

# Quick search for similar cases
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{
    "case_text": "freedom of speech and reasonable restrictions",
    "k": 10
  }'
```

## 📊 Response Format

### Full Analysis Response

```json
{
  "current_case": "Description of the case...",
  "analysis": "## Case Analysis\n\n### Current Case Summary\n...",
  "similar_cases": [
    {
      "case_title": "Maneka Gandhi v. Union of India",
      "citation": "AIR 1978 SC 597",
      "case_number": "Crl. A. No. 296 of 1977",
      "section": "Fundamental Rights - Article 21",
      "chunk_id": 5,
      "s3_url": "https://lexiq-supreme-court-pdfs.s3...",
      "content_preview": "First 200 chars..."
    }
  ],
  "num_similar_cases": 5
}
```

### Analysis Markdown Structure

```markdown
## Case Analysis

### Current Case Summary
[AI summary of the legal issues]

### Similar Precedents Found

#### 1. **Maneka Gandhi v. Union of India (AIR 1978 SC 597)**
**Relevance Score:** High  
**Section:** Fundamental Rights - Article 21  

**Why This Matters:**
[Detailed explanation of how this precedent applies to your case]

**Key Legal Principle:**
[What this case established]

**Direct Quote:**
> "Procedure established by law must be just, fair and reasonable..."

**How to Use This:**
[Practical advice for the lawyer]

📄 [View Full Case PDF](https://...)

---

[More precedents...]

## Strategic Recommendations
[Overall strategy for using these precedents]

## All References
- Maneka Gandhi v. Union of India (AIR 1978 SC 597) [PDF](link)
- [More cases...]
```

## 🎨 Use Cases

### For Lawyers

#### 1. **Case Preparation**
```python
# Upload your current case
result = analyzer.analyze_case_from_pdf("client_case.pdf", k=10)

# Get comprehensive analysis with precedents
print(result["analysis"])

# Save to file for case notes
with open("case_research.md", "w") as f:
    f.write(result["analysis"])
```

#### 2. **Quick Research**
```python
# Search by legal issue
cases = analyzer.find_similar_cases_only(
    "violation of Article 14 - arbitrary state action",
    k=20,
    with_scores=True
)

# Review relevance scores
for case in cases[:5]:
    print(f"{case['case_title']}: {case['similarity_score']:.3f}")
```

#### 3. **Argument Building**
```python
# Describe your argument
argument = """
The petitioner contends that the state action is arbitrary 
and violates the right to equality under Article 14...
"""

result = analyzer.analyze_case_from_text(argument, k=5)
# Get precedents that support this argument
```

#### 4. **Case Comparison**
```python
# Compare two cases
result = analyzer.compare_cases(
    case1_text="Facts of first case...",
    case2_text="Facts of second case..."
)

print(result["comparison"])
```

### For Law Firms

#### API Integration
```python
# Flask/FastAPI endpoint
@app.post("/analyze-client-case")
def analyze_client_case(file: UploadFile):
    # Save uploaded PDF
    temp_path = save_temp_file(file)
    
    # Analyze
    result = analyze_single_case(temp_path, is_pdf=True)
    
    # Return to frontend
    return {
        "analysis": result["analysis"],
        "precedents": result["similar_cases"]
    }
```

## 🔧 Configuration

### Adjust Number of Similar Cases

```python
# More comprehensive (slower)
result = analyzer.analyze_case_from_text(case, k=15)

# Faster, top results only
result = analyzer.analyze_case_from_text(case, k=3)
```

### Adjust Response Detail

```python
# Detailed analysis
result = analyzer.analyze_case_from_text(
    case,
    max_tokens=3000,  # Longer response
    temperature=0.2   # More factual
)

# Concise analysis
result = analyzer.analyze_case_from_text(
    case,
    max_tokens=1000,  # Shorter response
    temperature=0.3
)
```

### Temperature Settings

- `0.1-0.3`: Factual, conservative legal analysis (recommended)
- `0.4-0.6`: Balanced analysis with some creativity
- `0.7-0.9`: More creative arguments (use with caution)

## 📝 Example Workflow

### Complete Case Analysis Workflow

```python
from utils.case_similarity import CaseSimilarityAnalyzer

# 1. Initialize
analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# 2. Describe current case
current_case = """
Case Title: XYZ Corp vs. State of Maharashtra

Facts:
- Digital media platform challenges state law
- Law imposes prior censorship on online content
- Petitioner claims violation of Article 19(1)(a)

Legal Issues:
1. Is prior censorship on digital media constitutional?
2. Are restrictions reasonable under Article 19(2)?
3. What is the balance between free speech and public order?

Arguments:
- Digital media deserves same protection as traditional press
- Censorship mechanism lacks clear guidelines
- Imposes unreasonable restrictions on expression
"""

# 3. Find similar precedents
result = analyzer.analyze_case_from_text(current_case, k=5)

# 4. Review analysis
print("=" * 70)
print("CASE ANALYSIS")
print("=" * 70)
print(result["analysis"])

# 5. Get quick reference to cases
print("\n" + "=" * 70)
print("SIMILAR CASES SUMMARY")
print("=" * 70)
for case in result["similar_cases"]:
    print(f"\n• {case['case_title']}")
    print(f"  {case['citation']}")
    print(f"  📄 {case['s3_url']}")

# 6. Save for later
with open("case_research_xyz_corp.md", "w") as f:
    f.write(f"# Case Research: XYZ Corp vs. State\n\n")
    f.write(result["analysis"])

print("\n✓ Analysis saved to case_research_xyz_corp.md")
```

## 🔍 API Endpoints

### 1. Analyze Case from Text
**POST** `/api/analyze-case-text`

```json
{
  "case_description": "Full case description...",
  "k": 5
}
```

### 2. Analyze Case from PDF
**POST** `/api/analyze-case-pdf`

```
Form Data:
- file: (PDF file)
- k: 5
```

### 3. Find Similar Cases (Quick)
**POST** `/api/find-similar-cases`

```json
{
  "case_text": "Search query...",
  "k": 10,
  "with_scores": true
}
```

### 4. Compare Cases
**POST** `/api/compare-cases`

```json
{
  "case1_text": "First case...",
  "case2_text": "Second case..."
}
```

## 🎯 Advanced Features

### Similarity Scores

```python
# Get cases with relevance scores
cases = analyzer.find_similar_cases_only(
    "your case description",
    k=10,
    with_scores=True
)

# Filter by score threshold
high_relevance = [c for c in cases if c['similarity_score'] > 0.7]
```

### Section-Specific Search

The analyzer automatically tracks which sections of precedent cases are most relevant:

```python
result = analyzer.analyze_case_from_text(case)

for case in result["similar_cases"]:
    print(f"{case['case_title']}")
    print(f"  Relevant Section: {case['section']}")
    print(f"  Chunk ID: {case['chunk_id']}")
```

### Batch Analysis

```python
# Analyze multiple cases
cases_to_analyze = [
    "Case 1 description...",
    "Case 2 description...",
    "Case 3 description..."
]

results = []
for case in cases_to_analyze:
    result = analyzer.analyze_case_from_text(case, k=3)
    results.append(result)

# Compare patterns across cases
```

## 🐛 Troubleshooting

### PDF Links Not Showing

**Fixed!** PDF links now properly appear in responses. Make sure you:
1. Re-run `python process_documents.py` to update vector store with new metadata
2. Set `UPLOAD_TO_S3 = True` in `process_documents.py` if you want S3 links

### Low Similarity Scores

- Try rephrasing your case description
- Include more legal terminology
- Be more specific about the legal issues
- Increase `k` to get more results

### Analysis Too Generic

- Provide more detailed case facts
- Include specific legal issues and arguments
- Reference constitutional articles or specific laws
- Lower temperature for more focused analysis

## 📈 Performance

- **Search Time**: ~100-200ms for similarity search
- **Claude Analysis**: ~3-8s depending on complexity and max_tokens
- **Total Time**: ~4-10s for complete analysis
- **PDF Processing**: +2-5s for PDF parsing

## 🔐 Best Practices

1. **Provide Detailed Case Descriptions**
   - Include all relevant facts
   - State legal issues clearly
   - Mention applicable laws/articles

2. **Use Appropriate k Values**
   - Research: k=10-20
   - Quick lookup: k=3-5
   - Comprehensive: k=15-30

3. **Review Similarity Scores**
   - >0.8: Highly relevant
   - 0.6-0.8: Relevant
   - <0.6: Potentially relevant

4. **Save Results**
   - Keep markdown files for case notes
   - Build a knowledge base of researched issues
   - Track which precedents work for different cases

## 📦 Files Created

- `utils/case_similarity.py` - Core analyzer
- `case_analyzer.py` - Interactive CLI
- `case_api.py` - REST API server
- `test_case_analyzer.py` - Test suite

## 🎓 Next Steps

1. **Test the System**
   ```bash
   python test_case_analyzer.py
   ```

2. **Try Interactive Mode**
   ```bash
   python case_analyzer.py
   ```

3. **Start API Server**
   ```bash
   python case_api.py
   ```

4. **Integrate into Your App**
   - Add to Streamlit UI
   - Connect to your frontend
   - Build custom workflows

---

**Your case similarity analyzer is ready!** 🎉

This is the core feature lawyers will use to find relevant precedents for their cases.

