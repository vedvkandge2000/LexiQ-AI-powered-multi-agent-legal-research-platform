"""
S3 Uploader Module
Handles uploading files to AWS S3.
"""

import boto3
from typing import Optional


class S3Uploader:
    """Handles uploading files to AWS S3."""
    
    def __init__(self, bucket_name: str, region: Optional[str] = None):
        """
        Initialize S3 uploader.
        
        Args:
            bucket_name: Name of the S3 bucket
            region: AWS region (optional)
        """
        self.bucket_name = bucket_name
        if region:
            self.s3_client = boto3.client("s3", region_name=region)
        else:
            self.s3_client = boto3.client("s3")
    
    def upload_file(self, local_path: str, s3_key: str) -> str:
        """
        Upload a local file to S3.
        
        Args:
            local_path: Path to the local file
            s3_key: S3 key (path) for the uploaded file
            
        Returns:
            S3 URI of the uploaded file (s3://bucket/key)
        """
        self.s3_client.upload_file(local_path, self.bucket_name, s3_key)
        return f"s3://{self.bucket_name}/{s3_key}"
    
    def upload_pdf(self, local_path: str, s3_key: str) -> str:
        """
        Upload a PDF file to S3.
        
        Args:
            local_path: Path to the local PDF file
            s3_key: S3 key (path) for the uploaded file
            
        Returns:
            S3 URI of the uploaded file
        """
        return self.upload_file(local_path, s3_key)
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Check if a file exists in S3.
        
        Args:
            s3_key: S3 key to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except:
            return False
