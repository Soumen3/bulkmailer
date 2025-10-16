# Quick Start: Sending Emails in BulkMailer

## 1. Test Your Email Configuration

```bash
python manage.py test_email
```

If this works, your email setup is correct! ✓

## 2. Create and Send a Campaign

### Via Web Interface (Automatic Sending)
1. Go to Dashboard → Create Campaign
2. Fill in campaign details:
   - Campaign name
   - Email subject
   - From email (your email)
   - From name (optional)
   - HTML content
3. Select recipients (groups or individual contacts)
4. Choose sending method:
   - **BCC Mode**: All recipients in one email (faster, recommended)
   - **Individual Mode**: Separate emails (personalized with variables)
5. Click "Create & Send Campaign"
6. **Emails will be sent automatically!** ✨

### Via Command Line (Manual Control)
```bash
# Send existing campaign with ID 1
python manage.py send_campaign 1

# Send with personalization
python manage.py send_campaign 1 --individual
```

## 3. Check Results

View campaign statistics on the dashboard:
- Total recipients
- Successfully sent
- Failed deliveries
- Delivery rate

## Personalization Examples

Use these in your email content when using Individual Mode:

```html
<h1>Hello {{first_name}}!</h1>
<p>Dear {{full_name}},</p>
<p>Your email is: {{email}}</p>
<p>Hi {{last_name}}, welcome!</p>
```

## Common Commands

```bash
# Test email
python manage.py test_email --to your@email.com

# Send campaign
python manage.py send_campaign <campaign_id>

# Send with individual emails
python manage.py send_campaign <campaign_id> --individual

# Run migrations (if needed)
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## Troubleshooting Quick Fixes

### "Authentication failed"
→ Check EMAIL_HOST_PASSWORD in settings.py
→ Use Gmail App Password (not regular password)

### "Connection refused"
→ Verify EMAIL_HOST = 'smtp.gmail.com'
→ Verify EMAIL_PORT = 587
→ Verify EMAIL_USE_TLS = True

### "No recipients found"
→ Make sure contacts exist
→ Check contacts are marked as active
→ Verify contacts are assigned to the campaign

### Emails go to spam
→ Verify sender email
→ Add proper from_name
→ Include unsubscribe link
→ Test content with spam checkers

## Important Notes

⚠️ **AUTO-SEND ENABLED**: Emails are sent IMMEDIATELY when you create a campaign!
⚠️ **Test First**: Always create a test campaign with yourself as recipient first
⚠️ **Gmail Limits**: 500 emails/day for free accounts
⚠️ **Double Check**: Review all details before clicking "Create & Send Campaign"
⚠️ **No Undo**: Once sent, you cannot recall emails
⚠️ **BCC vs Individual**: Use BCC for bulk, Individual for personalization
⚠️ **App Password**: Gmail requires App Password, not your regular password

## Email Settings (settings.py)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # 16-character App Password
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
```

## Need Help?

1. Run: `python manage.py test_email`
2. Check: `/admin/mailer/emaillog/` for error messages
3. Review: EMAIL_SENDING_GUIDE.md for detailed documentation
