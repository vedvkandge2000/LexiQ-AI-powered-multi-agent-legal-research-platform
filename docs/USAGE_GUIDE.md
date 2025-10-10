# LexiQ Usage Guide

Complete guide to using the LexiQ retrieval and query system.

## Quick Start

### 1. Interactive CLI Mode

The easiest way to start querying:

```bash
python orchestrator.py
```

Example session:
```
🏛️  LexiQ - Supreme Court Case Law Assistant
================================================

💡 Type your legal question or 'exit' to quit.
------------------------------------------------------------

📝 Your Query: What are the key cases on freedom of speech?

🔍 Searching for: What are the key cases on freedom of speech?
✓ Retrieved 5 relevant documents
🤖 Generating response with Claude...

============================================================
📋 RESPONSE
============================================================

## Summary
Freedom of speech under Article 19(1)(a) has been extensively...

## Relevant Precedents
1. **Romesh Thappar v. State of Madras (AIR 1950 SC 124, Page 3)**  
   > "Freedom of speech is a cardinal value essential to democracy..."
   [View Full Case PDF](https://...)

...
```

### 2. Python Script

Create a script to query programmatically:

```python
from utils.query_handler import QueryHandler

# Initialize
handler = QueryHandler(vector_store_dir="data/vector_store", k=5)
handler.initialize()

# Query
result = handler.query("What is the basic structure doctrine?")

# Access results
print(result["response"])          # Markdown formatted answer
print(result["num_documents"])     # Number of sources
print(result["retrieved_documents"])  # Case metadata
```

### 3. Single Query Function

For simple one-off queries:

```python
from orchestrator import query_once

result = query_once("Cases on Article 14 equality")
print(result["response"])
```

### 4. REST API

Run the Flask API server:

```bash
python example_api.py
```

Then make HTTP requests:

```bash
# Query endpoint
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Article 21?"}'

# Search-only endpoint (no Claude)
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "freedom of speech", "k": 10}'

# Batch query endpoint
curl -X POST http://localhost:5000/api/batch-query \
  -H "Content-Type: application/json" \
  -d '{
    "questions": [
      "What is Article 14?",
      "Cases on freedom of religion"
    ]
  }'
```

## Configuration Options

### Retrieval Parameters

```python
handler = QueryHandler(
    vector_store_dir="data/vector_store",  # Path to FAISS index
    k=5  # Number of relevant documents to retrieve
)
```

### Query Parameters

```python
result = handler.query(
    user_query="Your question",
    max_tokens=1500,     # Max response length (Claude)
    temperature=0.3      # 0.0 = factual, 1.0 = creative
)
```

### Retriever Methods

```python
from utils.retriever import LegalDocumentRetriever

retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
retriever.load_vector_store()

# Basic retrieval
docs = retriever.retrieve("freedom of speech", k=5)

# Retrieval with scores
docs_with_scores = retriever.retrieve_with_scores("Article 14", k=3)
for doc, score in docs_with_scores:
    print(f"Score: {score}, Case: {doc.metadata['case_title']}")

# Get metadata only
metadata = retriever.get_metadata_summary(docs)
```

## Response Structure

All query results return a dictionary:

```python
{
    "query": "User's original question",
    "response": "Markdown formatted answer from Claude",
    "retrieved_documents": [
        {
            "case_title": "Maneka Gandhi v. Union of India",
            "citation": "AIR 1978 SC 597",
            "page_number": 5,
            "s3_url": "https://lexiq-supreme-court-pdfs.s3...",
            "content_preview": "First 200 chars of chunk..."
        },
        ...
    ],
    "num_documents": 5
}
```

## Example Queries

### Constitutional Law
```python
queries = [
    "What is the basic structure doctrine?",
    "Explain Article 14 - Right to Equality",
    "Cases on Article 19(1)(a) freedom of speech",
    "Article 21 - Right to Life and Personal Liberty",
    "What is the Kesavananda Bharati case about?"
]
```

### Search by Topic
```python
queries = [
    "Supreme Court cases on environmental law",
    "Landmark judgments on women's rights",
    "Cases related to criminal procedure",
    "Judicial review in India"
]
```

### Legal Doctrines
```python
queries = [
    "What is judicial review?",
    "Explain the doctrine of prospective overruling",
    "What is public interest litigation?",
    "Doctrine of legitimate expectation"
]
```

## Integration Examples

### Streamlit App

