# LexiQ - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Ensure Vector Store Exists

```bash
# If you haven't processed your PDFs yet:
python process_documents.py
```

This creates the FAISS index from your Supreme Court case PDFs.

### Step 2: Try the Case Analyzer

```bash
python case_analyzer.py
```

Select option 1 and paste this sample case:

```
Case Title: Digital Media Platform v. State

Facts:
A social media company challenges a new state law requiring 
government pre-approval of all online content before publication.

Legal Issues:
1. Does pre-approval violate Article 19(1)(a)?
2. Are such restrictions reasonable under Article 19(2)?

Relief Sought:
Declaration that the law is unconstitutional.
```

Type `END` when done, then enter `5` for number of similar cases.

### Step 3: Review Results

You'll get:
- ✅ AI analysis of your case
- ✅ 5 similar precedent cases
- ✅ Direct quotes from each case
- ✅ Why each is relevant
- ✅ PDF links to full cases
- ✅ Strategic recommendations

## 🎯 Your Main Use Cases

### For General Legal Questions

```bash
python orchestrator.py
```

Ask questions like:
- "What is the basic structure doctrine?"
- "Explain Article 14 of the Constitution"
- "Cases on freedom of speech"

### For Finding Similar Cases (Main Feature!)

```bash
python case_analyzer.py
```

Options:
1. **Type case description** - Paste your case facts
2. **Upload PDF** - Upload your client's case file
3. **Quick search** - Fast search without AI analysis

### For API Integration

```bash
# Start server
python case_api.py

# In another terminal, test it:
curl -X POST http://localhost:5001/api/analyze-case-text \
  -H "Content-Type: application/json" \
  -d '{
    "case_description": "Your case here...",
    "k": 5
  }'
```

## 📝 Python Usage

```python
from utils.case_similarity import CaseSimilarityAnalyzer

# Initialize
analyzer = CaseSimilarityAnalyzer()
analyzer.initialize()

# Analyze a case
result = analyzer.analyze_case_from_text(
    "Your case description...",
    k=5
)

# Print results
print(result["analysis"])  # Full markdown analysis

# Access similar cases
for case in result["similar_cases"]:
    print(f"{case['case_title']}")
    print(f"  Citation: {case['citation']}")
    print(f"  PDF: {case['s3_url']}")
```

## 🔧 Common Commands

```bash
# Process new PDFs
python process_documents.py

# Interactive case analysis (main feature)
python case_analyzer.py

# General legal queries
python orchestrator.py

# Run tests
python test_case_analyzer.py

# Start API server
python case_api.py

# Start general query API
python example_api.py
```

## 🎨 Sample Queries

### Case Similarity (case_analyzer.py)

```
"Client arrested without warrant. Police claim national security. 
Challenge habeas corpus rights under Article 21 and 22."

"Company merger blocked by government. Arbitrary exercise of power. 
Challenge under Article 14 - equality and non-arbitrariness."

"Student expelled for social media post criticizing university. 
First Amendment / Article 19 free speech issue."
```

### General Questions (orchestrator.py)

```
"What are the key cases on judicial review?"

"Explain the Kesavananda Bharati judgment"

"Cases interpreting Article 21 - right to life"
```

## ✨ Key Features

### What Makes LexiQ Special

1. **Semantic Search** - Finds cases by meaning, not keywords
2. **AI Analysis** - Claude explains why each case is relevant
3. **Direct Quotes** - Actual excerpts from precedents
4. **PDF Links** - Clickable links to full cases
5. **Strategic Advice** - How to use the precedents
6. **Chain-of-Thought** - Explains the legal connections

### Output Format

Every analysis includes:

```markdown
## Case Analysis
[Summary of your case's legal issues]

## Similar Precedents Found
1. **Case Name (Citation)**
   Section: [Which part of the case]
   Why Relevant: [Specific connection to your case]
   Key Excerpt: > "Direct quote..."
   📄 [PDF Link](url)

## Strategic Recommendations
[How to use these precedents]

## All References
[Complete list with PDF links]
```

## 🐛 Troubleshooting

### "Vector store not found"
```bash
python process_documents.py
```

### "AWS credentials error"
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### "Import error"
```bash
pip install -r requirements.txt
```

## 📚 Learn More

- **PROJECT_SUMMARY.md** - Complete overview
- **CASE_SIMILARITY_README.md** - Detailed case similarity docs
- **USAGE_GUIDE.md** - More examples
- **RETRIEVAL_README.md** - Technical details

## 🎯 Next Steps

1. ✅ Try the interactive case analyzer
2. ✅ Test with your own case descriptions
3. ✅ Upload a PDF to analyze
4. ✅ Start the API for frontend integration
5. ✅ Review the detailed documentation

---

**Ready to revolutionize legal research!** 🏛️✨

Questions? Check the detailed docs or reach out.

