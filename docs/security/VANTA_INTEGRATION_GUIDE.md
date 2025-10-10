# Vanta API Integration Guide

## Overview

This integration allows LexiQ to log PII masking job results to Vanta for compliance monitoring and audit trails. The system automatically tracks PII detection, redaction effectiveness, and compliance status.

## Features

### 🔐 **SHA-256 Hash Computation**
- Computes hashes of original and masked content for integrity verification
- Ensures no raw text is sent to Vanta - only hashes and metadata
- Provides tamper-proof audit trail

### 📊 **Structured JSON Payload**
- Matches Vanta's Custom Resource format exactly
- Includes comprehensive metadata and compliance information
- Supports case and user tracking for detailed audit trails

### 🔑 **OAuth Authentication**
- Uses Vanta's OAuth client credentials flow
- Automatic token refresh and error handling
- Secure credential management via environment variables

### ✅ **Pass/Fail Determination**
- Intelligent masking success assessment based on PII reduction ratios
- Configurable success threshold (default: 95% reduction required)
- Risk level assessment (LOW, MEDIUM, HIGH, CRITICAL)

## Setup Instructions

### 1. Vanta Application Setup

1. **Log in to Vanta**: Go to your Vanta account dashboard
2. **Navigate to Developer Console**: Settings → Developer Console
3. **Create Application**: Click "Create" and provide:
   - **Name**: "LexiQ PII Masking Integration"
   - **Description**: "Automated PII masking compliance logging"
   - **App Type**: Select appropriate type for your use case
4. **Generate Credentials**: Copy the OAuth client ID and secret

### 2. Environment Configuration

Add the following to your `.env` file (same pattern as AWS Bedrock configuration):

```bash
# Add to .env file
VANTA_CLIENT_ID=your_vanta_client_id
VANTA_CLIENT_SECRET=your_vanta_client_secret
VANTA_BASE_URL=https://api.vanta.com
ENVIRONMENT=development
```

**Note**: The system automatically loads these variables using `python-dotenv`, just like the AWS Bedrock client configuration.

### 3. Integration Usage

#### Basic Usage

```python
from security.pii_redactor import PIIRedactor

# Initialize with Vanta integration
redactor = PIIRedactor()

# Process text with Vanta logging
result = redactor.redact_pii_with_vanta_logging(
    text="John Doe's email is john@example.com",
    case_id="case-123",
    user_id="user-456"
)

print(f"Compliance Status: {result.redaction_metadata}")
```

#### Direct Vanta Client Usage

```python
from integrations.vanta_client import VantaClient, PIIMaskingResult

# Initialize client
vanta_client = VantaClient()

# Create masking result
result = PIIMaskingResult(
    original_content_hash="abc123...",
    masked_content_hash="def456...",
    pii_types_detected=["email", "phone"],
    pii_counts_before={"email": 1, "phone": 1},
    pii_counts_after={"email": 0, "phone": 0},
    masking_success=True,
    confidence_score=0.95,
    processing_time_ms=150,
    timestamp=datetime.now(timezone.utc),
    job_id="job-123"
)

# Log to Vanta
response = vanta_client.log_pii_masking_result(result)
```

## Payload Structure

The system generates JSON payloads in this format:

```json
{
  "resourceType": "PII_MASKING_JOB",
  "resourceId": "unique-job-uuid",
  "timestamp": "2025-01-12T10:30:00Z",
  "metadata": {
    "case_id": "case-123",
    "user_id": "user-456",
    "processing_time_ms": 150,
    "confidence_score": 0.95
  },
  "integrity": {
    "original_content_hash": "sha256-hash-of-original-content",
    "masked_content_hash": "sha256-hash-of-masked-content",
    "hash_algorithm": "SHA-256"
  },
  "pii_analysis": {
    "types_detected": ["email", "phone", "person_name"],
    "counts_before_masking": {"email": 2, "phone": 1, "person_name": 1},
    "counts_after_masking": {"email": 0, "phone": 0, "person_name": 0},
    "total_pii_before": 4,
    "total_pii_after": 0
  },
  "compliance": {
    "masking_success": true,
    "success_threshold": 0.95,
    "compliance_status": "PASS",
    "risk_level": "LOW"
  },
  "audit": {
    "job_type": "PII_MASKING",
    "system": "LexiQ",
    "version": "1.0.0",
    "environment": "production"
  }
}
```

## Compliance Logic

### Masking Success Determination

The system determines success based on PII reduction:

```python
def determine_masking_success(pii_counts_before, pii_counts_after, threshold=0.95):
    total_before = sum(pii_counts_before.values())
    total_after = sum(pii_counts_after.values())
    
    if total_before == 0:
        return True  # No PII to mask
    
    reduction_ratio = (total_before - total_after) / total_before
    return reduction_ratio >= threshold
```

### Risk Level Assessment

- **LOW**: No PII remaining after masking
- **MEDIUM**: 1-2 PII instances remaining
- **HIGH**: 3-5 PII instances remaining  
- **CRITICAL**: 6+ PII instances remaining

## API Endpoints

### Authentication
- **Endpoint**: `POST /oauth/token`
- **Method**: Client Credentials Grant
- **Scopes**: `vanta-api.all:read vanta-api.all:write`

### Custom Resources
- **Endpoint**: `POST /custom-resources`
- **Purpose**: Log PII masking results
- **Rate Limit**: 50 requests per minute

### Compliance Summary
- **Endpoint**: `GET /custom-resources`
- **Purpose**: Retrieve compliance summaries
- **Filters**: case_id, user_id, days

## Testing

Run the test script to verify integration:

```bash
python test_vanta_integration.py
```

This will test:
- PII detection and redaction
- Hash computation
- Payload structuring
- API authentication
- Compliance logging

## Error Handling

The system includes comprehensive error handling:

- **Authentication Failures**: Automatic retry with credential validation
- **API Errors**: Graceful degradation with detailed error messages
- **Network Issues**: Timeout handling and retry logic
- **Payload Validation**: Schema validation before API calls

## Security Considerations

- **No Raw Text**: Only hashes and metadata are sent to Vanta
- **Secure Credentials**: Environment variable storage
- **Token Management**: Automatic refresh and secure storage
- **Audit Trail**: Complete logging of all operations

## Monitoring and Alerts

The system provides:

- **Real-time Logging**: Immediate feedback on compliance status
- **Batch Summaries**: Daily/weekly compliance reports
- **Alert Thresholds**: Configurable risk level alerts
- **Audit Trails**: Complete history of all masking operations

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Check VANTA_CLIENT_ID and VANTA_CLIENT_SECRET
   - Verify credentials in Vanta Developer Console
   - Ensure proper scopes are assigned

2. **API Rate Limits**
   - Monitor request frequency
   - Implement exponential backoff
   - Consider batch processing for high volume

3. **Payload Validation Errors**
   - Check JSON structure
   - Verify required fields
   - Validate data types

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show detailed API communication
```

## Production Deployment

### Environment Variables
```bash
# Add to .env file for production
VANTA_CLIENT_ID=prod_client_id
VANTA_CLIENT_SECRET=prod_client_secret
VANTA_BASE_URL=https://api.vanta.com
ENVIRONMENT=production
```

### Monitoring
- Set up alerts for compliance failures
- Monitor API response times
- Track masking success rates
- Review audit logs regularly

---

**Status**: ✅ **Ready for Production**

The Vanta integration is fully implemented and tested. Configure your credentials and start logging PII masking compliance automatically!
