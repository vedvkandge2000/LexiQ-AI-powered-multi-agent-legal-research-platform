# LexiQ - Project Structure

## 📁 Organized File Structure

```
lexiq/
│
├── 📄 README.md                    # Main project documentation
├── 📄 requirements.txt             # Python dependencies
├── 📄 .env                         # Environment variables (AWS keys)
├── 📄 PROJECT_STRUCTURE.md         # This file
│
├── 🎯 Main Scripts
│   ├── process_documents.py        # Process PDFs → vector store
│   ├── case_analyzer.py            # Interactive case analyzer ⭐
│   ├── orchestrator.py             # General legal queries
│   ├── case_api.py                 # Case similarity API (port 5001)
│   ├── example_api.py              # General query API (port 5000)
│   └── app.py                      # Streamlit UI (optional)
│
├── 📂 utils/                       # Core Python modules
│   ├── __init__.py
│   ├── pdf_parser.py               # PDF text extraction
│   ├── text_chunker.py             # Semantic text chunking
│   ├── vector_store.py             # FAISS vector store management
│   ├── retriever.py                # Semantic search & retrieval
│   ├── query_handler.py            # Query orchestration
│   ├── case_similarity.py          # Case similarity analysis ⭐
│   ├── pipeline.py                 # Document processing pipeline
│   ├── s3_uploader.py              # AWS S3 integration
│   └── README.md                   # Utils module documentation
│
├── 📂 aws/                         # AWS integration
│   └── bedrock_client.py           # Claude API wrapper
│
├── 📂 data/                        # Data storage
│   ├── pdfs/                       # Input PDF files (Supreme Court cases)
│   │   ├── 1.pdf
│   │   ├── 2.pdf
│   │   └── ...
│   └── vector_store/               # FAISS index files
│       ├── index.faiss
│       └── index.pkl
│
├── 📂 docs/                        # 📚 All Documentation (15 files)
│   ├── README.md                   # Documentation index
│   │
│   ├── Getting Started
│   │   ├── QUICKSTART.md           # Quick start guide
│   │   └── PROJECT_SUMMARY.md      # Complete overview
│   │
│   ├── User Guides
│   │   ├── USAGE_GUIDE.md          # Complete usage guide
│   │   ├── USER_OPTIONS_GUIDE.md   # User controls
│   │   └── EXAMPLE_SESSION.md      # Real examples
│   │
│   ├── Feature Docs
│   │   ├── CASE_SIMILARITY_README.md       # Case similarity
│   │   ├── DEDUPLICATION_GUIDE.md          # Search modes
│   │   ├── QUICK_ANSWER_DEDUPLICATION.md   # Quick ref
│   │   ├── RETRIEVAL_README.md             # Retrieval system
│   │   └── PAGE_NUMBER_UPDATE.md           # Page tracking
│   │
│   └── Technical
│       ├── IMPLEMENTATION_COMPLETE.md      # What was built
│       ├── FINAL_SUMMARY.md                # Final summary
│       ├── RETRIEVAL_SUMMARY.md            # Retrieval ref
│       └── USER_CONTROL_SUMMARY.md         # Controls ref
│
├── 📂 examples/                    # Demo scripts (3 files)
│   ├── README.md                   # Examples index
│   ├── demo_deduplication.py       # Deduplication demo
│   └── demo_retrieval.py           # Retrieval demo
│
├── 📂 tests/                       # Test scripts (4 files)
│   ├── README.md                   # Tests index
│   ├── test_case_analyzer.py       # Test case analyzer
│   ├── test_query.py               # Test queries
│   └── test_claude.py              # Test Claude API
│
├── 📂 agents/                      # (Future: AI agents)
├── 📂 prompts/                     # (Future: Prompt templates)
│
└── 📂 venv/                        # Python virtual environment
    └── ...
```

---

## 📊 File Count Summary

| Category | Count | Location |
|----------|-------|----------|
| **Main Scripts** | 6 | Root |
| **Core Modules** | 9 | `utils/` |
| **Documentation** | 15 | `docs/` |
| **Examples** | 2 | `examples/` |
| **Tests** | 3 | `tests/` |
| **Data Files** | 7 PDFs + index | `data/` |
| **Total** | 42+ files | - |

---

## 🎯 Quick Navigation

### I want to...

**Start using LexiQ**
→ `README.md` → `docs/QUICKSTART.md`

**Find similar cases**
→ `python case_analyzer.py`

**Read documentation**
→ `docs/README.md`

**See examples**
→ `examples/README.md`

**Run tests**
→ `tests/README.md`

**Understand the code**
→ `utils/` modules

---

## 📚 Documentation Organization

### docs/ (15 documents)

