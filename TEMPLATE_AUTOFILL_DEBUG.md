# Template Auto-Fill Debug Guide

## Overview
The template auto-fill feature is now implemented with debug logging to help identify any issues.

## How It Should Work

### Expected Behavior:
1. Navigate to "Create Campaign" page
2. In the "Template Selection" dropdown, select a template
3. **Instantly**, the following fields should auto-fill:
   - ✅ **Subject** field
   - ✅ **HTML Content** field
   - ✅ **Text Content** field (if template has it)
4. **Live Preview** should update automatically
5. Green notification appears: "Template content loaded!"

## Debug Steps

### Step 1: Open Browser Console
1. Open the Create Campaign page: http://127.0.0.1:8000/campaign/create/
2. Press **F12** to open Developer Tools
3. Go to the **Console** tab

### Step 2: Check Initial Logs
You should see these console logs when the page loads:
```
Templates loaded: Array(n) [...]
Template select element: <select id="id_use_template">
HTML content field: <textarea id="id_html_content">
```

**If you don't see these logs:**
- ❌ Problem: JavaScript not loading
- Solution: Check browser console for errors

### Step 3: Select a Template
1. Click on the "Use Template" dropdown
2. Select any template from the list
3. Watch the console for these logs:
```
Selected template ID: 3
Found template: {id: 3, name: "...", subject: "...", html_content: "...", text_content: "..."}
Subject filled: "..."
HTML content filled: "..."
Text content filled: "..."
```

### Step 4: Verify Fields
After selecting a template, check:
- ✅ Subject field has the template's subject
- ✅ HTML Content textarea has the template's HTML
- ✅ Text Content textarea has the template's text
- ✅ Live preview shows the HTML content
- ✅ Green notification appears at top-right

## Troubleshooting

### Issue 1: No Templates in Dropdown
**Symptoms:**
- Dropdown shows "-- Select a template (optional) --" only
- No template names appear

**Possible Causes:**
1. No active templates created
2. Templates belong to different user

**Solution:**
1. Go to Templates page
2. Create a new template or activate existing ones
3. Make sure templates are marked as "Active"

### Issue 2: Fields Not Auto-Filling
**Symptoms:**
- Template selected but fields remain empty
- Console shows: "Template not found in data"

**Possible Causes:**
1. Template data not loaded from backend
2. Template ID mismatch

**Debug Steps:**
1. Check console log: `Templates loaded: [...]`
2. Verify array contains your templates
3. Check if template IDs match

**Console Commands to Test:**
```javascript
// Check what templates are loaded
console.log(templatesData);

// Check if template select exists
console.log(document.getElementById('id_use_template'));

// Check if HTML content field exists
console.log(document.getElementById('id_html_content'));

// Manually test template loading
const testTemplate = templatesData[0];
document.getElementById('id_html_content').value = testTemplate.html_content;
```

### Issue 3: Preview Not Updating
**Symptoms:**
- Fields fill correctly but preview stays empty

**Possible Cause:**
- Input event not triggering preview update

**Solution:**
The code already includes this fix:
```javascript
htmlContentField.dispatchEvent(new Event('input'));
```

### Issue 4: Console Shows "Template data element not found"
**Symptoms:**
- Console error: "Template data element not found"

**Possible Cause:**
- Backend not passing template data
- json_script filter not rendering

**Debug Steps:**
1. View page source (Ctrl+U)
2. Search for: `<script type="application/json" id="templates-data">`
3. Verify it exists and contains JSON data

**If missing:**
- Check `mailer/views.py` - `create_campaign_view` function
- Verify: `templates_json` is in context
- Verify: `EmailTemplate.objects.filter(user=request.user, is_active=True)` returns results

### Issue 5: Notification Not Appearing
**Symptoms:**
- Fields fill but green notification doesn't show

**Possible Cause:**
- CSS animation not working
- Z-index conflict

**Quick Fix:**
The notification should appear at top-right with:
- Green background
- White text
- Auto-disappears after 3 seconds

## Manual Testing Checklist

### Test 1: Basic Auto-Fill
- [ ] Open Create Campaign page
- [ ] Select template from dropdown
- [ ] Subject field fills automatically
- [ ] HTML content fills automatically
- [ ] Text content fills automatically (if template has it)
- [ ] Green notification appears

