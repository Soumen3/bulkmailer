# CC and BCC Groups Feature Update

## Overview
Enhanced the bulk mailer to support selecting CC and BCC recipients from contact groups, in addition to manual email entry. This provides more flexibility and organization for campaign management.

## Changes Made

### 1. Model Updates (`mailer/models.py`)
Added two new ManyToMany fields to EmailCampaign model:
- **`cc_groups`**: ManyToManyField linking to ContactGroup (related_name='cc_campaigns')
- **`bcc_groups`**: ManyToManyField linking to ContactGroup (related_name='bcc_campaigns')

Both fields are optional (blank=True) and allow selecting multiple groups.

### 2. Form Updates (`mailer/forms.py`)
- **Added fields**: `cc_groups` and `bcc_groups` with CheckboxSelectMultiple widgets
- **Updated labels**:
  - `cc`: "CC (Manual Email Addresses)"
  - `bcc`: "BCC (Manual Email Addresses)"
  - `cc_groups`: "CC Groups"
  - `bcc_groups`: "BCC Groups"
- **Updated help texts**: Clear descriptions distinguishing manual emails from group selection
- **Queryset filtering**: Both group fields are filtered to show only the user's own groups

### 3. Email Utility Updates (`mailer/email_utils.py`)
Updated `send_campaign_emails()` function to:
- **Parse CC list**:
  1. Extract manual CC emails from `campaign.cc` field
  2. Get all contacts from selected `cc_groups`
  3. Combine both lists
- **Parse BCC list**:
  1. Extract manual BCC emails from `campaign.bcc` field
  2. Get all contacts from selected `bcc_groups`
  3. Combine both lists
- **Remove duplicates**: Uses `dict.fromkeys()` to remove duplicate emails while preserving order
- **Filter active contacts**: Only includes contacts with `is_active=True`

### 4. Template Updates (`mailer/templates/create_campaign.html`)
- **Reorganized layout**: Manual email inputs at top, group selections below
- **Added CC Groups section**:
  - Checkbox list with scrollable container (max-height: 48)
  - Hover effects for better UX
  - Shows contact count for each group
- **Added BCC Groups section**:
  - Similar styling and functionality to CC Groups
  - Clearly labeled as "hidden from recipients"
- **Grid layout**: Side-by-side display on desktop, stacked on mobile

### 5. Database Migration
Created migration `0003_emailcampaign_bcc_groups_emailcampaign_cc_groups.py`
- Adds `bcc_groups` field
- Adds `cc_groups` field
- Successfully applied to database

## Usage

### Creating a Campaign with CC/BCC

#### Option 1: Manual Email Addresses
```
CC: manager@company.com, team-lead@company.com
BCC: archive@company.com
```

#### Option 2: Select Groups
- **CC Groups**: Check boxes for groups like "Management Team", "Sales Team"
- **BCC Groups**: Check boxes for groups like "Archive", "Compliance"

#### Option 3: Combine Both
You can use both manual emails AND groups:
- **CC Manual**: `external@partner.com`
- **CC Groups**: "Internal Team" (50 contacts)
- **Result**: All 51 recipients (external + internal team) receive CC

### Example Scenarios

#### Scenario 1: Newsletter with Team CC
**Setup:**
- **Main Recipients**: "Newsletter Subscribers" group (500 contacts)
- **CC Groups**: "Content Team" group (5 members)
- **Sending Mode**: Standard

**Result:**
Each of the 500 subscribers receives an email with:
- To: their email
- CC: all 5 content team members (visible)

#### Scenario 2: Campaign with Archive BCC
**Setup:**
- **Main Recipients**: "Premium Customers" group (100 contacts)
- **BCC Groups**: "Email Archive" group (1 email)
- **BCC Manual**: `compliance@company.com`

**Result:**
Each of 100 customers receives email with:
- To: their email
- BCC: archive email + compliance email (hidden from customers)

#### Scenario 3: Complex Multi-Group Setup
**Setup:**
- **Main Recipients**: "Active Users" group (1000 contacts)
- **CC Manual**: `external-consultant@partner.com`
- **CC Groups**: "Project Managers" (3 contacts), "Executives" (2 contacts)
- **BCC Groups**: "Audit Team" (2 contacts)

