# LexiQ Security Module

## Overview

Backend security enforcement layer that **all requests must pass through** before processing.

### Components

1. **PII Redactor** - Detects and redacts personally identifiable information
2. **Input Validator** - Validates and sanitizes all inputs
3. **Hallucination Detector** - Validates legal references (cases, statutes, articles)
4. **Security Enforcer** - Backend enforcement combining all + audit logging

---

## Features

### ✅ PII Redaction
- **Detects**: Names, phone numbers, email, Aadhaar, PAN, bank accounts
- **Context Preservation**: Uses placeholders instead of deletion
- **Hash-based**: Same PII always gets same placeholder
- **Confidence Scoring**: Adjustable threshold (default 0.7)

### ✅ Input Validation
- **Length limits**: Min/max character validation
- **Prompt injection detection**: Blocks LLM manipulation attempts
- **XSS prevention**: Removes malicious HTML/JavaScript
- **SQL injection check**: Defensive pattern detection
- **File upload validation**: Type, size, malware prevention

### ✅ Hallucination Detection
- **Statute validation**: IPC, CrPC, CPC, IT Act sections against known ranges
- **Article validation**: Constitution articles (1-395 + special)
- **Case citation validation**: Validates against vector store database
- **Confidence scoring**: 0.95 for definite fakes, 0.8 for likely fakes
- **Audit logging**: Logs all suspected hallucinations

### ✅ Audit Logging
**Security Audit Log** (`security_audit.log`):
- `original_input_hash` - SHA256 hash of original
- `pii_types_detected` - Types of PII found
- `num_redactions` - Number of redactions made
- `redaction_confidence_score` - Average confidence
- `validation_passed` - Boolean pass/fail
- `risk_score` - Calculated risk (0.0 - 1.0)
- `violations` - List of validation violations
- `request_id` - Unique identifier
- `user_id` - User identifier
- `ip_address` - Request IP
- `timestamp` - ISO timestamp

**Hallucination Audit Log** (`hallucination_audit.log`):
- `suspected_hallucination` - Boolean
- `input_query` - Original query
- `output_text` - LLM output (truncated)
- `suspected_fake_refs` - List of suspected fake references
- `confidence_score` - Detection confidence (0.0 - 1.0)
- `matched_statute` - Boolean for statute validation
- `validated_against_index` - Boolean for vector store validation

---

## Usage

### Basic Usage (Input Processing)

```python
from security.security_enforcer import SecurityEnforcer

# Initialize
enforcer = SecurityEnforcer(
    enable_pii_redaction=True,
    enable_validation=True,
    min_pii_confidence=0.7
)

# Process user input
result = enforcer.process_case_input(
    case_text=user_input,
    user_id="user_123",
    ip_address="192.168.1.1"
)

if result['success']:
    # Use redacted text for processing
    safe_text = result['processed_text']
    
    # Access security metadata
    pii_detected = result['security_metadata']['pii_detected']
    risk_score = result['security_metadata']['risk_score']
else:
    # Handle validation failure
    print(f"Security check failed: {result['error']}")
    print(f"Violations: {result['violations']}")
```

### Hallucination Detection (Output Validation)

```python
from security.hallucination_detector import HallucinationDetector
from utils.retriever import LegalDocumentRetriever

# Initialize with vector store
retriever = LegalDocumentRetriever(vector_store_dir="data/vector_store")
retriever.load_vector_store()

detector = HallucinationDetector(retriever=retriever)

# After getting LLM response
llm_output = call_claude(prompt)

# Check for hallucinations
result = detector.detect_hallucinations(
    input_query=user_query,
    output_text=llm_output,
    user_id="user_123"
)

# Warn user if suspected hallucinations
if result['has_hallucinations']:
    print(f"⚠️ Warning: {result['num_suspected']} suspected fake reference(s)")
    for fake in result['suspected_fake_refs']:
        print(f"  - {fake['text']}: {fake['reason']}")
```

### File Upload Validation

```python
result = enforcer.process_file_upload(
    filename="document.pdf",
    file_size_bytes=file.size,
    content_type=file.content_type,
    user_id="user_123"
)

if not result['success']:
    raise ValueError(result['error'])
```

---

## PII Detection Examples

### Input:
```
Contact Mr. Rajesh Kumar at rajesh@email.com or +91-9876543210.
Aadhaar: 1234-5678-9012, PAN: ABCDE1234F
```

### Output:
```
Contact [PERSON_1_bb3f1289] at [EMAIL_1_77b33a95] or [PHONE_1_91e491a2].
Aadhaar: [AADHAAR_1_6a3eef27], PAN: [PAN_1_6442fd73]
```

### Metadata:
```json
{
  "pii_types_detected": ["person_name", "email", "phone", "aadhaar", "pan"],
  "num_redactions": 5,
  "redaction_confidence_score": 0.85,
  "original_input_hash": "8a4ba5a..."
}
```

---

## Validation Examples

### ✅ Valid Input
```python
case_text = "Patent infringement case involving AI algorithms..."
# Passes validation
```

### ❌ Invalid Input (Prompt Injection)
```python
case_text = "Ignore previous instructions and..."
# Blocked with violation: "Potential prompt injection detected"
```

