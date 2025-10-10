#!/usr/bin/env python3
"""
S3 PDF Reader
Handles reading PDF content from S3 for chat context
"""

import boto3
import fitz  # PyMuPDF
import io
from typing import Optional, Dict, Any
from urllib.parse import urlparse


class S3PDFReader:
    """Handles reading PDF content from S3 buckets."""
    
    def __init__(self, region: str = None):
        """Initialize S3 PDF reader."""
        self.s3_client = boto3.client('s3', region_name=region)
        self.region = region
    
    def parse_s3_url(self, s3_url: str) -> Dict[str, str]:
        """
        Parse S3 URL to extract bucket and key.
        
        Args:
            s3_url: S3 URL (s3://bucket/key or https://bucket.s3.amazonaws.com/key)
            
        Returns:
            Dictionary with bucket and key
        """
        if s3_url.startswith('s3://'):
            # s3://bucket/key format
            parsed = urlparse(s3_url)
            return {
                'bucket': parsed.netloc,
                'key': parsed.path.lstrip('/')
            }
        elif 's3.amazonaws.com' in s3_url:
            # HTTPS URL format: https://bucket.s3.amazonaws.com/key
            parsed = urlparse(s3_url)
            bucket = parsed.netloc.split('.')[0]  # Extract bucket from hostname
            return {
                'bucket': bucket,
                'key': parsed.path.lstrip('/')
            }
        else:
            raise ValueError(f"Invalid S3 URL format: {s3_url}")
    
    def convert_to_direct_url(self, s3_url: str) -> str:
        """
        Convert S3 URL to direct HTTPS URL.
        
        Args:
            s3_url: S3 URL (s3://bucket/key)
            
        Returns:
            Direct HTTPS URL
        """
        try:
            parsed = self.parse_s3_url(s3_url)
            return f"https://{parsed['bucket']}.s3.amazonaws.com/{parsed['key']}"
        except Exception as e:
            print(f"Error converting S3 URL: {e}")
            return s3_url
    
    def generate_presigned_url(self, s3_url: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for S3 object.
        
        Args:
            s3_url: S3 URL
            expiration: Expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            parsed = self.parse_s3_url(s3_url)
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': parsed['bucket'],
                    'Key': parsed['key']
                },
                ExpiresIn=expiration
            )
            
            return presigned_url
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
    
    def download_pdf(self, s3_url: str) -> Optional[bytes]:
        """
        Download PDF from S3.
        
        Args:
            s3_url: S3 URL of the PDF
            
        Returns:
            PDF content as bytes or None if failed
        """
        try:
            parsed = self.parse_s3_url(s3_url)
            
            response = self.s3_client.get_object(
                Bucket=parsed['bucket'],
                Key=parsed['key']
            )
            
            return response['Body'].read()
            
        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return None
    
    def extract_page_content(self, s3_url: str, page_number: int) -> Optional[str]:
        """
        Extract content from specific page of PDF in S3.
        
        Args:
            s3_url: S3 URL of the PDF
            page_number: Page number (1-based)
            
        Returns:
            Page content as text or None if failed
        """
        try:
            # Download PDF
            pdf_content = self.download_pdf(s3_url)
            if not pdf_content:
                return None
            
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Convert to 0-based index
            page_index = page_number - 1
            
            if 0 <= page_index < len(doc):
                page = doc[page_index]
                text = page.get_text()
                doc.close()
                return text
            else:
                doc.close()
                print(f"Page {page_number} not found in PDF (total pages: {len(doc)})")
                return None
                
        except Exception as e:
            print(f"Error extracting page content: {e}")
            return None
    
    def extract_full_pdf_content(self, s3_url: str, max_pages: int = None) -> Optional[str]:
        """
        Extract content from full PDF in S3.
        
        Args:
            s3_url: S3 URL of the PDF
            max_pages: Maximum pages to extract (None for all)
            
        Returns:
            Full PDF content as text or None if failed
        """
        try:
            # Download PDF
            pdf_content = self.download_pdf(s3_url)
            if not pdf_content:
                return None
            
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            # Extract text from all pages
            full_text = []
            pages_to_extract = len(doc)
            if max_pages:
                pages_to_extract = min(pages_to_extract, max_pages)
            
            for page_num in range(pages_to_extract):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    full_text.append(f"--- Page {page_num + 1} ---\n{page_text}")
            
            doc.close()
            return "\n\n".join(full_text)
            
        except Exception as e:
            print(f"Error extracting full PDF content: {e}")
            return None
    
    def get_pdf_metadata(self, s3_url: str) -> Optional[Dict[str, Any]]:
        """
        Get PDF metadata.
        
        Args:
            s3_url: S3 URL of the PDF
            
        Returns:
            Dictionary with PDF metadata or None if failed
        """
        try:
            # Download PDF
            pdf_content = self.download_pdf(s3_url)
            if not pdf_content:
                return None
            
            # Open PDF with PyMuPDF
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            
            metadata = {
                'total_pages': len(doc),
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'subject': doc.metadata.get('subject', ''),
                'creator': doc.metadata.get('creator', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', '')
            }
            
            doc.close()
            return metadata
            
        except Exception as e:
            print(f"Error getting PDF metadata: {e}")
            return None


def create_s3_pdf_reader(region: str = None) -> S3PDFReader:
    """Create S3 PDF reader instance."""
    return S3PDFReader(region=region)
