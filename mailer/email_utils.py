"""
Email sending utilities for bulk email campaigns
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import EmailLog, Contact


def send_campaign_emails(campaign):
    """
    Send emails for a campaign to all recipients using BCC
    
    Args:
        campaign: EmailCampaign instance
    
    Returns:
        dict: Statistics about sent emails
    """
    # Get all recipients
    recipients = get_campaign_recipients(campaign)
    
    if not recipients:
        return {
            'success': False,
            'message': 'No recipients found',
            'sent': 0,
            'failed': 0,
        }
    
    # Update campaign status
    campaign.status = 'sending'
    campaign.started_at = timezone.now()
    campaign.save()
    
    # Prepare email details
    from_email = campaign.from_email
    if campaign.from_name:
        from_email = f"{campaign.from_name} <{campaign.from_email}>"
    
    reply_to = [campaign.reply_to] if campaign.reply_to else None
    
    # Collect all recipient emails
    recipient_emails = [contact.email for contact in recipients]
    
    # Send email using BCC (all recipients in one email)
    try:
        # Create email message
        msg = EmailMultiAlternatives(
            subject=campaign.subject,
            body=campaign.text_content or strip_html_tags(campaign.html_content),
            from_email=from_email,
            to=[from_email],  # Send to sender (required)
            bcc=recipient_emails,  # All recipients in BCC
            reply_to=reply_to,
        )
        
        # Attach HTML content
        if campaign.html_content:
            msg.attach_alternative(campaign.html_content, "text/html")
        
        # Send the email
        msg.send(fail_silently=False)
        
        # Create email logs for all recipients
        logs_created = 0
        for contact in recipients:
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'sent',
                    'sent_at': timezone.now(),
                }
            )
            logs_created += 1
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        return {
            'success': True,
            'message': f'Successfully sent to {logs_created} recipients',
            'sent': logs_created,
            'failed': 0,
        }
        
    except Exception as e:
        # Log the failure
        for contact in recipients:
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'failed',
                    'error_message': str(e),
                }
            )
        
        # Update campaign status
        campaign.status = 'failed'
        campaign.save()
        
        return {
            'success': False,
            'message': f'Failed to send emails: {str(e)}',
            'sent': 0,
            'failed': len(recipients),
        }


def get_campaign_recipients(campaign):
    """
    Get all unique recipients for a campaign
    
    Args:
        campaign: EmailCampaign instance
    
    Returns:
        QuerySet: Unique active contacts
    """
    # Get contacts from groups
    group_contacts = Contact.objects.filter(
        group__in=campaign.contact_groups.all(),
        is_active=True
    )
    
    # Get individual contacts
    individual_contacts = campaign.individual_contacts.filter(is_active=True)
    
    # Combine and get unique contacts
    all_contacts = (group_contacts | individual_contacts).distinct()
    
    return all_contacts


def strip_html_tags(html_content):
    """
    Strip HTML tags to create plain text version
    
    Args:
        html_content: str, HTML content
    
    Returns:
        str: Plain text content
    """
    import re
    # Remove HTML tags
    text = re.sub('<[^<]+?>', '', html_content)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def import_contacts_from_csv(contacts_data, user):
    """
    Import contacts from CSV data
    
    Args:
        contacts_data: list of dicts with contact information
        user: User instance
    
    Returns:
        dict: Statistics about imported contacts
    """
    imported = 0
    skipped = 0
    errors = []
    
    for data in contacts_data:
        try:
            # Check if contact already exists
            contact, created = Contact.objects.get_or_create(
                user=user,
                email=data['email'],
                defaults={
                    'first_name': data.get('first_name', ''),
                    'last_name': data.get('last_name', ''),
                    'group': data.get('group'),
                }
            )
            
            if created:
                imported += 1
            else:
                skipped += 1
                
        except Exception as e:
            errors.append(f"Error importing {data['email']}: {str(e)}")
    
    return {
        'imported': imported,
        'skipped': skipped,
        'total': imported + skipped,
        'errors': errors,
    }
