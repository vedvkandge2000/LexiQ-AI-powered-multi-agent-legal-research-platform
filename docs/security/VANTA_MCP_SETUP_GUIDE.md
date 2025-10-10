# Vanta MCP Server Setup Guide

## 🚀 Much Better Approach!

Using Cursor's MCP (Model Context Protocol) server for Vanta integration is a much better approach than managing raw API endpoints. This provides:

- ✅ **Official Vanta SDK** with proper API handling
- ✅ **Built-in authentication** management
- ✅ **Structured data models** and validation
- ✅ **No endpoint guessing** required
- ✅ **Native Cursor integration**

## 📋 Setup Steps

### 1. **Update Your Vanta Credentials**

Edit the `vanta-credentials.env` file with your actual credentials:

```bash
# vanta-credentials.env
VANTA_CLIENT_ID=your_actual_vanta_client_id
VANTA_CLIENT_SECRET=your_actual_vanta_client_secret
VANTA_BASE_URL=https://api.vanta.com
VANTA_ENVIRONMENT=development
```

### 2. **Configure Cursor MCP Settings**

Add this to your Cursor MCP configuration:

```json
{
  "mcpServers": {
    "Vanta": {
      "command": "npx",
      "args": ["-y", "@vantasdk/vanta-mcp-server"],
      "env": {
        "VANTA_ENV_FILE": "/Users/vedantkandge/Documents/Hackathons/lexiq/vanta-credentials.env"
      }
    }
  }
}
```

**Location**: 
- **macOS**: `~/Library/Application Support/Cursor/User/globalStorage/storage.json`
- **Windows**: `%APPDATA%\Cursor\User\globalStorage\storage.json`
- **Linux**: `~/.config/Cursor/User/globalStorage/storage.json`

### 3. **Restart Cursor**

After adding the MCP configuration, restart Cursor to load the Vanta MCP server.

### 4. **Test MCP Integration**

Run the test script to verify everything is working:

```bash
python test_vanta_mcp_integration.py
```

## 🔧 Updated Integration

### New MCP Client

I've created a new `VantaMCPClient` that's designed to work with Cursor's MCP server:

```python
from integrations.vanta_mcp_client import VantaMCPClient

# Initialize MCP client
client = VantaMCPClient()

# Log PII masking result
result = client.log_pii_masking_result(masking_result)
```

### Updated PII Redactor

The PII redactor now supports both approaches:

```python
from security.pii_redactor import PIIRedactor

# Initialize with MCP integration
redactor = PIIRedactor()

# Use MCP-based logging
result = redactor.redact_pii_with_vanta_mcp_logging(
    text="John Doe's email is john@example.com",
    case_id="case-123",
    user_id="user-456"
)
```

## 🎯 Benefits of MCP Approach

### 1. **No API Endpoint Management**
- ✅ MCP server handles all API endpoints
- ✅ No need to guess or test endpoints
- ✅ Automatic endpoint discovery

### 2. **Proper Authentication**
- ✅ Built-in OAuth handling
- ✅ Automatic token refresh
- ✅ Secure credential management

### 3. **Structured Data Models**
- ✅ Validated data structures
- ✅ Type safety and validation
- ✅ Consistent API contracts

### 4. **Native Cursor Integration**
- ✅ Direct integration with Cursor
- ✅ Real-time data access
- ✅ Seamless development experience

## 📊 MCP vs Raw API Comparison

| Feature | Raw API | MCP Server |
|---------|---------|------------|
| Authentication | Manual OAuth | Built-in |
| Endpoints | Manual discovery | Automatic |
| Data Models | Custom | Structured |
| Error Handling | Manual | Built-in |
| Cursor Integration | None | Native |
| Maintenance | High | Low |

## 🚀 Next Steps

1. **Update credentials** in `vanta-credentials.env`
2. **Configure Cursor MCP** settings
3. **Restart Cursor**
4. **Test integration** with MCP client
5. **Use in production** with confidence!

## 🔍 Troubleshooting

### MCP Server Not Loading
- Check Cursor MCP configuration syntax
- Verify credentials file path
- Restart Cursor after configuration changes

### Authentication Issues
- Verify credentials in `vanta-credentials.env`
- Check Vanta Developer Console for correct credentials
- Ensure no extra spaces or quotes in credentials

### Integration Errors
- Check MCP server logs in Cursor
- Verify data payload structure
- Test with simple requests first

---

**Status**: ✅ **Ready for MCP Integration**

This approach eliminates the need to manage raw API endpoints and provides a much more robust integration with Vanta!
