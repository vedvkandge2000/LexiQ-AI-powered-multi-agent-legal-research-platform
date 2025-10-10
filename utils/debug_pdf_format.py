#!/usr/bin/env python3
"""
Debug script to see the actual PDF content format
"""

from langchain_community.document_loaders import PyPDFLoader

# Load first PDF
pdf_path = "data/pdfs/1.pdf"
loader = PyPDFLoader(pdf_path)
pages = loader.load()

print("=" * 70)
print(f"First page content of {pdf_path}")
print("=" * 70)
print()
print(pages[0].page_content[:2000])
print()
print("=" * 70)
print("Second page (first 1000 chars):")
print("=" * 70)
if len(pages) > 1:
    print(pages[1].page_content[:1000])