**Getting Started (2)**
- QUICKSTART.md - 3-step guide
- PROJECT_SUMMARY.md - Complete overview

**User Guides (3)**
- USAGE_GUIDE.md - How to use everything
- USER_OPTIONS_GUIDE.md - All controls
- EXAMPLE_SESSION.md - Real examples

**Features (5)**
- CASE_SIMILARITY_README.md - Main feature
- DEDUPLICATION_GUIDE.md - Search modes
- QUICK_ANSWER_DEDUPLICATION.md - TL;DR
- RETRIEVAL_README.md - How search works
- PAGE_NUMBER_UPDATE.md - Page tracking

**Technical (4)**
- IMPLEMENTATION_COMPLETE.md - What's built
- FINAL_SUMMARY.md - Feature summary
- RETRIEVAL_SUMMARY.md - Quick reference
- USER_CONTROL_SUMMARY.md - Controls

**Index (1)**
- README.md - Navigation guide

---

## 🚀 Key Entry Points

### For End Users (Lawyers)

```bash
# Interactive case analyzer
python case_analyzer.py

# Read the guides
cat docs/QUICKSTART.md
cat docs/USAGE_GUIDE.md
```

### For Developers

```python
# Import the modules
from utils.case_similarity import CaseSimilarityAnalyzer
from utils.query_handler import QueryHandler

# Read the docs
docs/PROJECT_SUMMARY.md
docs/CASE_SIMILARITY_README.md
```

### For API Users

```bash
# Start the API
python case_api.py

# Read API docs
docs/CASE_SIMILARITY_README.md
docs/USER_OPTIONS_GUIDE.md
```

---

## 📦 Module Organization

### utils/ - Core Functionality

| Module | Purpose |
|--------|---------|
| `pdf_parser.py` | Extract text from PDFs |
| `text_chunker.py` | Intelligent text chunking |
| `vector_store.py` | FAISS vector store |
| `retriever.py` | Semantic search |
| `query_handler.py` | General queries |
| `case_similarity.py` | Case analysis ⭐ |
| `pipeline.py` | Complete pipeline |
| `s3_uploader.py` | S3 integration |

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python packages |
| `.env` | AWS credentials |
| `.gitignore` | Git exclusions |

---

## 🎓 Learning Path

### Beginner
1. `README.md` - Overview
2. `docs/QUICKSTART.md` - Get started
3. `python case_analyzer.py` - Try it!
4. `docs/USAGE_GUIDE.md` - Learn features

### Intermediate
1. `docs/USER_OPTIONS_GUIDE.md` - All controls
2. `examples/demo_deduplication.py` - See modes
3. `docs/DEDUPLICATION_GUIDE.md` - Understand search
4. `docs/EXAMPLE_SESSION.md` - Real usage

### Advanced
1. `docs/PROJECT_SUMMARY.md` - Architecture
2. `docs/CASE_SIMILARITY_README.md` - API reference
3. `utils/case_similarity.py` - Source code
4. `docs/IMPLEMENTATION_COMPLETE.md` - Technical details

---

## 📝 File Descriptions

### Root Level

- **README.md** - Main project documentation
- **process_documents.py** - Process PDFs into vector store
- **case_analyzer.py** - Interactive case analyzer (main feature)
- **orchestrator.py** - General legal query interface
- **case_api.py** - REST API for case similarity
- **example_api.py** - REST API for general queries

### Supporting Folders

- **docs/** - All documentation (well organized)
- **examples/** - Demo scripts to try features
- **tests/** - Test scripts to verify functionality
- **utils/** - Core Python modules (the engine)
- **aws/** - Cloud integration (Bedrock/S3)
- **data/** - PDFs and vector store

---

## 🎯 Most Important Files

### Must Read
1. `README.md` - Start here!
2. `docs/QUICKSTART.md` - Get going
3. `docs/USAGE_GUIDE.md` - Learn everything

### Must Try
1. `case_analyzer.py` - Main app
2. `examples/demo_deduplication.py` - See features
3. `tests/test_case_analyzer.py` - Verify it works

### Must Know
1. `docs/USER_OPTIONS_GUIDE.md` - All controls
2. `docs/DEDUPLICATION_GUIDE.md` - Search modes
3. `docs/CASE_SIMILARITY_README.md` - API reference

---

## ✨ Clean & Organized!

The project is now well-structured:

✅ **Docs** in `docs/` (15 files)  
✅ **Examples** in `examples/` (2 demos)  
✅ **Tests** in `tests/` (3 tests)  
✅ **Code** in `utils/` (9 modules)  
✅ **Main scripts** in root (6 files)  
✅ **README.md** in each folder  

Everything has its place! 🎉

