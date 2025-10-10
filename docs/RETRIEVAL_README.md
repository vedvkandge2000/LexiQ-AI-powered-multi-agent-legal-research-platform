# LexiQ Retrieval & Query System

## Overview

The retrieval system provides semantic search over Supreme Court case law documents, retrieves relevant precedents, and generates comprehensive legal responses using Claude via AWS Bedrock.

## Architecture

### Components

1. **`utils/retriever.py`** - `LegalDocumentRetriever`
   - Loads FAISS vector store
   - Performs semantic search
   - Formats retrieved documents with metadata

2. **`utils/query_handler.py`** - `QueryHandler`
   - Orchestrates retrieval + response generation
   - Integrates with Claude via Bedrock
   - Formats responses in markdown

3. **`orchestrator.py`** - Main CLI interface
   - Interactive query loop
   - Handles user input/output
   - Provides `query_once()` for API integration

## Usage

### Interactive CLI Mode

```bash
python orchestrator.py
```

This launches an interactive prompt where you can ask legal questions:

```
🏛️  LexiQ - Supreme Court Case Law Assistant
================================================

💡 Type your legal question or 'exit' to quit.

📝 Your Query: What are the key cases on freedom of speech?
```

### Programmatic Usage

```python
from utils.query_handler import QueryHandler

# Initialize
query_handler = QueryHandler(
    vector_store_dir="data/vector_store",
    k=5  # Retrieve top 5 relevant cases
)

query_handler.initialize()

# Query
result = query_handler.query("What is the basic structure doctrine?")

print(result["response"])  # Formatted markdown response
print(result["retrieved_documents"])  # List of case metadata
```

### API Integration

```python
from orchestrator import query_once

# Simple one-shot query
result = query_once("Cases related to Article 21")

# Result structure:
{
    "query": "Cases related to Article 21",
    "response": "## Summary\n...",  # Markdown formatted
    "retrieved_documents": [
        {
            "case_title": "Maneka Gandhi v. Union of India",
            "citation": "AIR 1978 SC 597",
            "page_number": 5,
            "s3_url": "https://...",
            "content_preview": "..."
        },
        ...
    ],
    "num_documents": 5
}
```

## Response Format

Responses are formatted in markdown with:

### 1. Summary
Concise explanation in plain English

### 2. Relevant Precedents
List of cases with:
- Case title, citation, year, page number
- Quoted relevant excerpt (2-3 lines)
- Clickable PDF link

### 3. References
Complete list of all citations

## Configuration

### In `orchestrator.py`:

```python
VECTOR_STORE_DIR = "data/vector_store"  # Path to FAISS store
NUM_RESULTS = 5  # Number of cases to retrieve
```

### In `QueryHandler`:

```python
query_handler.query(
    user_query="Your question",
    max_tokens=1500,      # Max response length
    temperature=0.3       # Lower = more factual, higher = more creative
)
```

## Features

### Semantic Search
- Uses Amazon Titan embeddings for query encoding
- FAISS vector similarity search
- Retrieves most relevant case chunks

### Metadata Enrichment
Each retrieved chunk includes:
- Case title
- Official citation
- Page number
- S3 PDF URL

### Claude Integration
- Powered by Claude 3 Sonnet via Bedrock
- Context-aware responses
- Proper legal formatting with citations

### Batch Processing
```python
queries = [
    "What is Article 14?",
    "Cases on freedom of religion"
]

results = query_handler.batch_query(queries)
```

## Testing

Run the test script:

```bash
python test_query.py
```

This will:
1. Load the vector store
2. Run a sample query
3. Display the formatted response
4. Show metadata for retrieved cases

## Frontend Integration

For a web app, use the `query_once()` function:

```python
# In your Flask/FastAPI endpoint
from orchestrator import query_once

@app.post("/api/query")
def handle_query(request):
    user_question = request.json["question"]
    result = query_once(user_question)
    
    return {
        "answer": result["response"],  # Markdown response
        "sources": result["retrieved_documents"]  # Case metadata
    }
```

Then in your frontend, render the markdown and create clickable PDF links from the S3 URLs.

## System Prompt

The system uses a custom legal assistant prompt that ensures:
- Accurate citations
- Clear explanations
- Relevant case law references
- Professional legal formatting
- Clickable source links

See `LEXIQ_SYSTEM_PROMPT` in `utils/query_handler.py` to customize.

## Error Handling

The system handles:
- Missing vector store → Clear error message
- Bedrock API failures → Fallback error response
- Empty queries → Validation prompt
- No relevant results → Claude indicates insufficient context

## Performance

- **Vector Search**: ~100ms for top-k retrieval
- **Claude Response**: ~2-5s depending on complexity
- **Total Query Time**: ~3-6s end-to-end

## Next Steps

1. **Add to `app.py`**: Integrate query handler into Streamlit UI
2. **Caching**: Add Redis/memory cache for common queries
3. **Filters**: Add date range, court level, subject filters
4. **Conversation**: Add chat history for follow-up questions
5. **Export**: Add PDF/Word export of responses