### Test 2: Clear Fields
- [ ] Select a template (fields fill)
- [ ] Change dropdown to "-- Select a template (optional) --"
- [ ] All fields clear automatically

### Test 3: Switch Templates
- [ ] Select template A (fields fill)
- [ ] Select template B (fields update to template B content)
- [ ] No leftover content from template A

### Test 4: Preview Update
- [ ] Select template with HTML content
- [ ] Live preview box shows the HTML rendered
- [ ] Preview updates immediately

### Test 5: Form Submission
- [ ] Select template
- [ ] Add recipients
- [ ] Submit form
- [ ] Campaign created with template content

## Expected Console Output (Success)

```
Templates loaded: (2) [{…}, {…}]
  0: {id: 3, name: "Welcome Email", subject: "Welcome!", html_content: "<h1>Welcome</h1>...", text_content: "Welcome..."}
  1: {id: 4, name: "Newsletter", subject: "Monthly Newsletter", html_content: "<html>...</html>", text_content: ""}
  
Template select element: <select id="id_use_template" class="...">
HTML content field: <textarea id="id_html_content" class="...">

[User selects template]

Selected template ID: 3
Found template: {id: 3, name: "Welcome Email", subject: "Welcome!", html_content: "<h1>Welcome</h1>...", text_content: "Welcome..."}
Subject filled: Welcome!
HTML content filled: <h1>Welcome</h1>...
Text content filled: Welcome...
```

## Code Verification

### Backend (views.py)
```python
# Lines ~100-104
templates = EmailTemplate.objects.filter(user=request.user, is_active=True).values('id', 'name', 'subject', 'html_content', 'text_content')
templates_json = json.dumps(list(templates))

return render(request, 'create_campaign.html', {
    'form': form,
    'templates_json': templates_json
})
```

### Template (create_campaign.html)
```django
<!-- Line ~493 -->
{{ templates_json|json_script:"templates-data" }}

<!-- Lines ~495-570 -->
<script>
  let templatesData = [];
  try {
    const dataElement = document.getElementById('templates-data');
    if (dataElement) {
      templatesData = JSON.parse(dataElement.textContent);
      console.log('Templates loaded:', templatesData);
    }
  } catch (e) {
    console.error('Error parsing template data:', e);
  }
  
  document.addEventListener('DOMContentLoaded', function() {
    const templateSelect = document.getElementById('id_use_template');
    
    if (templateSelect) {
      templateSelect.addEventListener('change', function() {
        const selectedTemplateId = parseInt(this.value);
        
        if (selectedTemplateId) {
          const selectedTemplate = templatesData.find(t => t.id === selectedTemplateId);
          
          if (selectedTemplate) {
            // Auto-fill fields
            htmlContentField.value = selectedTemplate.html_content || '';
            // ... etc
          }
        }
      });
    }
  });
</script>
```

## Quick Test Command

Run this in browser console after page loads:
```javascript
// Test if everything is connected
if (document.getElementById('templates-data')) {
  console.log('✅ Template data element exists');
  const data = JSON.parse(document.getElementById('templates-data').textContent);
  console.log('✅ Templates loaded:', data.length);
} else {
  console.log('❌ Template data element NOT found');
}

if (document.getElementById('id_use_template')) {
  console.log('✅ Template dropdown exists');
} else {
  console.log('❌ Template dropdown NOT found');
}

if (document.getElementById('id_html_content')) {
  console.log('✅ HTML content field exists');
} else {
  console.log('❌ HTML content field NOT found');
}
```

## Success Criteria

✅ **Feature Working If:**
1. Console logs show templates loaded
2. Selecting template fills all fields
3. Preview updates automatically
4. Green notification appears
5. No console errors

❌ **Feature NOT Working If:**
1. Console shows errors
2. Fields don't fill
3. Templates array is empty
4. Template select element not found

## Next Steps

1. **Open the page**: http://127.0.0.1:8000/campaign/create/
2. **Open console**: Press F12
3. **Follow the debug steps** above
4. **Report findings**: Share console logs if issue persists

---

**Created:** October 16, 2025
**Purpose:** Debug template auto-fill feature
**Status:** ✅ Debug logging added - ready for testing
