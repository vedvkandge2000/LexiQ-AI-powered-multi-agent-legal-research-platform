# LexiQ - AI-Powered Legal Research Platform

A comprehensive multi-agent legal research platform that combines precedent analysis, news relevance, statute reference, and bench bias analysis with advanced security features and compliance monitoring.

## 🏗️ Project Structure

```
lexiq/
├── 📁 agents/                    # AI Agents for legal analysis
│   ├── news_relevance_agent.py   # News relevance analysis
│   ├── statute_reference_agent.py # Statute and legal reference analysis
│   ├── bench_bias_agent.py       # Judicial bias analysis
│   └── README.md                 # Agent architecture overview
│
├── 📁 auth/                      # Authentication & Authorization
│   ├── cognito_auth.py          # AWS Cognito integration
│   ├── jwt_manager.py           # JWT token management
│   ├── user_manager.py          # User data management
│   └── __init__.py
│
├── 📁 chat/                      # Conversational AI
│   ├── conversation_engine.py   # Core chat logic with RAG
│   ├── chat_manager.py          # Chat session management
│   ├── chat_storage.py          # DynamoDB chat history
│   └── __init__.py
│
├── 📁 docs/                      # Documentation
│   ├── 📁 agents/               # Agent documentation
│   ├── 📁 auth/                 # Authentication docs
│   ├── 📁 aws/                  # AWS setup guides
│   ├── 📁 chat/                 # Chat system docs
│   ├── 📁 integrations/         # Integration guides
│   ├── 📁 security/             # Security documentation
│   ├── 📁 testing/              # Testing documentation
│   └── [various MD files]       # Feature documentation
│
├── 📁 examples/                  # Example scripts and demos
│   ├── demo_*.py                # Feature demonstration scripts
│   ├── multi_agent_orchestrator.py # CLI orchestrator
│   ├── news_analyzer.py         # News agent CLI
│   ├── statute_analyzer.py      # Statute agent CLI
│   └── README.md                # Examples guide
│
├── 📁 integrations/              # External integrations
│   ├── vanta_client.py          # Raw Vanta API client
│   ├── vanta_mcp_client.py      # Vanta MCP client
│   └── __init__.py
│
├── 📁 security/                  # Security & Compliance
│   ├── pii_redactor.py          # PII detection and redaction
│   ├── input_validator.py       # Input validation and sanitization
│   ├── hallucination_detector.py # AI hallucination detection
│   ├── security_enforcer.py     # Central security enforcement
│   ├── view_audit_trail.py      # Audit trail viewer
│   ├── 📁 logs/                 # Security audit logs
│   └── README.md                # Security documentation
│
├── 📁 tests/                     # Test Suite
│   ├── test_*.py                # Comprehensive test files
│   ├── sample_test_cases.py     # Test case samples
│   └── README.md                # Testing guide
│
├── 📁 utils/                     # Utility modules
│   ├── case_similarity.py       # Case similarity analysis
│   ├── pdf_parser.py            # PDF parsing and metadata extraction
│   ├── vector_store.py          # FAISS vector store management
│   ├── retriever.py             # Document retrieval
│   ├── s3_pdf_reader.py         # S3 PDF content extraction
│   ├── check_database_content.py # Database content verification
│   ├── debug_pdf_format.py      # PDF format debugging
│   ├── get_detailed_content.py  # Content detail extraction
│   └── README.md                # Utilities guide
│
├── 📁 aws/                       # AWS Services
│   ├── bedrock_client.py        # AWS Bedrock integration
│   └── __pycache__/
│
├── 📁 data/                      # Data storage
│   ├── 📁 pdfs/                 # PDF documents
│   └── 📁 vector_store/         # FAISS vector store files
│
├── 📁 prompts/                   # AI prompts and templates
│
├── 📁 .cursor/                   # Cursor IDE configuration
│   └── cursor-mcp-config.json   # MCP server configuration
│
├── 📁 .env.d/                    # Environment configuration
│   └── vanta-credentials.env    # Vanta API credentials
│
├── app_ui.py                     # Main Streamlit application
├── case_analyzer.py              # Case analysis utilities
├── case_api.py                   # Case analysis API
├── example_api.py                # Example API usage
├── orchestrator.py               # Main orchestrator
├── process_documents.py          # Document processing pipeline
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
└── README.md                     # This file
```

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
# Clone repository
git clone <repository-url>
cd lexiq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configure AWS & Vanta**
```bash
# Copy environment template
cp .env.example .env

# Add your credentials to .env:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# VANTA_CLIENT_ID=your_vanta_id
# VANTA_CLIENT_SECRET=your_vanta_secret
```

### 3. **Process Documents**
```bash
# Process PDFs and build vector store
python process_documents.py
```

### 4. **Run Application**
```bash
# Start Streamlit UI
streamlit run app_ui.py
```