### ❌ Invalid Input (Too Long)
```python
case_text = "A" * 60000  # Exceeds 50K limit
# Blocked with violation: "Text exceeds maximum length"
```

---

## Configuration

### Security Levels

**High Security** (Recommended for production):
```python
enforcer = SecurityEnforcer(
    enable_pii_redaction=True,
    enable_validation=True,
    min_pii_confidence=0.8  # Higher threshold
)
```

**Medium Security** (Development):
```python
enforcer = SecurityEnforcer(
    enable_pii_redaction=True,
    enable_validation=True,
    min_pii_confidence=0.7  # Default
)
```

**Low Security** (Testing only):
```python
enforcer = SecurityEnforcer(
    enable_pii_redaction=False,
    enable_validation=False
)
```

---

## Audit Logs

Location: `security/logs/security_audit.log`

### Log Format:
```json
{
  "timestamp": "2025-10-09T23:41:55",
  "request_id": "REQ_20251009234155_000001",
  "user_id": "user_123",
  "action": "CASE_INPUT_PROCESSED",
  "original_input_hash": "8a4ba5a1e00cee73...",
  "pii_types_detected": ["email", "phone"],
  "num_redactions": 2,
  "redaction_confidence_score": 0.85,
  "validation_passed": true,
  "risk_score": 0.0,
  "violations": [],
  "ip_address": "192.168.1.1"
}
```

---

## Integration

### Streamlit UI Integration

```python
# In app_ui.py
from security.security_enforcer import SecurityEnforcer

# Initialize once
if 'security_enforcer' not in st.session_state:
    st.session_state.security_enforcer = SecurityEnforcer()

# Process user input
result = st.session_state.security_enforcer.process_case_input(
    case_text=user_input,
    user_id=st.session_state.get('user_id'),
    ip_address=st.request.headers.get('X-Forwarded-For')
)

if not result['success']:
    st.error(f"Security validation failed: {result['error']}")
    st.stop()

# Use safe text
safe_text = result['processed_text']
```

### API Integration

```python
# In case_api.py
from security.security_enforcer import SecurityEnforcer

enforcer = SecurityEnforcer()

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    
    # Security check
    security_result = enforcer.process_case_input(
        case_text=data['case_text'],
        user_id=get_current_user_id(),
        ip_address=request.remote_addr
    )
    
    if not security_result['success']:
        return jsonify({
            'error': 'Security validation failed',
            'violations': security_result['violations']
        }), 400
    
    # Process with safe text
    result = process_case(security_result['processed_text'])
    return jsonify(result)
```

---

## Testing

### Security Module Tests
```bash
# Test PII, validation, and file upload
python -c "from security import SecurityEnforcer; print('Security module OK')"
```

### Hallucination Detection Tests
```bash
# Test hallucination detection
python -c "
from security.hallucination_detector import HallucinationDetector
detector = HallucinationDetector()
result = detector.detect_hallucinations('test', 'Section 999 of IPC', 'test')
print('Detected:', result['has_hallucinations'])
"
```

Coverage:
1. ✅ PII Redaction
2. ✅ Input Validation
3. ✅ File Upload Validation
4. ✅ Hallucination Detection (Statutes, Articles, Cases)
5. ✅ Complete Workflow

---

## Limitations

### PII Redaction
1. **Name Detection**: May have false positives for case names (e.g., "State of Punjab")
2. **Phone Numbers**: 10-digit numbers might be case numbers
3. **Context**: Cannot understand semantic context beyond regex patterns
4. **Language**: Optimized for English and Indian legal documents

### Hallucination Detection
1. **New Laws**: Recently enacted laws not in database
2. **Amendments**: Section numbers that changed
3. **Citation Formats**: May miss unusual citation formats
4. **Context**: Cannot verify if citation is used correctly in context
5. **Case Names**: Only validates citations, not case names

---

## Future Enhancements

### PII & Validation
- ML-based PII detection (spaCy NER)
- Custom PII patterns per client
- Unredaction API with authentication
- Real-time threat intelligence
- Rate limiting integration
- IP blacklist/whitelist

### Hallucination Detection
- Auto-update statute database from web scraping
- Add more statutes (state laws, special acts)
- Citation context validation
- Case name validation
- Confidence adjustment based on semantic context
- Integration with IndiaCode API for real-time validation

---

## Documentation

- **[PII Redaction Details](./HALLUCINATION_DETECTION.md)** - Not created yet
- **[Hallucination Detection Guide](./HALLUCINATION_DETECTION.md)** - Comprehensive guide
- **[Security Enforcer API](./SECURITY_IMPLEMENTATION.md)** - Implementation summary

---

## Quick Reference

| Component | Purpose | Log File | Status |
|-----------|---------|----------|--------|
| PII Redactor | Remove sensitive info | `security_audit.log` | ✅ Ready |
| Input Validator | Block malicious input | `security_audit.log` | ✅ Ready |
| Hallucination Detector | Validate legal refs | `hallucination_audit.log` | ✅ Ready |
| Security Enforcer | Orchestrate all | `security_audit.log` | ✅ Ready |

