# Environment Variables Setup

## Overview
Sensitive credentials are now stored in a `.env` file and loaded using `python-dotenv`. This is a security best practice that keeps sensitive data out of version control.

## Setup Instructions

### 1. Environment File Created ✅
A `.env` file has been created in the project root with your current credentials.

**Location:** `c:\Users\user\Desktop\bulkmailer\.env`

### 2. Git Ignore Updated ✅
The `.env` file is already in `.gitignore`, so it won't be committed to Git.

### 3. Example File Created ✅
A `.env.example` file has been created as a template (without sensitive data).

**Location:** `c:\Users\user\Desktop\bulkmailer\.env.example`

## Current Configuration

### Environment Variables in `.env`:
```env
# Django Secret Key
SECRET_KEY=django-insecure-*aky4gv9tymm9kvgbhx_qhjeudfsax&_3(7&)0=3@4vrse@@l3

# Email Configuration
EMAIL_HOST_USER=try.soumen@gmail.com
EMAIL_HOST_PASSWORD=kzyf uexp soin qayr

# Debug Mode
DEBUG=True
```

### Updated `settings.py`:
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(BASE_DIR / '.env')

# Use environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

## How It Works

1. **On Application Start:**
   - `load_dotenv()` reads the `.env` file
   - Loads all key=value pairs as environment variables

2. **Accessing Variables:**
   - `os.getenv('VARIABLE_NAME')` retrieves the value
   - Second parameter is optional fallback/default value

3. **Security:**
   - `.env` is in `.gitignore` (never committed)
   - Sensitive credentials stay on your local machine
   - Share `.env.example` with team (no real credentials)

## For Team Members / Production

### Setting Up on a New Machine:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bulkmailer
   ```

2. **Copy the example file**
   ```bash
   copy .env.example .env
   ```

3. **Edit `.env` with real credentials**
   ```bash
   notepad .env
   ```

4. **Update the values:**
   ```env
   SECRET_KEY=your-real-secret-key
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEBUG=True
   ```

5. **Activate virtual environment and install dependencies**
   ```bash
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

### Production Deployment:

For production servers (Heroku, AWS, etc.):

1. **Set environment variables in hosting platform:**
   - Heroku: `heroku config:set VARIABLE_NAME=value`
   - AWS: Use AWS Secrets Manager or Parameter Store
   - Azure: Use App Settings
   - DigitalOcean: Use App Platform environment variables

2. **Update production settings:**
   ```env
   DEBUG=False
   SECRET_KEY=generate-new-secure-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

## Security Benefits

### ✅ Before (Hardcoded):
```python
EMAIL_HOST_USER = 'try.soumen@gmail.com'  # ❌ Visible in Git
EMAIL_HOST_PASSWORD = 'kzyf uexp soin qayr'  # ❌ Exposed publicly
```

### ✅ After (Environment Variables):
```python
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')  # ✅ Loaded from .env
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # ✅ Secret
```

**Benefits:**
1. ✅ Credentials never in version control
2. ✅ Different values per environment (dev/staging/prod)
3. ✅ Easy to rotate credentials (just update .env)
4. ✅ No code changes needed for different environments
5. ✅ Complies with 12-factor app methodology

## Testing

### Verify Setup:
```python
# In Django shell
python manage.py shell

>>> import os
>>> from dotenv import load_dotenv
>>> from pathlib import Path
>>> load_dotenv()
>>> os.getenv('EMAIL_HOST_USER')
'try.soumen@gmail.com'
>>> os.getenv('EMAIL_HOST_PASSWORD')
'kzyf uexp soin qayr'
```

### Test Email:
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test email.',
    settings.EMAIL_HOST_USER,
    ['recipient@example.com'],
    fail_silently=False,
)
```

## Additional Environment Variables

You can add more variables to `.env`:

```env
# Database (for production)
DATABASE_URL=postgresql://user:password@localhost/dbname

# AWS Credentials
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket

# API Keys
STRIPE_SECRET_KEY=sk_test_...
GOOGLE_API_KEY=AIza...
```

Then use in `settings.py`:
```python
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
```

## Troubleshooting

### Issue: "EMAIL_HOST_USER is None"

**Cause:** `.env` file not loaded or doesn't exist

**Solution:**
```bash
# Check if .env exists
dir .env

# Verify python-dotenv is installed
pip show python-dotenv

# If not installed:
pip install python-dotenv
```

### Issue: Changes to .env not taking effect

**Cause:** Django caches settings

**Solution:**
1. Restart the Django development server
2. Or run: `python manage.py runserver --noreload`

### Issue: Variables showing "None" in production

**Cause:** .env file doesn't exist on production server

**Solution:**
Set environment variables directly on the hosting platform, not via .env file.

## Files Modified

1. ✅ **Created:** `.env` (your actual credentials)
2. ✅ **Created:** `.env.example` (template without secrets)
3. ✅ **Modified:** `bulkmailer/settings.py` (uses os.getenv())
4. ✅ **Verified:** `.gitignore` (already has .env)

## Important Notes

⚠️ **Never commit `.env` to Git!**
- The `.env` file contains your actual passwords
- It's already in `.gitignore`
- Only commit `.env.example`

✅ **Share `.env.example` instead:**
- Contains variable names (no real values)
- Safe to commit to Git
- Team members copy to `.env` and fill in real values

🔐 **Gmail App Passwords:**
- The password in `.env` is a Gmail App Password
- Regular Gmail passwords won't work with SMTP
- Generate at: https://myaccount.google.com/apppasswords

## Next Steps

1. ✅ **Test the application:**
   ```bash
   .\.venv\Scripts\Activate.ps1
   python manage.py runserver
   ```

2. ✅ **Create a campaign and send test email** to verify email settings work

3. ✅ **Commit changes to Git:**
   ```bash
   git add .env.example settings.py .gitignore
   git commit -m "Move credentials to environment variables"
   git push
   ```

4. ⚠️ **Verify .env is NOT in Git:**
   ```bash
   git status
   # Should NOT show .env file
   ```

---

**Status:** ✅ Environment variables configured successfully!
**Security:** ✅ Credentials protected
**Ready for:** Development, Testing, Production deployment