**Result:**
Each of 1000 users receives:
- To: their email
- CC: 1 external + 3 PMs + 2 executives = 6 CC recipients (visible)
- BCC: 2 audit team members (hidden)

## Technical Details

### Email List Compilation
```python
# In email_utils.py - send_campaign_emails()

cc_list = []
# Add manual CC emails
if campaign.cc:
    cc_list.extend([email.strip() for email in campaign.cc.split(',') if email.strip()])

# Add CC group emails
for group in campaign.cc_groups.all():
    cc_contacts = Contact.objects.filter(group=group, is_active=True)
    cc_list.extend([contact.email for contact in cc_contacts])

# Remove duplicates while preserving order
cc_list = list(dict.fromkeys(cc_list))
```

### Duplicate Handling
If the same email appears in multiple places (e.g., manual CC and in a CC group), it's automatically deduplicated. Only one instance of each email address will be included.

### Active Contact Filtering
Only contacts marked as `is_active=True` are included from groups. Inactive contacts are automatically excluded.

## UI Features

### Group Selection
- **Scrollable lists**: Prevents UI overflow with many groups
- **Hover effects**: Visual feedback on group selection
- **Contact counts**: Each group shows number of contacts
- **Empty states**: Friendly message when no groups available
- **Responsive design**: Stacks vertically on mobile devices

### Visual Hierarchy
1. Manual email inputs (for quick individual additions)
2. Group selections (for bulk additions)
3. Clear separation between CC and BCC
4. Consistent styling with campaign form

## Benefits

1. **Organized Management**: Select entire teams/departments as CC/BCC
2. **Reusable Groups**: Create groups once, use in multiple campaigns
3. **Flexibility**: Combine manual emails with groups
4. **Automatic Updates**: When group membership changes, campaigns use updated list
5. **Reduced Errors**: Less typing, fewer email address mistakes
6. **Transparency**: See which groups are included before sending
7. **Scalability**: Easily CC/BCC large teams without manual entry

## Validation

- **Manual emails**: Still validated as proper email format
- **Group selections**: No validation needed (pre-validated contacts)
- **Duplicates**: Automatically handled
- **Empty selections**: Both manual and groups can be empty (optional)

## Testing Checklist

- [x] Model changes applied successfully
- [x] Form displays CC and BCC group options
- [x] Manual emails still work
- [x] Group emails are extracted correctly
- [x] Duplicates are removed
- [x] Both CC and BCC groups can be selected
- [ ] Test campaign with only CC groups (no manual)
- [ ] Test campaign with only manual CC (no groups)
- [ ] Test campaign with both CC groups and manual emails
- [ ] Test campaign with duplicate emails in manual and group
- [ ] Verify inactive contacts are excluded
- [ ] Test with empty groups
- [ ] Test with groups having many contacts (100+)

## Migration Notes

**Database Changes:**
- Two new many-to-many relationship tables created
- Existing campaigns unaffected (backward compatible)
- No data migration needed

**Backward Compatibility:**
- Old campaigns with only manual CC/BCC still work
- New campaigns can use groups, manual, or both
- Template gracefully handles missing groups

## Future Enhancements

Possible improvements:
1. **Individual CC/BCC contacts**: Select specific contacts (not just groups)
2. **Smart groups**: Dynamic groups based on criteria
3. **CC/BCC exclusions**: Select groups to exclude from CC/BCC
4. **Preview recipients**: Show full list before sending
5. **CC/BCC templates**: Save common CC/BCC configurations
6. **Conditional CC/BCC**: Different CC/BCC based on recipient segment

## Notes

- **CC Groups are visible**: All recipients can see CC'd group members
- **BCC Groups are hidden**: Recipients cannot see BCC'd group members
- **Groups apply to ALL emails**: Each recipient gets the same CC/BCC list
- **Active contacts only**: Inactive group members are excluded
- **Order preserved**: First manual emails, then group emails (per group)
