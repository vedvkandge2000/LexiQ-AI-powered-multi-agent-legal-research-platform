# Authentication & Chat Setup Guide

## 🎯 Overview

LexiQ now includes **authentication** and **conversational chat** features using AWS services.

---

## 🏗️ Architecture

### AWS Services Used

| Service | Purpose | Status |
|---------|---------|--------|
| **AWS Cognito** | User authentication, registration, password management | ✅ Integrated (with mock fallback) |
| **AWS DynamoDB** | Chat history, sessions, user data storage | ✅ Integrated (with in-memory fallback) |
| **AWS Bedrock** | Claude for analysis & chat | ✅ Already in use |
| **AWS S3** | PDF storage | ✅ Already in use |

### Components Built

1. **`auth/cognito_auth.py`** - AWS Cognito integration
2. **`auth/jwt_manager.py`** - JWT token management for API
3. **`auth/user_manager.py`** - Simple user management (dev mode)
4. **`chat/chat_storage.py`** - DynamoDB storage for chat history
5. **`chat/conversation_engine.py`** - Chain-of-thought conversation with RAG
6. **`chat/chat_manager.py`** - High-level chat orchestration
7. **`app_with_auth.py`** - Complete Streamlit app with auth + chat

---

## 🚀 Quick Start (Development Mode)

The system works **out of the box** without AWS configuration using fallback modes:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app_with_auth.py
```

**Default Behavior:**
- ✅ Authentication: File-based user storage (`data/users.json`)
- ✅ Chat Storage: In-memory (no persistence between restarts)
- ✅ All features work immediately for development

---

## 🔧 Production Setup (AWS Services)

### Step 1: AWS Cognito Setup

1. **Create User Pool:**
   ```bash
   aws cognito-idp create-user-pool \
     --pool-name lexiq-users \
     --policies "PasswordPolicy={MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=true}" \
     --auto-verified-attributes email \
     --mfa-configuration OFF
   ```

2. **Create App Client:**
   ```bash
   aws cognito-idp create-user-pool-client \
     --user-pool-id <YOUR_POOL_ID> \
     --client-name lexiq-app \
     --explicit-auth-flows "ALLOW_USER_PASSWORD_AUTH" "ALLOW_REFRESH_TOKEN_AUTH" \
     --generate-secret
   ```

3. **Set Environment Variables:**
   ```bash
   export COGNITO_USER_POOL_ID="us-east-1_xxxxxxxx"
   export COGNITO_CLIENT_ID="xxxxxxxxxxxxxxxxxxxxxxxxxx"
   export COGNITO_CLIENT_SECRET="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
   ```

### Step 2: DynamoDB Setup

1. **Create Chat History Table:**
   ```bash
   aws dynamodb create-table \
     --table-name lexiq-chat-history \
     --attribute-definitions \
       AttributeName=session_id,AttributeType=S \
       AttributeName=message_id,AttributeType=S \
       AttributeName=user_id,AttributeType=S \
     --key-schema \
       AttributeName=session_id,KeyType=HASH \
     --global-secondary-indexes \
       '[
         {
           "IndexName": "user-sessions-index",
           "KeySchema": [{"AttributeName":"user_id","KeyType":"HASH"}],
           "Projection": {"ProjectionType":"ALL"},
           "ProvisionedThroughput": {"ReadCapacityUnits":5,"WriteCapacityUnits":5}
         }
       ]' \
     --billing-mode PAY_PER_REQUEST
   ```

2. **Set Environment Variable:**
   ```bash
   export DYNAMODB_CHAT_TABLE="lexiq-chat-history"
   ```

### Step 3: JWT Secret

```bash
# Generate secure secret
export JWT_SECRET_KEY=$(openssl rand -base64 32)
```

### Step 4: Run Production App

```bash
# With all AWS services configured
streamlit run app_with_auth.py
```

---

## 📖 Features

### 1. Authentication

#### Registration
- Username, email, password
- User roles (user, lawyer, student)
- Password hashing with bcrypt
- Email verification (if Cognito configured)

#### Login
- Username/password authentication
- Session management
- JWT tokens for API access

#### Security
- Password requirements (8+ chars, uppercase, lowercase, numbers)
- Secure password storage (bcrypt hashing)
- Session timeout
- Token refresh

### 2. Conversational Chat

#### Starting a Chat
1. **From Case Analysis**: After analyzing a case, click "Start Chat" to discuss it
2. **New Chat**: Create a blank chat and describe your case
3. **Continue Existing**: Resume previous conversations

#### Chat Features
- **Context-Aware**: Maintains full conversation history
- **RAG Integration**: Retrieves relevant precedents for each response
- **Suggested Questions**: AI generates follow-up questions
- **Citation Tracking**: Shows which precedents were used
- **Export**: Download chat as Markdown
- **Summarize**: Generate conversation summary
- **Multi-Session**: Multiple concurrent chat sessions per user

#### Chat Flow
```
User analyzes case
     ↓
Initial analysis generated (with precedents)
     ↓
Chat session created
     ↓
User asks questions
     ↓
System retrieves relevant precedents
     ↓
Claude generates response with context
     ↓
Citations shown + suggested follow-ups
     ↓
