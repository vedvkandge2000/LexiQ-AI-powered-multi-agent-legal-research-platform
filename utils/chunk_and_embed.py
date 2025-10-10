import os
import re
import boto3
import uuid
from typing import List, Tuple
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

# --- Config ---
PDF_DIR = "data/pdfs"
S3_BUCKET = "lexiq-supreme-court-pdfs"
VECTOR_STORE_DIR = "data/vector_store"

# --- AWS Clients ---
s3 = boto3.client("s3")

# --- Embeddings ---
embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0")  # Replace with OpenAI if needed

# --- Semantic Text Splitter (fallback for large sections) ---
semantic_splitter = SemanticChunker(
    embeddings=embeddings,
    breakpoint_threshold_type="percentile"
)

# --- Header-Based Chunking for Legal Documents ---
# Common section headers in Supreme Court judgments
LEGAL_SECTION_HEADERS = [
    r'Issue for Consideration',
    r'Headnotes†?',
    r'Held:?',
    r'List of Acts',
    r'List of Keywords',
    r'Case Arising From',
    r'Case Law Cited',
    r'Appearances for Parties',
    r'Judgment\s*/\s*Order of the Supreme Court',
    r'^Judgment$',
    r'^Order$',
    r'^ORDER$',
    r'Conclusion',
    r'Facts',
    r'Analysis',
    r'Reasoning',
    r'Background',
    r'Submissions?',
    r'Discussion',
    r'Ratio Decidendi',
    r'Obiter Dicta',
]

def header_based_chunk(text: str, max_chunk_size: int = 2000) -> List[Tuple[str, str]]:
    """
    Split text by legal section headers, preserving document structure.
    Returns list of tuples: (section_header, content)
    If a section is too large, it will be further split semantically.
    """
    chunks = []
    lines = text.split('\n')
    current_header = "Case Introduction"
    current_content = []
    
    for line in lines:
        line_stripped = line.strip()
        
        # Check if line is a section header
        is_header = False
        matched_header = None
        
        for header_pattern in LEGAL_SECTION_HEADERS:
            # Match at the beginning of the line
            if re.match(f'^{header_pattern}', line_stripped, re.IGNORECASE):
                is_header = True
                matched_header = line_stripped
                break
        
        if is_header and matched_header:
            # Save previous section
            if current_content:
                content_text = '\n'.join(current_content).strip()
                if content_text:  # Only add if there's actual content
                    chunks.append((current_header, content_text))
            
            # Start new section
            current_header = matched_header
            current_content = []
        else:
            # Add line to current section
            current_content.append(line)
    
    # Add the last section
    if current_content:
        content_text = '\n'.join(current_content).strip()
        if content_text:
            chunks.append((current_header, content_text))
    
    # If no meaningful headers were found, fall back to semantic chunking
    if not chunks or (len(chunks) == 1 and len(text) > max_chunk_size):
        semantic_chunks = semantic_splitter.split_text(text)
        return [("Section", chunk) for chunk in semantic_chunks]
    
    # Further split large sections using semantic chunking
    final_chunks = []
    for header, content in chunks:
        if len(content) > max_chunk_size:
            # Split large sections semantically while preserving header
            sub_chunks = semantic_splitter.split_text(content)
            for idx, sub_chunk in enumerate(sub_chunks):
                sub_header = f"{header} (Part {idx + 1})" if len(sub_chunks) > 1 else header
                final_chunks.append((sub_header, sub_chunk))
        else:
            final_chunks.append((header, content))
    
    return final_chunks

# --- Utils ---
def upload_to_s3(local_path, s3_key):
    s3.upload_file(local_path, S3_BUCKET, s3_key)
    return f"s3://{S3_BUCKET}/{s3_key}"

def extract_citation(text: str) -> str:
    combined = " ".join(text.splitlines())
    # Match the full citation: [YEAR] NUMBER S.C.R. NUMBER : YEAR INSC NUMBER
    match = re.search(r'\[(\d{4})\]\s*(\d+)\s*S\.C\.R\.\s*(\d+)\s*:\s*(\d{4})\s*INSC\s*(\d+)', combined, re.IGNORECASE)
    if match:
        return f"[{match.group(1)}] {match.group(2)} S.C.R. {match.group(3)} : {match.group(4)} INSC {match.group(5)}"
    # Fallback: try to match just the S.C.R. part
    match = re.search(r'\[\d{4}\]\s*\d+\s*S\.C\.R\.\s*\d+', combined, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    # Fallback: try to match just the INSC part
    match = re.search(r'\d{4}\s*INSC\s*\d+', combined, re.IGNORECASE)
    if match:
        return match.group(0).strip()
    return "Unknown Citation"

def extract_case_title(text: str) -> str:
    """
    Capture multi-line case names:
    Example: Railway Protection Force & Ors. v. Prem Chand Kumar & Ors.
    """
    combined = " ".join(text.splitlines())
    # Match case title - it appears after citation and before case number (in parentheses)
    # Look for pattern: word(s) v. word(s) followed by opening parenthesis
    match = re.search(r'INSC\s+\d+\s+(.+?)\s+v\.?\s+(.+?)(?=\s*\()', combined, re.IGNORECASE)
    if match:
        return f"{match.group(1).strip()} v. {match.group(2).strip()}"
    return "Unknown Title"

def extract_case_number(text: str) -> str:
    """
    Capture case number
    Example: (Civil Appeal No. 11716 of 2025)
    Example: (Criminal Appeal No(s). 3955-3956 of 2025)
    """
    combined = " ".join(text.splitlines())  # flatten newlines
    # Look for parentheses containing 'No.' or 'No(s).' - capture content inside parentheses
    # The pattern handles: No, No., No(s), No(s).
    match = re.search(r'\(([^)]*No\.?(?:\(s\))?\.?\s+\d+[^)]*)\)', combined, re.IGNORECASE)
    return match.group(1).strip() if match else "Unknown Case Number"

# --- Main Chunking & Embedding ---
all_docs = []
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

for file in os.listdir(PDF_DIR):
    if not file.endswith(".pdf"):
        continue

    pdf_path = os.path.join(PDF_DIR, file)
    print(f"Processing {file}...")

    loader = PyPDFLoader(pdf_path)
    pages = loader.load()

    # Extract from first page only
    first_page_text = pages[0].page_content
    citation = extract_citation(first_page_text)
    case_title = extract_case_title(first_page_text)
    case_number = extract_case_number(first_page_text)

    # Upload to S3
    s3_key = f"cases/{uuid.uuid4()}.pdf"
    # pdf_url = upload_to_s3(pdf_path, s3_key)

    # Combine all pages into one text for header-based chunking
    full_text = "\n\n".join([page.page_content for page in pages])
    
    # Chunk using header-based approach
    header_chunks = header_based_chunk(full_text, max_chunk_size=2000)
    
    for section_header, chunk_content in header_chunks:
        doc = Document(
            page_content=chunk_content,
            metadata={
                "case_title": case_title,
                "citation": citation,
                "case_number": case_number,
                "section": section_header,  # Add section header as metadata
                # "pdf_url": pdf_url,
            }
        )
        all_docs.append(doc)
    
    print(f"  ✓ Created {len(header_chunks)} chunks for {file}")

print(f"Total Chunks: {len(all_docs)}")

# Embed & Store in FAISS
faiss_index = FAISS.from_documents(all_docs, embeddings)
faiss_index.save_local(VECTOR_STORE_DIR)
print("✅ Vector store created and saved locally.")