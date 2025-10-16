# CC and BCC Feature Update

## Overview
Updated the bulk mailer to support CC (Carbon Copy) and BCC (Blind Carbon Copy) fields, and automatically use the host email from settings as the sender.

## Changes Made

### 1. Model Updates (`mailer/models.py`)
- **Added `cc` field**: TextField to store comma-separated CC email addresses
- **Added `bcc` field**: TextField to store comma-separated BCC email addresses
- Both fields are optional (blank=True)

### 2. Form Updates (`mailer/forms.py`)
- **Removed fields**: `from_email` and `from_name` (now auto-set from settings)
- **Added fields**: `cc` and `bcc` with proper widgets and styling
- **Added validation**: Email validation for CC and BCC addresses
  - Validates each comma-separated email address
  - Shows clear error messages for invalid emails
- **Updated labels and help text**: Clear descriptions of what CC and BCC do

### 3. View Updates (`mailer/views.py`)
- **Auto-set sender**: `from_email` is automatically set from `settings.EMAIL_HOST_USER`
- **Auto-set sender name**: `from_name` is set from `settings.DEFAULT_FROM_NAME` (defaults to "Bulk Mailer")
- Added `from django.conf import settings` import

### 4. Email Utility Updates (`mailer/email_utils.py`)
- **Updated `send_campaign_emails()`**: Parses CC and BCC fields from campaign
- **Updated `send_bcc_email()`**: Accepts and includes CC/BCC lists in emails
- **Updated `send_individual_emails()`**: Accepts and includes CC/BCC lists in personalized emails
- CC and BCC recipients are added to EVERY email sent in the campaign

### 5. Template Updates (`mailer/templates/create_campaign.html`)
- **Removed**: From Email and From Name input fields
- **Added**: Blue info box explaining sender is automatically set
- **Added**: CC input field with placeholder and help text
- **Added**: BCC input field with placeholder and help text
- **Updated section title**: "Sender Information" → "Sender & Additional Recipients"

### 6. Database Migration
- Created migration `0002_emailcampaign_bcc_emailcampaign_cc.py`
- Successfully applied to database

## Usage

### Creating a Campaign with CC/BCC

1. **Automatic Sender**: The sender email is automatically set to `try.soumen@gmail.com` (from settings)
2. **Reply-To (Optional)**: Specify where replies should go (if different from sender)
3. **CC (Optional)**: Enter comma-separated email addresses
   - Example: `manager@company.com, team-lead@company.com`
   - These recipients will see each other's addresses
4. **BCC (Optional)**: Enter comma-separated email addresses
   - Example: `archive@company.com, backup@company.com`
   - These recipients are hidden from everyone else

### Example Scenario

**Campaign Setup:**
- Main Recipients: 100 customers from "Newsletter" group
- CC: `sales@company.com, support@company.com`
- BCC: `archive@company.com`

**Result:**
Each of the 100 customers will receive an email with:
- To: their own email address
- CC: sales@company.com, support@company.com (visible to all)
- BCC: archive@company.com (hidden from recipients)

## Technical Details

### Email Address Parsing
```python
# In email_utils.py
cc_list = [email.strip() for email in campaign.cc.split(',') if email.strip()]
bcc_list = [email.strip() for email in campaign.bcc.split(',') if email.strip()]
```

### Email Sending
```python
msg = EmailMultiAlternatives(
    subject=campaign.subject,
    body=text_content,
    from_email=from_email,  # Auto-set from settings
    to=[contact.email],
    cc=cc_list or [],
    bcc=bcc_list or [],
    reply_to=reply_to,
)
```

### Form Validation
```python
# Validates each email in CC/BCC fields
for email in cc_emails:
    try:
        forms.EmailField().clean(email)
    except forms.ValidationError:
        raise forms.ValidationError(f"Invalid CC email address: {email}")
```

## Configuration

To customize the sender name, add to `bulkmailer/settings.py`:
```python
DEFAULT_FROM_NAME = 'Your Company Name'
```

If not set, it defaults to "Bulk Mailer".

## Benefits

1. **Simplified Setup**: No need to enter sender email each time (it's in settings)
2. **Consistent Sender**: All campaigns use the same verified sender
3. **Team Collaboration**: CC keeps team members in the loop
4. **Archive/Compliance**: BCC for automatic archiving or compliance tracking
5. **Error Prevention**: Validation ensures all CC/BCC addresses are valid emails

## Testing Checklist

- [x] Model changes applied successfully
- [x] Form validation works for CC/BCC
- [x] Template displays CC/BCC fields
- [x] Sender auto-set from settings
- [ ] Test campaign with CC recipients
- [ ] Test campaign with BCC recipients
- [ ] Test campaign with both CC and BCC
- [ ] Verify CC recipients are visible to all
- [ ] Verify BCC recipients are hidden

## Notes

- **CC/BCC apply to ALL recipients**: If you send to 100 people, each will get the same CC/BCC recipients
- **Sender cannot be changed per campaign**: It's set at system level for consistency
- **Empty CC/BCC allowed**: Both fields are optional
- **Whitespace handling**: Leading/trailing spaces are automatically removed from email addresses
