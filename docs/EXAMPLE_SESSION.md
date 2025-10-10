# Example Interactive Session

## 🎬 Complete Walkthrough

Here's what users see when they use the interactive interface:

---

## Session 1: Quick Search with Mode Selection

```bash
$ python case_analyzer.py
```

```
======================================================================
⚖️  LexiQ Case Analyzer - Find Similar Precedents
======================================================================

Initializing Case Similarity Analyzer...
Loading vector store...
✓ Vector store loaded successfully!
✓ Analyzer ready!

======================================================================
📋 OPTIONS
======================================================================
1. Analyze case from text description
2. Analyze case from PDF file
3. Quick search for similar cases (no analysis)
4. Exit

Select option (1-4): 3

----------------------------------------------------------------------
🔍 Quick Search
----------------------------------------------------------------------

Search Mode:
1. Unique Cases (deduplicated) - One result per case
2. All Chunks - May include multiple chunks from same case
3. Grouped by Case - Multiple relevant chunks per case

Select mode (1-3, default 1): 1          ← User chooses mode 1

Enter search text (case facts, legal issues, etc.):
freedom of speech reasonable restrictions  ← User enters search

How many results? (default 10): 15        ← User asks for 15

🔍 Finding 15 similar cases...
✓ Found 4 unique cases

======================================================================
🔍 SEARCH RESULTS (4 unique cases found)
======================================================================

1. **Railway Protection Force & Ors. v. Prem Chand Kumar & Ors.**
   Citation: [2025] 9 S.C.R. 558 : 2025 INSC 1083
   Case Number: Civil Appeal No. 8127 of 2013
   Page Number: 1
   Similarity: 1.6192
   Section: Issue for Consideration
   📄 PDF: s3://lexiq-supreme-court-pdfs/cases/...
   Preview: Whether a reserved candidate who has been empanelled ...

2. **Union of India & Ors. v. Sajib Roy**
   Citation: [2025] 9 S.C.R. 542 : 2025 INSC 1084
   Case Number: Civil Appeal No. 19 of 2025
   Page Number: 1
   Similarity: 1.6506
   Section: Issue for Consideration
   📄 PDF: s3://lexiq-supreme-court-pdfs/cases/...
   Preview: Whether a reserved candidate who has been empanelled ...

... (showing 4 total)

----------------------------------------------------------------------
```

---

## Session 2: Quick Search - Grouped Mode

```
Select option (1-4): 3

----------------------------------------------------------------------
🔍 Quick Search
----------------------------------------------------------------------

Search Mode:
1. Unique Cases (deduplicated) - One result per case
2. All Chunks - May include multiple chunks from same case
3. Grouped by Case - Multiple relevant chunks per case

Select mode (1-3, default 1): 3          ← User chooses mode 3

Enter search text (case facts, legal issues, etc.):
Article 14 equality arbitrary state action

How many unique cases? (default 5): 5    ← User asks for 5 cases
Max chunks per case? (default 3): 4      ← 4 chunks each

🔍 Finding 5 cases with up to 4 chunks each...
✓ Found 4 unique cases with 15 total relevant chunks

======================================================================
🔍 SEARCH RESULTS (4 cases, 15 chunks)
======================================================================

1. **Railway Protection Force & Ors. v. Prem Chand Kumar & Ors.**
   Citation: [2025] 9 S.C.R. 558 : 2025 INSC 1083
   Case Number: Civil Appeal No. 8127 of 2013
   Best Similarity: 1.6192
   📄 PDF: s3://lexiq-supreme-court-pdfs/cases/...

   Relevant Chunks (4):
   1. Page 1, Section: Issue for Consideration...
      Similarity: 1.6192
      Whether a reserved candidate who has been...
   2. Page 2, Section: Held: View expressed by the High...
      Similarity: 1.6346
      The High Court has correctly interpreted...
   3. Page 3, Section: List of Keywords...
      Similarity: 1.6590
      Service law - Reservation - Selection...
   4. Page 5, Section: Analysis...
      Similarity: 1.6723
      The constitutional mandate requires...

2. **Union of India & Ors. v. Sajib Roy**
   (Similar detailed breakdown with 4 chunks)
   ...
```

---

## Session 3: Full Case Analysis with Options