Conversation continues...
```

---

## 🎨 UI Overview

### Pages

1. **🏠 Home** - Overview of all features
2. **🔍 Case Analysis** - Find similar precedents
3. **💬 Chat** - Conversational case discussion
4. **📜 My Chats** - View all chat sessions
5. **📰 News** - (To be integrated)
6. **📚 Statutes** - (To be integrated)
7. **⚖️ Bench Bias** - (To be integrated)

### Sidebar
- User profile
- Logout button
- Navigation menu
- Recent chat sessions (in Chat page)

---

## 💡 Usage Examples

### Example 1: Complete Workflow

```
1. Register → Create account
2. Login → Enter credentials
3. Case Analysis → Describe your case
   ↓ System finds similar precedents
   ↓ Generates initial analysis
4. Start Chat → Discuss the analysis
5. Ask Questions → "What about jurisdiction?"
   ↓ System retrieves relevant precedents
   ↓ Generates informed response
6. Follow-ups → Continue the conversation
7. Export → Download chat transcript
```

### Example 2: Chat Interaction

```
User: "What are the chances of success in this case?"

System: [Retrieves 3 relevant precedents]
        [Analyzes based on similar cases]
        
Response: "Based on precedents like State vs. X [2020] 
          and similar cases, your chances are moderate. 
          Key factors: [Analysis]
          
          📚 Precedents Referenced:
          • State vs. X [2020] 5 S.C.R. 123
          • ABC Corp vs. State [2019]
          
          💡 Suggested questions:
          • What defenses are available?
          • How long might this take?
          • What evidence is most important?"
```

---

## 🔐 Security Integration

All features are protected by the existing security layer:

- ✅ **PII Redaction**: Automatically removes sensitive info from chat
- ✅ **Input Validation**: Prevents injection attacks
- ✅ **Hallucination Detection**: Validates legal references in responses
- ✅ **Audit Logging**: Tracks all authentication and chat activities

---

## 📁 File Structure

```
lexiq/
├── auth/
│   ├── __init__.py
│   ├── cognito_auth.py       # AWS Cognito integration
│   ├── jwt_manager.py         # JWT token management
│   └── user_manager.py        # Simple user management
│
├── chat/
│   ├── __init__.py
│   ├── chat_storage.py        # DynamoDB storage
│   ├── conversation_engine.py # Conversation logic
│   └── chat_manager.py        # High-level orchestration
│
├── data/
│   └── users.json            # User storage (dev mode)
│
├── app_with_auth.py          # Main app with auth + chat
└── AUTH_CHAT_SETUP.md        # This file
```

---

## 🧪 Testing

### Test Authentication

```python
from auth.user_manager import UserManager

user_mgr = UserManager()

# Register
result = user_mgr.register(
    username="test_user",
    password="TestPass123",
    email="test@example.com"
)

# Login
user = user_mgr.authenticate("test_user", "TestPass123")
print(user)  # {'username': 'test_user', 'email': '...', ...}
```

### Test Chat

```python
from chat.chat_manager import ChatManager

chat_mgr = ChatManager()

# Start chat
result = chat_mgr.start_new_chat(
    user_id="test_user",
    case_text="Case about breach of contract...",
    case_title="Contract Dispute"
)

session_id = result['session_id']

# Send message
response = chat_mgr.send_message(
    session_id=session_id,
    user_message="What are the key legal issues?"
)

print(response['response'])
```

---

## 🔧 Configuration

### Environment Variables

```bash
# AWS Cognito (optional)
COGNITO_USER_POOL_ID=us-east-1_xxxxxxxx
COGNITO_CLIENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxx
COGNITO_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# DynamoDB (optional)
DYNAMODB_CHAT_TABLE=lexiq-chat-history

# JWT (recommended for production)
JWT_SECRET_KEY=<secure-random-string>

# AWS Credentials (if not using default profile)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1
```

### Running Modes

**Development (Default):**
- File-based users
- In-memory chat storage
- No AWS services required

**Production:**
- AWS Cognito for auth
- DynamoDB for chat storage
- Full persistence and scalability

---

## 🚨 Troubleshooting

### "Mock mode" warning
- **Cause**: AWS credentials not configured
- **Solution**: Either set environment variables or continue in dev mode
- **Impact**: Features work but data isn't persisted

### Chat not saving
- **Cause**: DynamoDB not configured
- **Solution**: Set `DYNAMODB_CHAT_TABLE` or use in-memory mode
- **Impact**: Chats lost on restart (dev mode only)

### Login fails
- **Cause**: User not registered or wrong credentials
- **Solution**: Register a new account or check password

---

## 📝 Next Steps

1. **Run the App**: `streamlit run app_with_auth.py`
2. **Create Account**: Register a new user
3. **Test Analysis**: Analyze a case
4. **Start Chat**: Discuss the case with AI
5. **(Optional) Configure AWS**: Set up Cognito and DynamoDB for production

---

## 📞 API Integration

JWT tokens can be used for API authentication:

```python
from auth.jwt_manager import JWTManager
from flask import Flask, request, jsonify

app = Flask(__name__)
jwt_mgr = JWTManager()

@app.route('/api/chat', methods=['POST'])
@jwt_mgr.token_required
def api_chat(current_user):
    # current_user contains user info from JWT
    message = request.json['message']
    # ... process chat
    return jsonify({'response': '...'})
```

---

**Status:** ✅ **Complete & Ready to Use**

- Authentication: ✅ Working (mock + AWS)
- Chat System: ✅ Working (in-memory + DynamoDB)
- Security Integration: ✅ Active
- UI: ✅ Complete
- Documentation: ✅ Done

**Run:** `streamlit run app_with_auth.py`
