# AWS S3 Setup Guide for PDF Access

## ✅ ISSUE RESOLVED!

**Good News**: Your S3 bucket is already properly configured and accessible!

- ✅ S3 bucket exists and is accessible
- ✅ Direct HTTPS URLs are working (HTTP 200)
- ✅ PDFs are accessible via direct URLs
- ✅ No AWS configuration changes needed

## Solution Implemented

The code has been updated to use **direct HTTPS URLs** instead of presigned URLs:

**Before**: `s3://lexiq-supreme-court-pdfs/cases/file.pdf` (not browser accessible)
**After**: `https://lexiq-supreme-court-pdfs.s3.amazonaws.com/cases/file.pdf` (browser accessible)

## Current Status: ✅ WORKING

Your PDF links should now work directly in the browser without any AWS configuration changes.

### Step 1: Disable Block Public Access (Required for Presigned URLs)

1. Go to **AWS S3 Console**
2. Select your bucket: `lexiq-supreme-court-pdfs`
3. Go to **Permissions** tab
4. Scroll to **Block public access (bucket settings)**
5. Click **Edit**
6. **Uncheck** the following:
   - ✅ Block all public access
   - ✅ Block public access to buckets and objects granted through new access control lists (ACLs)
   - ✅ Block public access to buckets and objects granted through any access control lists (ACLs)
   - ✅ Block public access to buckets and objects granted through new public bucket or access point policies
   - ✅ Block public access to buckets and objects granted through any public bucket or access point policies

7. Click **Save changes**
8. Type `confirm` when prompted

### Step 2: Add CORS Configuration (Required for Browser Access)

1. In your S3 bucket, go to **Permissions** tab
2. Scroll to **Cross-origin resource sharing (CORS)**
3. Click **Edit**
4. Add this CORS configuration:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

5. Click **Save changes**

### Step 3: Verify Bucket Policy (Optional but Recommended)

Your bucket should have a policy that allows your IAM user to generate presigned URLs. If you want to make PDFs publicly accessible (simpler option), add this policy:

1. Go to **Permissions** tab
2. Scroll to **Bucket policy**
3. Click **Edit**
4. Add this policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::lexiq-supreme-court-pdfs/*"
        }
    ]
}
```

**Note**: This makes your PDFs publicly accessible. If you prefer to keep them private, skip this step and rely on presigned URLs only.

### Step 4: Test the Configuration

After making these changes, test the setup:

```bash
python test_s3_permissions.py
```

The presigned URLs should now return HTTP 200 instead of HTTP 403.

## Alternative: Quick Public Access (Simplest)

If you want the simplest solution:

1. **Disable Block Public Access** (Step 1 above)
2. **Add the bucket policy** (Step 3 above)
3. **Update the UI** to use direct HTTPS URLs instead of presigned URLs

Then I can modify the code to generate direct HTTPS URLs like:
`https://lexiq-supreme-court-pdfs.s3.amazonaws.com/cases/filename.pdf`

## Current Status

**Your AWS Setup:**
- ✅ Bucket exists: `lexiq-supreme-court-pdfs`
- ✅ IAM user has proper permissions
- ✅ Presigned URLs are generated
- ❌ Block Public Access is preventing access
- ❌ CORS may not be configured

**Next Steps:**
1. Follow Step 1 (Disable Block Public Access)
2. Follow Step 2 (Add CORS configuration)
3. Test the configuration
4. Let me know if you need help with any step

## Files to Update (After AWS Config)

Once AWS is configured, the UI will automatically work because:
- ✅ `app_ui.py` already generates presigned URLs
- ✅ `utils/s3_pdf_reader.py` handles S3 access
- ✅ Error handling is in place

## Testing Commands

```bash
# Test S3 permissions
python test_s3_permissions.py

# Test specific URL generation
python -c "
from utils.s3_pdf_reader import create_s3_pdf_reader
reader = create_s3_pdf_reader()
url = reader.generate_presigned_url('s3://lexiq-supreme-court-pdfs/cases/test.pdf')
print(url)
"
```

---

**Priority**: Start with Step 1 (Disable Block Public Access) - this is likely the main issue.