```
Select option (1-4): 1

----------------------------------------------------------------------
📝 Enter Case Description
----------------------------------------------------------------------
Describe your current case (facts, legal issues, parties, etc.)
Type 'END' on a new line when finished:

Case Title: Tech Platform vs State Government

Facts: 
State passed law requiring government approval before 
posting content online. Client argues this violates 
freedom of speech under Article 19(1)(a).

Legal Issues:
1. Is prior approval/censorship constitutional?
2. Are restrictions reasonable under Article 19(2)?
3. Balance between free speech and public order?

Relief: Declaration that law is unconstitutional.
END

How many similar cases to retrieve? (default 5, max 20): 10

Response Detail Level:
1. Concise (max_tokens=1000)
2. Balanced (max_tokens=2000)
3. Comprehensive (max_tokens=3000)
Select level (1-3, default 2): 3         ← User wants detailed

🔍 Analyzing case and finding similar precedents...
📝 Case description length: 387 characters
✓ Found 10 similar precedents
🤖 Generating detailed analysis with Claude...

======================================================================
📊 CASE ANALYSIS RESULTS
======================================================================

## Case Analysis

### Current Case Summary
The current case involves constitutional challenges to content 
regulation on digital platforms, specifically concerning the 
constitutionality of prior approval requirements...

### Similar Precedents Found

#### 1. **Romesh Thappar v. State of Madras (AIR 1950 SC 124) - Page 3**
**Relevance Score:** High
**Section:** Freedom of Speech and Expression

**Why This Matters:**
This landmark case established that prior restraint on publication 
is prima facie unconstitutional unless it falls within the narrow 
exceptions specified in Article 19(2)...

**Key Legal Principle:**
Freedom of speech cannot be curtailed except under very narrow 
circumstances outlined in Article 19(2).

**Direct Quote:**
> "Freedom of speech and of the press lay at the foundation of 
> all democratic organizations..."

**How to Use This:**
Cite this case to establish that pre-approval mechanisms require 
meeting a very high constitutional bar...

📄 [View Full Case PDF](s3://...) | Page 3

... (9 more precedents with full analysis)

======================================================================
📚 Retrieved 10 similar precedents
======================================================================

QUICK REFERENCE - Similar Cases:

1. Romesh Thappar v. State of Madras
   AIR 1950 SC 124
   Case Number: Appeal No. 39 of 1949
   Page Number: 3
   📄 s3://lexiq-supreme-court-pdfs/cases/...

... (10 total)

----------------------------------------------------------------------
Save results to file? (y/n): y
Enter filename (default: case_analysis.md): my_case_analysis.md
✓ Results saved to my_case_analysis.md
```

---

## Session 4: PDF Upload with Options

```
Select option (1-4): 2

----------------------------------------------------------------------
📄 Analyze Case from PDF
----------------------------------------------------------------------
Enter path to PDF file: data/pdfs/client_case.pdf

How many similar cases to retrieve? (default 5, max 20): 8

Response Detail Level:
1. Concise (max_tokens=1000)
2. Balanced (max_tokens=2000)
3. Comprehensive (max_tokens=3000)
Select level (1-3, default 2): 2         ← Balanced

📄 Processing PDF: client_case.pdf
✓ Extracted case details:
   Title: Client Case Title
   Citation: [2025] SC 123
   Text length: 5420 characters

🔍 Analyzing case and finding similar precedents...
✓ Found 8 similar precedents
🤖 Generating response with Claude...

... (Results similar to Session 3)
```

---

## Quick Tips

### Using Defaults

Just press **Enter** to use default values:

```
Select mode (1-3, default 1): [Enter]     ← Uses mode 1
How many results? (default 10): [Enter]    ← Uses 10
Select level (1-3, default 2): [Enter]     ← Uses Balanced
```

### Choosing the Right Mode

**Mode 1 (Deduplicated)** - Most common
```
Use when: Need a list of unique cases
Example: "Find me 10 relevant precedents"
```

**Mode 2 (All Chunks)** - For deep research
```
Use when: Looking for all relevant passages
Example: "Find all mentions of 'basic structure'"
```

**Mode 3 (Grouped)** - For comprehensive analysis
```
Use when: Need multiple quotes per case
Example: "Analyze top 5 cases in detail"
```

---

## API Examples

### Python Quick Use

```python
from utils.case_similarity import CaseSimilarityAnalyzer

# Initialize once
analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Mode 1: Get 15 unique cases
cases = analyzer.find_similar_cases_only(
    "freedom of speech",
    k=15,
    deduplicate=True
)

# Mode 3: Get 5 cases with 4 chunks each
grouped = analyzer.find_similar_cases_with_chunks(
    "freedom of speech",
    k_cases=5,
    max_chunks_per_case=4
)
```

### REST API Quick Use

```bash
# Deduplicated search
curl -X POST http://localhost:5001/api/find-similar-cases \
  -H "Content-Type: application/json" \
  -d '{"case_text": "freedom of speech", "k": 15, "deduplicate": true}'

# Grouped search
curl -X POST http://localhost:5001/api/find-similar-cases-with-chunks \
  -H "Content-Type: application/json" \
  -d '{"case_text": "freedom of speech", "k_cases": 5, "max_chunks_per_case": 4}'
```

---

**Everything is now user-controlled! No more hardcoded values.** 🎉

Try it now:
```bash
python case_analyzer.py
```

