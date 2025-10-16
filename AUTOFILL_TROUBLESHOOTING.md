# Template Auto-Fill Troubleshooting Guide

## Issue: HTML field not filling when template is selected

### Enhanced Debug Version Installed ✅

I've updated the code with **extensive debug logging** to help us find the issue.

## Step-by-Step Testing Process

### 1. Start the Server
```powershell
.\.venv\Scripts\Activate.ps1
python manage.py runserver
```

### 2. Open the Page
Navigate to: http://127.0.0.1:8000/campaign/create/

### 3. Open Browser Console
- Press **F12** (or Right-click → Inspect → Console tab)
- Make sure you're on the **Console** tab

### 4. Check Initial Logs

When the page loads, you should see these logs:

```
Data element found: <script type="application/json" id="templates-data">
Raw text content: [{"id": ..., "name": ..., ...}]
Parsed templates data: Array(X) [...]
✓ Template select found: true
✓ Subject field found: true
✓ HTML field found: true
✓ Text field found: true
✅ Template auto-fill event listener registered
```

**If you see any ❌ (red X) messages, that's the problem!**

### 5. Select a Template

When you select a template from the dropdown, you should see:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Template dropdown changed!
Selected value: "3"
Selected ID: 3
Available templates: Array(X) [...]
Found template: {id: 3, name: "...", subject: "...", html_content: "...", ...}
Starting to fill fields...
✓ Subject: "" → "Your Subject"
✓ HTML: "" → "<h1>Your HTML Content...</h1>..."
✓ HTML length: 123 characters
✓ Triggered input event for preview update
✓ Text: "" → "Your text content..."
✓ Notification shown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Common Issues & Solutions

### Issue 1: "❌ Template data element not found"

**Cause:** Backend not passing template data or json_script not rendering

**Solution:**
1. Check if you have any active templates:
   - Go to Templates page
   - Make sure at least one template is marked as "Active"

2. Check view code in `mailer/views.py` (around line 100):
   ```python
   templates = EmailTemplate.objects.filter(user=request.user, is_active=True).values(...)
   templates_json = json.dumps(list(templates))
   ```

3. View page source (Ctrl+U) and search for: `id="templates-data"`
   - Should see: `<script type="application/json" id="templates-data">[...]</script>`

### Issue 2: "❌ HTML content field not found!"

**Cause:** Form field ID is different than expected

**Solution:**
1. In browser console, run:
   ```javascript
   document.querySelector('textarea').id
   ```
   This will show you the actual ID of the textarea

2. Check the form HTML:
   - Look for the HTML content textarea
   - Verify it has `id="id_html_content"`

### Issue 3: Logs show template found but field not filling

**Cause:** JavaScript unable to set field value

**Solution:**
Test manually in console:
```javascript
// Get the field
const field = document.getElementById('id_html_content');
console.log('Field:', field);

// Try to set value
field.value = '<h1>Test</h1>';
console.log('Field value after setting:', field.value);

// Check if it's read-only or disabled
console.log('Read-only?', field.readOnly);
console.log('Disabled?', field.disabled);
```

### Issue 4: "Template not found in data array"

**Cause:** Template ID mismatch between dropdown and data

**Solution:**
In console, run:
```javascript
// Check what's in the dropdown
const select = document.getElementById('id_use_template');
Array.from(select.options).forEach(opt => {
  console.log('Option:', opt.value, '-', opt.text);
});

// Check what's in the data
const data = JSON.parse(document.getElementById('templates-data').textContent);
console.log('Data IDs:', data.map(t => t.id));
```

### Issue 5: Field fills but preview doesn't update

**Cause:** Preview update event not working

**Solution:**
Manually trigger preview in console:
```javascript
const field = document.getElementById('id_html_content');
field.value = '<h1>Test</h1>';
field.dispatchEvent(new Event('input', { bubbles: true }));
```

## Manual Test Commands

### Test 1: Check if everything exists
```javascript
console.log('Template data:', document.getElementById('templates-data'));
console.log('Select:', document.getElementById('id_use_template'));
console.log('HTML field:', document.getElementById('id_html_content'));
console.log('Subject field:', document.getElementById('id_subject'));
```

### Test 2: Parse template data
```javascript
const data = JSON.parse(document.getElementById('templates-data').textContent);
console.log('Templates:', data);
console.log('First template:', data[0]);
```

### Test 3: Manually fill field
```javascript
const field = document.getElementById('id_html_content');
const data = JSON.parse(document.getElementById('templates-data').textContent);
field.value = data[0].html_content;
console.log('Manual fill successful!');
```

### Test 4: Test the full auto-fill
```javascript
const select = document.getElementById('id_use_template');
const data = JSON.parse(document.getElementById('templates-data').textContent);

// Get first template ID
const firstTemplateId = data[0].id;

// Set dropdown to that template
select.value = firstTemplateId;

// Trigger change event
select.dispatchEvent(new Event('change'));
```

## Expected vs Actual Behavior

### ✅ EXPECTED:
1. Page loads
2. Console shows all elements found
3. User selects template
4. Console shows detailed logs
5. Subject field fills
6. **HTML field fills** ← THIS IS THE KEY ISSUE
7. Text field fills
8. Preview updates
9. Green notification appears

### ❌ ACTUAL (Your Issue):
1. Page loads ✓
2. User selects template ✓
3. Subject field fills (probably) ✓
4. **HTML field DOES NOT fill** ← PROBLEM HERE
5. ???

## Debug Checklist

Run through this checklist and note the results:

- [ ] Open page, press F12
- [ ] See "✅ Template auto-fill event listener registered" in console
- [ ] Select a template from dropdown
- [ ] See "Template dropdown changed!" in console
- [ ] See "Found template: {...}" with actual data
- [ ] See "✓ HTML: ... → ..." showing old and new values
- [ ] See "✓ HTML length: X characters" with number > 0
- [ ] Check HTML field visually - is it filled?
- [ ] Run in console: `document.getElementById('id_html_content').value`
- [ ] Does it show HTML content?

## What to Report Back

Please share:

1. **Full console output** after selecting a template
2. **Result of:** `document.getElementById('id_html_content').value`
3. **Any error messages** (in red in console)
4. **Screenshot** of the page and console side-by-side

## Quick Fix Test

Try this in the console after selecting a template:

```javascript
// Force fill the HTML field
const select = document.getElementById('id_use_template');
const htmlField = document.getElementById('id_html_content');
const data = JSON.parse(document.getElementById('templates-data').textContent);

console.log('Current template:', select.value);
const template = data.find(t => t.id == select.value);
console.log('Found:', template);

if (template) {
  htmlField.value = template.html_content;
  console.log('Manually filled. Check field now!');
} else {
  console.log('No template found!');
}
```

## Additional Checks

### Check Form Widget
The HTML field might have restrictions. Check in `mailer/forms.py`:

```python
'html_content': forms.Textarea(attrs={
    'class': '...',
    'style': 'min-height: 480px; resize: vertical;',
    'placeholder': '...'
})
```

Make sure there's NO:
- `readonly='readonly'`
- `disabled='disabled'`
- JavaScript that's overriding the value

### Check for Conflicting JavaScript
Search the page source for other JavaScript that might be:
- Clearing the field
- Preventing value changes
- Intercepting change events

---

**Next Steps:**
1. Open the page: http://127.0.0.1:8000/campaign/create/
2. Open console (F12)
3. Select a template
4. Copy ALL console output
5. Share it with me so we can diagnose the exact issue

The new debug version will tell us **exactly** where the problem is! 🔍
