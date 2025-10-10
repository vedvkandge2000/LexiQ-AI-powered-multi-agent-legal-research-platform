# Utils Package - Legal Document Processing

This package provides modular components for processing legal documents (Supreme Court judgments) including parsing, chunking, embedding, and storage.

## Architecture

The package is organized into separate modules, each with a specific responsibility:

```
utils/
├── __init__.py           # Package exports
├── pdf_parser.py         # PDF parsing and metadata extraction
├── s3_uploader.py        # S3 file upload functionality
├── text_chunker.py       # Intelligent text chunking
├── vector_store.py       # Vector store management
└── pipeline.py           # Orchestration of all components
```

## Modules

### 1. `pdf_parser.py` - PDF Parsing

**Class:** `LegalPDFParser`

Handles parsing of PDF documents and extraction of legal metadata.

```python
from utils.pdf_parser import LegalPDFParser

parser = LegalPDFParser()

# Parse a PDF and get text + metadata
full_text, metadata = parser.parse_pdf("path/to/case.pdf")

# metadata contains: citation, case_title, case_number
print(metadata["citation"])
print(metadata["case_title"])
```

**Features:**
- Loads PDF files using LangChain's PyPDFLoader
- Extracts case citation (e.g., `[2025] 1 S.C.R. 123 : 2025 INSC 456`)
- Extracts case title (e.g., `Party A v. Party B`)
- Extracts case number (e.g., `Civil Appeal No. 11716 of 2025`)

### 2. `s3_uploader.py` - S3 Upload

**Class:** `S3Uploader`

Manages uploading files to AWS S3.

```python
from utils.s3_uploader import S3Uploader

uploader = S3Uploader(bucket_name="my-bucket")

# Upload a file
s3_uri = uploader.upload_file("local/path/file.pdf", "s3/key/file.pdf")
print(s3_uri)  # s3://my-bucket/s3/key/file.pdf

# Check if file exists
exists = uploader.file_exists("s3/key/file.pdf")
```

**Features:**
- Upload files to S3
- Check if files exist in S3
- Returns S3 URI for uploaded files

### 3. `text_chunker.py` - Text Chunking

**Class:** `LegalTextChunker`

Intelligently chunks legal documents using header-based and semantic approaches.

```python
from utils.text_chunker import LegalTextChunker

chunker = LegalTextChunker(max_chunk_size=2000)

# Chunk text
chunks = chunker.chunk_text(full_text)

# Returns list of tuples: (section_header, content)
for header, content in chunks:
    print(f"Section: {header}")
    print(f"Content length: {len(content)}")
```

**Features:**
- Header-based chunking using legal section headers
- Semantic chunking for large sections
- Preserves document structure
- Configurable maximum chunk size

**Recognized Headers:**
- Issue for Consideration
- Headnotes, Held
- Facts, Analysis, Reasoning
- Judgment, Order
- And more...

### 4. `vector_store.py` - Vector Store

**Class:** `VectorStoreManager`

Manages embedding and storage of documents in FAISS.

```python
from utils.vector_store import VectorStoreManager
from langchain.docstore.document import Document

manager = VectorStoreManager(store_dir="data/vector_store")

# Create vector store
documents = [Document(page_content="...", metadata={...}), ...]
manager.create_vector_store(documents)

# Save to disk
manager.save()

# Load from disk
vector_store = manager.load()

# Get the vector store
vs = manager.get_vector_store()
```

**Features:**
- Create FAISS vector stores
- Add documents to existing stores
- Save and load from disk
- Uses AWS Bedrock embeddings (configurable)

### 5. `pipeline.py` - Complete Pipeline

**Class:** `DocumentProcessingPipeline`

Orchestrates the entire document processing workflow.

```python
from utils.pipeline import DocumentProcessingPipeline

pipeline = DocumentProcessingPipeline(
    pdf_dir="data/pdfs",
    vector_store_dir="data/vector_store",
    s3_bucket="my-bucket",  # optional
    max_chunk_size=2000,
    upload_to_s3=False  # set to True to upload to S3
)

# Run the complete pipeline
pipeline.run()

# Or process a single PDF
documents = pipeline.process_single_pdf("path/to/case.pdf", "case.pdf")

# Get the vector store
vector_store = pipeline.get_vector_store()
```

**Pipeline Steps:**
1. Parse PDF and extract metadata
2. Upload to S3 (optional)
3. Chunk the text intelligently
4. Create Document objects with metadata
5. Embed and store in FAISS vector store

## Usage

### Quick Start (Complete Pipeline)

```python
from utils import DocumentProcessingPipeline

# Initialize pipeline
pipeline = DocumentProcessingPipeline(
    pdf_dir="data/pdfs",
    vector_store_dir="data/vector_store",
    upload_to_s3=False
)

# Run complete processing
pipeline.run()
```

### Using Individual Components

```python
from utils import LegalPDFParser, LegalTextChunker, VectorStoreManager
from langchain.docstore.document import Document

# 1. Parse PDF
parser = LegalPDFParser()
full_text, metadata = parser.parse_pdf("case.pdf")

# 2. Chunk text
chunker = LegalTextChunker()
chunks = chunker.chunk_text(full_text)

# 3. Create documents
documents = []
for header, content in chunks:
    doc = Document(
        page_content=content,
        metadata={**metadata, "section": header}
    )
    documents.append(doc)

# 4. Store in vector database
vs_manager = VectorStoreManager(store_dir="vector_store")
vs_manager.create_vector_store(documents)
vs_manager.save()
```

## Running the Pipeline

Use the provided `process_documents.py` script:

```bash
python process_documents.py
```

This will:
1. Process all PDFs in `data/pdfs/`
2. Create chunks with metadata
3. Generate embeddings
4. Save vector store to `data/vector_store/`

## Configuration

Edit `process_documents.py` to configure:

```python
PDF_DIR = "data/pdfs"              # Directory with PDF files
VECTOR_STORE_DIR = "data/vector_store"  # Where to save vector store
S3_BUCKET = "my-bucket"            # S3 bucket name (if using)
UPLOAD_TO_S3 = False               # Set to True to upload to S3
```

## Dependencies

Required packages (see `requirements.txt`):
- langchain
- langchain-community
- langchain-experimental
- langchain-aws
- boto3
- faiss-cpu (or faiss-gpu)
- pypdf
- python-dotenv

## Environment Variables

Create a `.env` file with AWS credentials if using Bedrock embeddings:

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## Benefits of Refactored Structure

✅ **Modularity**: Each component has a single responsibility  
✅ **Reusability**: Components can be used independently  
✅ **Testability**: Easy to write unit tests for each module  
✅ **Maintainability**: Changes to one component don't affect others  
✅ **Extensibility**: Easy to add new parsers, chunkers, or storage backends  
✅ **Documentation**: Each module is well-documented with docstrings
