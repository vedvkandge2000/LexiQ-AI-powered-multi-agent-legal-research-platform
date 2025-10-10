# LexiQ Tests

Test scripts for LexiQ components.

## 🧪 Test Scripts

### 1. test_case_analyzer.py

**Purpose:** Test the case similarity analyzer.

**Run:**
```bash
python tests/test_case_analyzer.py
```

**Tests:**
- Case analysis from text
- Quick similarity search
- PDF analysis (if test PDF available)
- Batch queries

**Duration:** ~1-2 minutes

---

### 2. test_query.py

**Purpose:** Test the general query system.

**Run:**
```bash
python tests/test_query.py
```

**Tests:**
- Single query processing
- Batch queries
- Metadata retrieval
- Response formatting

**Duration:** ~30 seconds

---

### 3. test_claude.py

**Purpose:** Test Claude API integration.

**Run:**
```bash
python tests/test_claude.py
```

**Tests:**
- Basic Claude API calls
- Response formatting
- Error handling

**Duration:** ~10 seconds

---

## 🚀 Running All Tests

```bash
# Run all tests sequentially
python tests/test_case_analyzer.py
python tests/test_query.py
python tests/test_claude.py
```

## 📋 Test Requirements

- Vector store must be created (`python process_documents.py`)
- AWS credentials configured
- All dependencies installed (`pip install -r requirements.txt`)

## ✅ Expected Results

All tests should:
- ✅ Initialize successfully
- ✅ Retrieve documents from vector store
- ✅ Generate responses from Claude
- ✅ Display formatted output
- ✅ Show metadata (page numbers, PDF links, etc.)

## 🐛 Troubleshooting

**"Vector store not found"**
→ Run `python process_documents.py` first

**"AWS credentials error"**
→ Run `aws configure` or set environment variables

**Import errors**
→ Activate venv: `source venv/bin/activate`

---

## 📚 More Testing

For interactive testing, use:
```bash
python case_analyzer.py
```

For API testing, use:
```bash
python case_api.py
# Then use curl or Postman
```

---

See [../docs/USAGE_GUIDE.md](../docs/USAGE_GUIDE.md) for usage examples.

