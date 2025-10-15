from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import EmailCampaignForm, CSVImportForm, ContactGroupForm
from .models import EmailCampaign
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
