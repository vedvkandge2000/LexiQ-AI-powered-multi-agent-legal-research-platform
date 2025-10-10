#!/usr/bin/env python3
"""
Main script to process legal documents.
Refactored version of chunk_and_embed.py using modular components.
"""

from utils.pipeline import DocumentProcessingPipeline

# Configuration
PDF_DIR = "data/pdfs"
VECTOR_STORE_DIR = "data/vector_store"
S3_BUCKET = "lexiq-supreme-court-pdfs"

# Whether to upload PDFs to S3 (set to False to skip S3 upload)
UPLOAD_TO_S3 = True


def main():
    """Run the document processing pipeline."""
    
    # Initialize and run pipeline
    pipeline = DocumentProcessingPipeline(
        pdf_dir=PDF_DIR,
        vector_store_dir=VECTOR_STORE_DIR,
        s3_bucket=S3_BUCKET,
        max_chunk_size=2000,
        upload_to_s3=UPLOAD_TO_S3
    )
    
    # Run the complete pipeline
    pipeline.run()


if __name__ == "__main__":
    main()
