# Vanta Environment Configuration Setup

## Quick Setup

The Vanta integration now uses the same `.env` file pattern as your AWS Bedrock client for consistent configuration management.

### 1. Add to .env File

Add these lines to your `.env` file:

```bash
# Vanta API Configuration
VANTA_CLIENT_ID=your_vanta_client_id
VANTA_CLIENT_SECRET=your_vanta_client_secret
VANTA_BASE_URL=https://api.vanta.com
ENVIRONMENT=development
```

### 2. Get Vanta Credentials

1. **Log in to Vanta**: Go to your Vanta account dashboard
2. **Navigate to Developer Console**: Settings → Developer Console  
3. **Create Application**: Click "Create" and provide:
   - **Name**: "LexiQ PII Masking Integration"
   - **Description**: "Automated PII masking compliance logging"
   - **App Type**: Select appropriate type for your use case
4. **Generate Credentials**: Copy the OAuth client ID and secret

### 3. Replace Placeholder Values

Replace the placeholder values in your `.env` file:

```bash
# Replace these with your actual credentials
VANTA_CLIENT_ID=abc123def456ghi789
VANTA_CLIENT_SECRET=xyz789uvw456rst123
VANTA_BASE_URL=https://api.vanta.com
ENVIRONMENT=development
```

### 4. Test Configuration

Run the test script to verify your configuration:

```bash
python test_vanta_integration.py
```

You should see:
- ✅ Vanta client initialized successfully
- ✅ Environment variables loaded correctly
- ✅ Authentication working (if credentials are valid)

## Complete .env Example

Here's how your complete `.env` file should look:

```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1

# Vanta API Configuration
VANTA_CLIENT_ID=your_vanta_client_id
VANTA_CLIENT_SECRET=your_vanta_client_secret
VANTA_BASE_URL=https://api.vanta.com

# Environment
ENVIRONMENT=development
```

## Benefits of .env Configuration

✅ **Consistent with AWS Bedrock**: Same pattern as your existing AWS configuration  
✅ **Automatic Loading**: Uses `python-dotenv` for seamless environment variable loading  
✅ **Security**: Credentials stored in `.env` file (not in code)  
✅ **Flexibility**: Easy to switch between development/production environments  
✅ **Version Control Safe**: `.env` files are typically gitignored  

## Production Deployment

For production, update your `.env` file:

```bash
# Production settings
VANTA_CLIENT_ID=prod_client_id
VANTA_CLIENT_SECRET=prod_client_secret
VANTA_BASE_URL=https://api.vanta.com
ENVIRONMENT=production
```

## Troubleshooting

### Environment Variables Not Loading
- Ensure `.env` file is in the project root directory
- Check that `python-dotenv` is installed: `pip install python-dotenv`
- Verify `.env` file format (no spaces around `=`)

### Authentication Errors
- Verify credentials are correct in Vanta Developer Console
- Check that credentials are properly set in `.env` file
- Ensure no extra spaces or quotes around credential values

### API Connection Issues
- Verify `VANTA_BASE_URL` is correct
- Check network connectivity to `https://api.vanta.com`
- Ensure Vanta application has proper permissions

---

**Status**: ✅ **Ready to Use**

Your Vanta integration is now configured to use the same `.env` pattern as your AWS Bedrock client for consistent and secure configuration management!