## 🤖 AI Agents

### **Precedent RAG Agent** (Core)
- Analyzes case similarity using FAISS vector store
- Provides comprehensive legal precedent analysis
- Integrates with S3 PDF storage for full judgment access

### **News Relevance Agent**
- Extracts key entities from case text
- Searches relevant news using GNews API
- Generates legal-context-aware news summaries

### **Statute Reference Agent**
- Uses NER + regex to extract legal sections/articles
- Scrapes full text from IndiaCode or cached data
- Generates plain-English legal explanations

### **Bench Bias Agent**
- Extracts judge names from precedent results
- Tracks judicial patterns across similar cases
- Provides bias analysis and judicial history

## 🔒 Security Features

### **PII Redaction**
- Detects and masks: Names, emails, phones, Aadhaar, PAN, bank accounts
- Uses hash-based placeholders to maintain context
- Integrates with Vanta for compliance logging

### **Input Validation**
- Prompt injection prevention
- XSS/SQL injection protection
- File upload validation
- Risk scoring and audit logging

### **Hallucination Detection**
- Validates legal references against vector store
- Checks statute authenticity
- Warns about potential AI hallucinations

### **Vanta Integration**
- Automatic compliance logging
- SHA-256 content integrity verification
- Real-time audit trail generation
- Risk assessment and reporting

## 💬 Conversational AI

### **Chain of Thought Chat**
- Multi-turn conversations about case analysis
- RAG integration for informed responses
- Context preservation across sessions
- Full PDF content access via S3

### **Authentication**
- AWS Cognito integration
- JWT token management
- Session management with DynamoDB
- Secure password hashing

## 🧪 Testing

### **Run Tests**
```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive test suite
python tests/test_comprehensive.py

# Run specific feature tests
python tests/test_security.py
python tests/test_vanta_mcp_integration.py

# View audit trail
python security/view_audit_trail.py
```

### **Test Coverage**
- ✅ Security features (PII, validation, hallucination)
- ✅ AI agents (news, statute, bench bias)
- ✅ Authentication and chat systems
- ✅ Vanta integration and compliance
- ✅ AWS services integration

## 📊 Monitoring & Compliance

### **Audit Trails**
- **Local**: `security/logs/` - JSON audit logs
- **Vanta**: https://app.vanta.com - Compliance dashboard
- **Real-time**: Console output during operations

### **View Audit Data**
```bash
# Comprehensive audit viewer
python security/view_audit_trail.py

# Monitor live logs
tail -f security/logs/pii_audit.log

# Check Vanta dashboard
# Visit: https://app.vanta.com
```

## 📚 Documentation

### **Feature Documentation**
- **Security**: `docs/security/` - PII, validation, hallucination detection
- **Authentication**: `docs/auth/` - AWS Cognito, JWT, sessions
- **Chat**: `docs/chat/` - Conversational AI, RAG integration
- **Agents**: `docs/agents/` - Multi-agent architecture
- **Integrations**: `docs/integrations/` - Vanta, AWS services
- **Testing**: `docs/testing/` - Test cases and validation

### **Setup Guides**
- **AWS**: `docs/aws/` - Bedrock, S3, Cognito setup
- **Security**: `docs/security/` - Vanta integration, compliance
- **Examples**: `examples/` - Demo scripts and usage

## 🔧 Configuration

### **Environment Variables**
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1

# Vanta Integration
VANTA_CLIENT_ID=your_client_id
VANTA_CLIENT_SECRET=your_client_secret
VANTA_BASE_URL=https://api.vanta.com

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### **Cursor MCP Configuration**
```json
{
  "mcpServers": {
    "Vanta": {
      "command": "npx",
      "args": ["-y", "@vantasdk/vanta-mcp-server"],
      "env": {
        "VANTA_ENV_FILE": "/path/to/vanta-credentials.env"
      }
    }
  }
}
```

## 🎯 Key Features

- ✅ **Multi-Agent Architecture** - Specialized AI agents for different legal analysis tasks
- ✅ **Advanced Security** - PII redaction, input validation, hallucination detection
- ✅ **Compliance Monitoring** - Vanta integration with real-time audit trails
- ✅ **Conversational AI** - Chain of thought chat with RAG integration
- ✅ **AWS Integration** - Bedrock, Cognito, DynamoDB, S3 services
- ✅ **Comprehensive Testing** - Full test suite with audit validation
- ✅ **Documentation** - Organized docs for all features and setup

## 📞 Support

For questions or issues:
1. Check the documentation in `docs/` directory
2. Review test cases in `tests/` directory
3. Run audit trail viewer: `python security/view_audit_trail.py`
4. Check Vanta dashboard for compliance status

---

**🎉 LexiQ - Your AI-Powered Legal Research Assistant**