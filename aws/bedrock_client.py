# aws/bedrock_client.py

import boto3
import json
import os
from dotenv import load_dotenv

# Load AWS credentials from .env if present
load_dotenv()


class BedrockClient:
    """Wrapper for AWS Bedrock Claude API."""
    
    def __init__(self, region: str = None):
        """Initialize Bedrock client."""
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.bedrock = boto3.client("bedrock-runtime", region_name=self.region)
    
    def invoke_model(self, prompt: str, max_tokens: int = 800, temperature: float = 0.3, timeout: int = 120) -> str:
        """Call Claude via Bedrock with timeout configuration."""
        return call_claude(prompt, max_tokens, temperature, timeout)


# Initialize Bedrock client with timeout configuration
bedrock = boto3.client(
    "bedrock-runtime", 
    region_name=os.getenv("AWS_REGION", "us-east-1"),
    config=boto3.session.Config(
        read_timeout=120,  # 2 minutes
        connect_timeout=60  # 1 minute
    )
)

def call_claude(prompt: str, max_tokens: int = 800, temperature: float = 0.3, timeout: int = 120) -> str:
    """
    Calls Claude 3 Sonnet via Amazon Bedrock.
    
    Parameters:
        prompt (str): Prompt to send to Claude
        max_tokens (int): Max tokens to generate
        temperature (float): Sampling temperature

    Returns:
        str: Claude's response text
    """

    # Format Claude-style message prompt
    claude_input = {
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "anthropic_version":"bedrock-2023-05-31"
    }

    # Claude 3 Sonnet via Bedrock
    # Option 1: Claude 3 Sonnet (stable, recommended)
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    
    # Option 2: Claude Sonnet 4 (if you have access to inference profiles)
    # model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"  # US East region inference profile
    # model_id = "anthropic.claude-sonnet-4-5-20250929-v1:0"     # Alternative inference profile
    try:
        # Add timeout configuration
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(claude_input),
        )

        result = response["body"].read().decode("utf-8")
        result_json = json.loads(result)

        return result_json["content"][0]["text"]

    except Exception as e:
        print(f"[ERROR] Claude call failed: {e}")
        return "⚠️ Error contacting Claude via Bedrock."