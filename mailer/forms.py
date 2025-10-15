from django import forms
from .models import EmailCampaign, Contact, ContactGroup, EmailTemplate
import csv
import io


class EmailCampaignForm(forms.ModelForm):
    """Form for creating email campaigns"""
    
    # Additional fields for better UX
    use_template = forms.ModelChoiceField(
        queryset=EmailTemplate.objects.none(),
        required=False,
        empty_label="-- Select a template (optional) --",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200'
        })
    )
    
    class Meta:
        model = EmailCampaign
        fields = [
            'name',
            'subject',
            'from_email',
            'from_name',
            'reply_to',
            'html_content',
            'text_content',
            'contact_groups',
            'individual_contacts',
            'scheduled_at',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'e.g., Welcome Email Campaign'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'Email subject line'
            }),
            'from_email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'sender@yourdomain.com'
            }),
            'from_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'Your Name or Company'
            }),
            'reply_to': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'reply@yourdomain.com (optional)'
            }),
            'html_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 12,
                'placeholder': 'Enter your email HTML content here...'
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 8,
                'placeholder': 'Plain text version (optional, but recommended)'
            }),
            'contact_groups': forms.CheckboxSelectMultiple(attrs={
                'class': 'text-cyan-500 focus:ring-cyan-500'
            }),
            'individual_contacts': forms.CheckboxSelectMultiple(attrs={
                'class': 'text-cyan-500 focus:ring-cyan-500'
            }),
            'scheduled_at': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'type': 'datetime-local',
                'placeholder': 'Leave empty to send immediately'
            }),
        }
        labels = {
            'name': 'Campaign Name',
            'subject': 'Email Subject',
            'from_email': 'From Email Address',
            'from_name': 'From Name',
            'reply_to': 'Reply-To Address',
            'html_content': 'Email Content (HTML)',
            'text_content': 'Plain Text Version',
            'contact_groups': 'Select Contact Groups',
            'individual_contacts': 'Select Individual Contacts',
            'scheduled_at': 'Schedule Send Time',
        }
        help_texts = {
            'from_email': 'The email address that will appear as the sender',
            'from_name': 'The name that will appear as the sender',
            'reply_to': 'Where replies will be sent (optional)',
            'html_content': 'You can use HTML tags to format your email',
            'text_content': 'Fallback for email clients that don\'t support HTML',
            'scheduled_at': 'Leave empty to send immediately, or schedule for later',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter querysets to only show user's own data
        if self.user:
            self.fields['contact_groups'].queryset = ContactGroup.objects.filter(user=self.user)
            self.fields['individual_contacts'].queryset = Contact.objects.filter(user=self.user, is_active=True)
            self.fields['use_template'].queryset = EmailTemplate.objects.filter(user=self.user, is_active=True)
        
        # Make some fields optional for better UX
        self.fields['text_content'].required = False
        self.fields['reply_to'].required = False
        self.fields['from_name'].required = False
        self.fields['scheduled_at'].required = False

    def clean(self):
        cleaned_data = super().clean()
        contact_groups = cleaned_data.get('contact_groups')
        individual_contacts = cleaned_data.get('individual_contacts')
        
        # Ensure at least one recipient is selected
        if not contact_groups and not individual_contacts:
            raise forms.ValidationError(
                "Please select at least one contact group or individual contact."
            )
        
        return cleaned_data

    def save(self, commit=True):
        campaign = super().save(commit=False)
        
        # Set the user
        if self.user:
            campaign.user = self.user
        
        # Set status based on scheduling
        if campaign.scheduled_at:
            campaign.status = 'scheduled'
        else:
            campaign.status = 'draft'
        
        if commit:
            campaign.save()
            self.save_m2m()  # Save many-to-many relationships
        
        return campaign


class ContactForm(forms.ModelForm):
    """Form for adding individual contacts"""
    
    class Meta:
        model = Contact
        fields = ['email', 'first_name', 'last_name', 'group']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'email@example.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'First name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'Last name'
            }),
            'group': forms.Select(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter groups to only show user's own groups
        if self.user:
            self.fields['group'].queryset = ContactGroup.objects.filter(user=self.user)
        
        # Make fields optional
        self.fields['first_name'].required = False
        self.fields['last_name'].required = False
        self.fields['group'].required = False
        self.fields['group'].empty_label = "-- No group --"

    def save(self, commit=True):
        contact = super().save(commit=False)
        
        if self.user:
            contact.user = self.user
        
        if commit:
            contact.save()
        
        return contact


class ContactGroupForm(forms.ModelForm):
    """Form for creating contact groups"""
    
    class Meta:
        model = ContactGroup
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'e.g., Newsletter Subscribers'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 3,
                'placeholder': 'Brief description of this group'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False

    def save(self, commit=True):
        group = super().save(commit=False)
        
        if self.user:
            group.user = self.user
        
        if commit:
            group.save()
        
        return group


class EmailTemplateForm(forms.ModelForm):
    """Form for creating email templates"""
    
    class Meta:
        model = EmailTemplate
        fields = ['name', 'description', 'subject', 'html_content', 'text_content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'Template name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 2,
                'placeholder': 'What is this template for?'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'placeholder': 'Default subject line'
            }),
            'html_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 12,
                'placeholder': 'HTML content'
            }),
            'text_content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
                'rows': 8,
                'placeholder': 'Plain text version'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        self.fields['text_content'].required = False

    def save(self, commit=True):
        template = super().save(commit=False)
        
        if self.user:
            template.user = self.user
        
        if commit:
            template.save()
        
        return template


class CSVImportForm(forms.Form):
    """Form for importing contacts from CSV file"""
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with columns: email, first_name (optional), last_name (optional)',
        widget=forms.FileInput(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200',
            'accept': '.csv'
        })
    )
    
    group = forms.ModelChoiceField(
        queryset=ContactGroup.objects.none(),
        required=False,
        empty_label="-- No group (optional) --",
        label='Assign to Group',
        help_text='Optionally assign imported contacts to a group',
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 bg-slate-900/50 border-2 border-slate-700 rounded-xl text-white focus:outline-none focus:border-cyan-500 focus:ring-4 focus:ring-cyan-500/10 transition-all duration-200'
        })
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['group'].queryset = ContactGroup.objects.filter(user=self.user)

    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        # Check file extension
        if not csv_file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        # Check file size (limit to 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise forms.ValidationError('File size must not exceed 5MB.')
        
        return csv_file

    def process_csv(self):
        """Process the CSV file and return list of contact data"""
        csv_file = self.cleaned_data['csv_file']
        group = self.cleaned_data.get('group')
        
        # Read CSV file with proper newline handling
        decoded_file = csv_file.read().decode('utf-8-sig')  # utf-8-sig handles BOM
        io_string = io.StringIO(decoded_file, newline='')  # Add newline='' parameter
        reader = csv.DictReader(io_string)
        
        contacts_data = []
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start from 2 to account for header
            # Get email (required)
            email = row.get('email', '').strip()
            if not email:
                errors.append(f"Row {row_num}: Email is required")
                continue
            
            # Validate email format
            try:
                forms.EmailField().clean(email)
            except forms.ValidationError:
                errors.append(f"Row {row_num}: Invalid email format '{email}'")
                continue
            
            contacts_data.append({
                'email': email,
                'first_name': row.get('first_name', '').strip(),
                'last_name': row.get('last_name', '').strip(),
                'group': group,
                'user': self.user,
            })
        
        return contacts_data, errors
