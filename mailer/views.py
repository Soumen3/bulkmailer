from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmailCampaignForm, CSVImportForm, ContactGroupForm, EmailTemplateForm
from .models import EmailCampaign, Contact, ContactGroup, EmailTemplate
from .email_utils import send_campaign_emails, import_contacts_from_csv

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Welcome back!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required(login_url='login')
def dashboard_view(request):
    # Get user's campaigns
    campaigns = EmailCampaign.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get statistics
    total_campaigns = EmailCampaign.objects.filter(user=request.user).count()
    total_sent = EmailCampaign.objects.filter(user=request.user, status='sent').count()
    
    context = {
        'campaigns': campaigns,
        'total_campaigns': total_campaigns,
        'total_sent': total_sent,
    }
    
    return render(request, 'dashboard.html', context)

@login_required(login_url='login')
def create_campaign_view(request):
    if request.method == 'POST':
        form = EmailCampaignForm(request.POST, user=request.user)
        if form.is_valid():
            campaign = form.save()
            messages.success(request, f'Campaign "{campaign.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = EmailCampaignForm(user=request.user)
    
    return render(request, 'create_campaign.html', {'form': form})

@login_required(login_url='login')
def import_contacts_view(request):
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Process CSV
            contacts_data, errors = form.process_csv()
            
            if errors:
                for error in errors:
                    messages.error(request, error)
            
            # Import contacts
            if contacts_data:
                result = import_contacts_from_csv(contacts_data, request.user)
                messages.success(request, f'Successfully imported {result["imported"]} contacts. Skipped {result["skipped"]} duplicates.')
                
                if result['errors']:
                    for error in result['errors']:
                        messages.error(request, error)
                
                return redirect('dashboard')
            else:
                messages.error(request, 'No valid contacts found in CSV file.')
    else:
        form = CSVImportForm(user=request.user)
    
    return render(request, 'import_contacts.html', {'form': form})

@login_required(login_url='login')
def create_group_view(request):
    if request.method == 'POST':
        form = ContactGroupForm(request.POST, user=request.user)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Contact group "{group.name}" created successfully!')
            return redirect('dashboard')
    else:
        form = ContactGroupForm(user=request.user)
    
    return render(request, 'create_group.html', {'form': form})

@login_required(login_url='login')
def create_template_view(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, user=request.user)
        if form.is_valid():
            print("Creating email template")
            template = form.save()
            messages.success(request, f'Email template "{template.name}" created successfully!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EmailTemplateForm(user=request.user)
    
    return render(request, 'create_template.html', {'form': form})

@login_required(login_url='login')
def send_campaign_view(request, campaign_id):
    campaign = get_object_or_404(EmailCampaign, id=campaign_id, user=request.user)
    
    if request.method == 'POST':
        # Send the campaign
        result = send_campaign_emails(campaign)
        
        if result['success']:
            messages.success(request, result['message'])
        else:
            messages.error(request, result['message'])
        
        return redirect('dashboard')
    
    # Show confirmation page
    return render(request, 'send_campaign.html', {'campaign': campaign})

@login_required(login_url='login')
def contacts_list_view(request):
    """Display all contacts for the user"""
    contacts = Contact.objects.filter(user=request.user).select_related('group').order_by('-created_at')
    
    # Get statistics
    total_contacts = contacts.count()
    active_contacts = contacts.filter(is_active=True).count()
    grouped_contacts = contacts.exclude(group=None).count()
    
    context = {
        'contacts': contacts,
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
        'grouped_contacts': grouped_contacts,
    }
    
    return render(request, 'contacts_list.html', context)

@login_required(login_url='login')
def groups_list_view(request):
    """Display all contact groups for the user"""
    groups = ContactGroup.objects.filter(user=request.user).prefetch_related('contact_set').order_by('-created_at')
    
    # Get statistics
    total_groups = groups.count()
    total_contacts_in_groups = Contact.objects.filter(user=request.user, group__isnull=False).count()
    
    context = {
        'groups': groups,
        'total_groups': total_groups,
        'total_contacts_in_groups': total_contacts_in_groups,
    }
    
    return render(request, 'groups_list.html', context)

@login_required(login_url='login')
def templates_list_view(request):
    """Display all email templates for the user"""
    templates = EmailTemplate.objects.filter(user=request.user).order_by('-created_at')
    
    # Get statistics
    total_templates = templates.count()
    active_templates = templates.filter(is_active=True).count()
    
    context = {
        'templates': templates,
        'total_templates': total_templates,
        'active_templates': active_templates,
    }
    
    return render(request, 'templates_list.html', context)

@login_required(login_url='login')
def group_detail_view(request, group_id):
    """Display details of a specific contact group"""
    group = get_object_or_404(ContactGroup, id=group_id, user=request.user)
    contacts = group.contact_set.all().order_by('email')
    
    # Get statistics
    total_contacts = contacts.count()
    active_contacts = contacts.filter(is_active=True).count()
    
    context = {
        'group': group,
        'contacts': contacts,
        'total_contacts': total_contacts,
        'active_contacts': active_contacts,
    }
    
    return render(request, 'group_detail.html', context)

@login_required(login_url='login')
def template_detail_view(request, template_id):
    """Display details of a specific email template"""
    template = get_object_or_404(EmailTemplate, id=template_id, user=request.user)
    
    context = {
        'template': template,
    }
    
    return render(request, 'template_detail.html', context)

@login_required(login_url='login')
def remove_contact_from_group(request, group_id, contact_id):
    """Remove a contact from a group"""
    group = get_object_or_404(ContactGroup, id=group_id, user=request.user)
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    # Check if the contact is actually in this group
    if contact.group == group:
        contact.group = None
        contact.save()
        messages.success(request, f'{contact.email} has been removed from "{group.name}"')
    else:
        messages.error(request, 'This contact is not in this group.')
    
    return redirect('group_detail', group_id=group_id)

@login_required(login_url='login')
def delete_contact_view(request, contact_id):
    """Delete a contact permanently"""
    contact = get_object_or_404(Contact, id=contact_id, user=request.user)
    
    if request.method == 'POST':
        email = contact.email
        contact.delete()
        messages.success(request, f'Contact "{email}" has been permanently deleted.')
        return redirect('contacts_list')
    
    # If GET request, show confirmation (though we'll use modal)
    return redirect('contacts_list')

@login_required(login_url='login')
def delete_group_view(request, group_id):
    """Delete a contact group permanently"""
    group = get_object_or_404(ContactGroup, id=group_id, user=request.user)
    
    if request.method == 'POST':
        group_name = group.name
        contact_count = group.contact_set.count()
        
        # Delete the group (contacts won't be deleted, just unlinked due to SET_NULL)
        group.delete()
        
        messages.success(request, f'Group "{group_name}" has been permanently deleted. {contact_count} contact(s) unlinked from this group.')
        return redirect('groups_list')
    
    # If GET request, show confirmation (though we'll use modal)
    return redirect('groups_list')
