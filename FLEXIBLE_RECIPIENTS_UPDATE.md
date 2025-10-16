# Flexible Recipients Update

## Overview
Updated the email campaign system to allow flexible recipient selection. You can now send emails with any combination of main recipients (To), CC, and BCC - or use just one of these fields.

## What Changed

### 1. Form Validation (`mailer/forms.py`)
**Before:** Required at least one contact group or individual contact (main recipients).

**After:** Accepts any combination of:
- Main recipients (To field): Contact groups or individual contacts
- CC recipients: Manual emails or contact groups
- BCC recipients: Manual emails or contact groups

You must have at least ONE of these, but any combination is valid.

**New Validation Logic:**
```python
# Check if there are any recipients at all (main TO, CC, or BCC)
has_main_recipients = bool(contact_groups or individual_contacts)
has_cc_recipients = bool(cc.strip() or cc_groups)
has_bcc_recipients = bool(bcc.strip() or bcc_groups)

# Ensure at least one recipient is selected (can be TO, CC, or BCC)
if not (has_main_recipients or has_cc_recipients or has_bcc_recipients):
    raise forms.ValidationError(
        "Please select at least one recipient. You can choose main recipients (To), "
        "CC recipients, or BCC recipients - or any combination of them."
    )
```

### 2. Email Sending Logic (`mailer/email_utils.py`)

#### Added New Function: `send_cc_bcc_only_email()`
Handles the case where there are no main recipients - only CC and/or BCC recipients.

```python
def send_cc_bcc_only_email(campaign, from_email, reply_to, cc_list, bcc_list):
    """
    Send one email with only CC/BCC recipients (no main To recipients)
    """
    # Creates email with empty To field: to=[]
    # All recipients go in CC or BCC fields
```

#### Updated `send_campaign_emails()`
Now checks for CC/BCC recipients before failing:
- If no main recipients but has CC/BCC → calls `send_cc_bcc_only_email()`
- If has main recipients → proceeds with normal sending (BCC mode or individual mode)
- If no recipients at all → returns error

### 3. User Interface (`create_campaign.html`)

#### Updated Section Title
**Before:** "Select Recipients"
**After:** "Main Recipients (To)"

#### Updated Description
**Before:** "Choose at least one contact group or individual contact"
**After:** "Select main recipients for the 'To' field (optional if using CC/BCC)"

#### Added Help Text
- Contact Groups: "Main recipients in the 'To' field (optional if using CC/BCC)"
- Individual Contacts: "Individual contacts in the 'To' field (optional if using CC/BCC)"

### 4. Form Field Labels (`mailer/forms.py`)
Added help texts to clarify that main recipients are optional:
```python
help_texts = {
    'contact_groups': 'Main recipients in the "To" field (optional if using CC/BCC)',
    'individual_contacts': 'Individual contacts in the "To" field (optional if using CC/BCC)',
    ...
}
```

## Use Cases Now Supported

### ✅ Case 1: Traditional Email (Main Recipients Only)
- Select contact groups or individual contacts
- Leave CC/BCC empty
- Emails sent to main recipients in "To" field

### ✅ Case 2: CC Only
- Leave main recipients empty
- Add CC emails or select CC groups
- All recipients in CC field (visible to each other)

### ✅ Case 3: BCC Only
- Leave main recipients empty
- Add BCC emails or select BCC groups
- All recipients in BCC field (hidden from each other)

### ✅ Case 4: Mixed Recipients
- Select main recipients (To field)
- Add CC recipients (visible copies)
- Add BCC recipients (hidden copies)
- All receive the same email

### ✅ Case 5: CC + BCC (No Main Recipients)
- Leave main recipients empty
- Add both CC and BCC recipients
- CC recipients see each other, BCC recipients are hidden

## How Email Sending Works

### Standard Mode (Recommended)
When there are **main recipients**:
- Each main recipient gets individual email with their address in "To" field
- CC recipients copied on each email (visible to all)
- BCC recipients copied on each email (hidden from others)

When there are **NO main recipients** (CC/BCC only):
- One email sent with empty "To" field
- CC recipients in CC field (visible)
- BCC recipients in BCC field (hidden)

### Personalized Mode
When there are **main recipients**:
- Each main recipient gets personalized email
- Placeholders replaced: {{first_name}}, {{last_name}}, {{email}}
- CC and BCC added to each personalized email

When there are **NO main recipients** (CC/BCC only):
- Same as Standard Mode (one email, no personalization)
- Personalization only applies to main recipients

## Testing

### Test Scenario 1: CC Only Campaign
1. Create new campaign
2. Leave "Main Recipients" empty (no groups, no contacts)
3. Add CC emails: `test1@example.com, test2@example.com`
4. Submit form
5. ✅ Email sent with empty To field, recipients in CC

### Test Scenario 2: BCC Only Campaign
1. Create new campaign
2. Leave "Main Recipients" empty
3. Select BCC contact groups
4. Submit form
5. ✅ Email sent with empty To field, recipients in BCC

### Test Scenario 3: Traditional Campaign
1. Create new campaign
2. Select contact groups in "Main Recipients"
3. Optionally add CC/BCC
4. Submit form
5. ✅ Each main recipient gets email in their "To" field

### Test Scenario 4: No Recipients at All
1. Create new campaign
2. Leave everything empty (no To, no CC, no BCC)
3. Submit form
4. ❌ Validation error: "Please select at least one recipient..."

## Benefits

1. **More Flexibility**: Use email the way you're used to (like Gmail/Outlook)
2. **Better Privacy**: BCC-only campaigns hide all recipient emails
3. **Professional CC Usage**: Properly CC stakeholders without main recipients
4. **Simplified Workflow**: Don't need fake "To" addresses when you only want CC/BCC
5. **Standards Compliant**: Works like standard email clients

## Technical Notes

- CC/BCC groups are resolved to individual email addresses before sending
- Duplicate emails are removed automatically (if someone is in multiple groups)
- EmailLog entries are only created for main recipients (not CC/BCC)
- Campaign statistics track main recipients only
- The `from_email` is automatically set from settings (user doesn't need to specify)

## Migration Required

No database migration needed - all changes are in validation and sending logic.

## Backward Compatibility

✅ **Fully backward compatible**
- Existing campaigns with main recipients work exactly as before
- Old validation rule was stricter (required main recipients)
- New validation rule is more flexible (accepts CC/BCC as valid)
- No existing functionality broken

## Future Enhancements

Consider adding:
1. EmailLog entries for CC/BCC recipients to track their engagement
2. Option to disable CC/BCC when using personalized mode
3. Warning when sending CC-only (recipients can see each other)
4. Recipient count preview showing To/CC/BCC breakdown
5. Test mode to send to only yourself with all recipients listed

---

**Created:** October 16, 2025
**Last Updated:** October 16, 2025
**Status:** ✅ Implemented and Ready for Testing