```python
import streamlit as st
from utils.query_handler import QueryHandler

@st.cache_resource
def load_query_handler():
    handler = QueryHandler(vector_store_dir="data/vector_store")
    handler.initialize()
    return handler

handler = load_query_handler()

st.title("🏛️ LexiQ - Supreme Court Assistant")

query = st.text_input("Ask a legal question:")
if st.button("Search") and query:
    with st.spinner("Searching case law..."):
        result = handler.query(query)
    
    st.markdown(result["response"])
    
    with st.expander("📚 View Sources"):
        for doc in result["retrieved_documents"]:
            st.write(f"**{doc['case_title']}** ({doc['citation']})")
            st.write(f"Page {doc['page_number']}")
            if doc['s3_url']:
                st.markdown(f"[View PDF]({doc['s3_url']})")
```

### FastAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from utils.query_handler import QueryHandler

app = FastAPI()

# Initialize once at startup
handler = QueryHandler(vector_store_dir="data/vector_store")

@app.on_event("startup")
async def startup_event():
    handler.initialize()

class QueryRequest(BaseModel):
    question: str
    max_tokens: int = 1500

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    try:
        result = handler.query(
            request.question,
            max_tokens=request.max_tokens
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### JavaScript Frontend

```javascript
async function queryLexiQ(question) {
    const response = await fetch('http://localhost:5000/api/query', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question })
    });
    
    const result = await response.json();
    
    // Display markdown response
    document.getElementById('answer').innerHTML = marked.parse(result.answer);
    
    // Display sources
    const sourcesHTML = result.sources.map(source => `
        <div class="source">
            <h4>${source.case_title}</h4>
            <p>${source.citation} - Page ${source.page_number}</p>
            <a href="${source.s3_url}" target="_blank">View PDF</a>
        </div>
    `).join('');
    
    document.getElementById('sources').innerHTML = sourcesHTML;
}

// Usage
queryLexiQ("What is Article 14?");
```

## Testing

### Run Test Script

```bash
python test_query.py
```

### Unit Testing

```python
import pytest
from utils.query_handler import QueryHandler

@pytest.fixture
def handler():
    h = QueryHandler(vector_store_dir="data/vector_store", k=3)
    h.initialize()
    return h

def test_basic_query(handler):
    result = handler.query("What is Article 14?")
    assert result["query"] == "What is Article 14?"
    assert result["num_documents"] == 3
    assert "Summary" in result["response"]

def test_batch_query(handler):
    queries = ["Article 14", "Article 19"]
    results = handler.batch_query(queries)
    assert len(results) == 2
```

## Performance Optimization

### 1. Cache Query Handler

Initialize once, reuse many times:

```python
# ❌ Slow - reinitializes every time
def handle_request(question):
    handler = QueryHandler()
    handler.initialize()  # Loads vector store each time!
    return handler.query(question)

# ✅ Fast - initialize once
handler = QueryHandler()
handler.initialize()

def handle_request(question):
    return handler.query(question)  # Reuses loaded vector store
```

### 2. Adjust Retrieval Count

Fewer documents = faster:

```python
# For quick lookups
handler = QueryHandler(k=3)

# For comprehensive research
handler = QueryHandler(k=10)
```

### 3. Reduce Token Limit

```python
# Faster, shorter responses
result = handler.query(question, max_tokens=500)

# Slower, more detailed responses
result = handler.query(question, max_tokens=2000)
```

## Troubleshooting

### Vector Store Not Found

```
Error: Vector store not loaded
```

**Solution**: Make sure you've run `process_documents.py` first:
```bash
python process_documents.py
```

### AWS Credentials Error

```
Error: Unable to locate credentials
```

**Solution**: Configure AWS credentials:
```bash
aws configure
# OR
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### No Relevant Results

If Claude says "insufficient context":
- Try rephrasing your question
- Use more specific legal terms
- Check if your documents contain relevant cases

## Best Practices

1. **Specific Questions**: Ask specific legal questions rather than broad topics
   - ✅ "What did the Supreme Court rule in Kesavananda Bharati about basic structure?"
   - ❌ "Tell me about constitutional law"

2. **Legal Terminology**: Use proper legal terms for better retrieval
   - ✅ "Article 14 equality jurisprudence"
   - ❌ "fairness laws"

3. **Case Citations**: Include citations if you know them
   - ✅ "Explain Maneka Gandhi v. Union of India"
   - ✅ "What is AIR 1978 SC 597 about?"

4. **Follow-up Questions**: For multi-part questions, query separately
   - First: "What is Article 14?"
   - Then: "How has Article 14 been interpreted?"

5. **Temperature Settings**:
   - Legal research: `temperature=0.1-0.3` (factual)
   - Legal writing help: `temperature=0.5-0.7` (creative)

## Next Steps

- **Integrate into UI**: Add to `app.py` for Streamlit interface
- **Add Filters**: Filter by date, court level, subject
- **Chat History**: Implement conversation memory
- **Export**: Add PDF/Word export of responses
- **Analytics**: Track popular queries and sources

For more details, see `RETRIEVAL_README.md`.

