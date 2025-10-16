# Email Sending Documentation

## Overview
BulkMailer provides robust email sending capabilities with support for both bulk (BCC) and personalized (individual) email campaigns.

## Features

### 1. Two Sending Modes

#### BCC Mode (Recommended for Bulk)
- All recipients receive the same email via BCC
- Faster and more efficient
- Uses fewer server resources
- Recipients' email addresses are hidden from each other
- Best for newsletters and announcements

#### Individual Mode (Personalized)
- Each recipient receives a separate email
- Supports personalization with template variables
- Takes longer for large lists
- Best for personalized messages

### 2. Personalization Variables
When using Individual Mode, you can use these placeholders in your email content:

- `{{first_name}}` - Contact's first name
- `{{last_name}}` - Contact's last name
- `{{full_name}}` - Contact's full name
- `{{email}}` - Contact's email address

Example:
```html
<p>Hello {{first_name}},</p>
<p>Thank you for subscribing to our newsletter!</p>
```

### 3. Email Tracking
The system tracks:
- Delivery status (sent/failed)
- Send timestamps
- Error messages for failed emails
- Individual email logs per campaign

## Configuration

### Email Settings (settings.py)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # Use Gmail App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

### Gmail Setup
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password
4. Use the App Password in `EMAIL_HOST_PASSWORD`

## Usage

### Method 1: Via Web Interface (Automatic - Recommended)
1. Create a campaign with recipients and content
2. Choose sending method (BCC or Individual)
3. Click "Create & Send Campaign"
4. **Emails are sent automatically upon creation!**
5. View results and statistics on the dashboard

**Benefits:**
- Immediate delivery after campaign creation
- No separate confirmation step
- Streamlined workflow
- Instant feedback on success/failure

### Method 2: Via Command Line (Manual Control)
Use this method to send existing campaigns or have more control over the sending process.

#### Test Email Configuration
```bash
python manage.py test_email
```

Test with a specific email:
```bash
python manage.py test_email --to recipient@example.com
```

#### Send Campaign via Command Line
```bash
python manage.py send_campaign <campaign_id>
```

Send with individual emails:
```bash
python manage.py send_campaign <campaign_id> --individual
```

### Method 3: Programmatically

```python
from mailer.models import EmailCampaign
from mailer.email_utils import send_campaign_emails

# Get campaign
campaign = EmailCampaign.objects.get(id=1)

# Send via BCC
result = send_campaign_emails(campaign, send_individually=False)

# Send individually (personalized)
result = send_campaign_emails(campaign, send_individually=True)

# Check result
if result['success']:
    print(f"Sent: {result['sent']}, Failed: {result['failed']}")
else:
    print(f"Error: {result['message']}")
```

## API Reference

### `send_campaign_emails(campaign, send_individually=False)`
Main function to send campaign emails.

**Parameters:**
- `campaign` (EmailCampaign): Campaign instance to send
- `send_individually` (bool): If True, sends individual emails; if False, uses BCC

**Returns:**
```python
{
    'success': bool,
    'message': str,
    'sent': int,
    'failed': int,
}
```

### `get_campaign_recipients(campaign)`
Get all unique active recipients for a campaign.

**Parameters:**
- `campaign` (EmailCampaign): Campaign instance

**Returns:**
- QuerySet of Contact objects

### `send_bcc_email(campaign, recipients, from_email, reply_to)`
Send one email with all recipients in BCC.

### `send_individual_emails(campaign, recipients, from_email, reply_to)`
Send individual personalized emails to each recipient.

## Email Logs

Every email sent is logged in the `EmailLog` model with:
- Campaign reference
- Contact reference
- Delivery status (pending/sending/sent/failed/bounced)
- Error messages (if failed)
- Timestamps

### Checking Campaign Statistics

```python
campaign = EmailCampaign.objects.get(id=1)

# Get statistics
total = campaign.get_total_recipients()
sent = campaign.get_sent_count()
failed = campaign.get_failed_count()
delivery_rate = campaign.get_delivery_rate()

print(f"Total: {total}, Sent: {sent}, Failed: {failed}")
print(f"Delivery Rate: {delivery_rate}%")
```

## Best Practices

### 1. Testing
- Always test with a small group first
- Use the `test_email` command to verify configuration
- **Important**: Since campaigns auto-send, test with yourself or a test group first
- Create a test contact group before sending to real recipients
- Review the HTML preview before submitting

### 2. Auto-Send Workflow
- **Double-check everything** before clicking "Create & Send Campaign"
- Verify recipient selection (groups and individual contacts)
- Review email content thoroughly
- Test personalization variables if using Individual Mode
- Check from_email and from_name
- No confirmation step - emails send immediately!

### 3. SMTP Limits
- Gmail: 500 emails/day (free), 2000/day (Google Workspace)
- Add delays between emails if sending individually
- Monitor your email provider's limits
- Consider creating campaigns in batches for large lists

### 3. Content Guidelines
- Include unsubscribe links
- Use proper HTML structure
- Provide plain text alternative
- Test email rendering in different clients

### 4. Avoiding Spam Filters
- Use a verified sender email
- Include proper headers (from_name, reply_to)
- Avoid spam trigger words
- Maintain good sender reputation

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- For Gmail, use App Password, not regular password
- Check if 2FA is enabled

#### 2. Connection Refused
- Verify EMAIL_HOST and EMAIL_PORT
- Check EMAIL_USE_TLS setting
- Ensure firewall allows SMTP connections

#### 3. Emails Not Received
- Check spam/junk folders
- Verify recipient email addresses
- Check EmailLog for error messages
- Review SMTP provider's sending limits

#### 4. Slow Sending
- Use BCC mode for large lists
- Consider background task queue (Celery) for production
- Batch large campaigns

### Debug Mode

Enable verbose email logging:
```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Production Considerations

### 1. Use Background Tasks
For large campaigns, use Celery or similar:
```python
from celery import shared_task

@shared_task
def send_campaign_async(campaign_id, send_individually=False):
    campaign = EmailCampaign.objects.get(id=campaign_id)
    return send_campaign_emails(campaign, send_individually)
```

### 2. Rate Limiting
Implement delays between individual emails:
```python
import time

for contact in recipients:
    send_email(contact)
    time.sleep(0.5)  # 500ms delay
```

### 3. Email Queue
For high-volume sending, consider dedicated email services:
- SendGrid
- Mailgun
- Amazon SES
- Postmark

### 4. Monitoring
- Set up alerts for failed campaigns
- Monitor bounce rates
- Track delivery statistics
- Log all email activities

## Security

### 1. Environment Variables
Store credentials securely:
```python
# settings.py
import os
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASSWORD')
```

### 2. Validate Recipients
- Sanitize email addresses
- Validate contact ownership
- Prevent unauthorized sending

### 3. CSRF Protection
All sending endpoints require CSRF tokens.

### 4. User Isolation
Each user can only send to their own contacts.

## Support

For issues or questions:
1. Check EmailLog for error details
2. Run `test_email` command to verify configuration
3. Review Django logs for detailed errors
4. Check SMTP provider's documentation
