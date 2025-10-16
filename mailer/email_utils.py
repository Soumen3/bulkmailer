"""
Email sending utilities for bulk email campaigns
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from .models import EmailLog, Contact


def send_campaign_emails(campaign, send_individually=False):
    """
    Send emails for a campaign to all recipients
    
    Args:
        campaign: EmailCampaign instance
        send_individually: bool, if True sends individual emails, if False uses BCC (default)
    
    Returns:
        dict: Statistics about sent emails
    """
    # Get all main recipients (To field)
    recipients = get_campaign_recipients(campaign)
    
    # Parse CC and BCC - combine manual emails and groups
    cc_list = []
    # Add manual CC emails
    if campaign.cc:
        cc_list.extend([email.strip() for email in campaign.cc.split(',') if email.strip()])
    # Add CC group emails
    for group in campaign.cc_groups.all():
        cc_contacts = Contact.objects.filter(group=group, is_active=True)
        cc_list.extend([contact.email for contact in cc_contacts])
    
    bcc_list = []
    # Add manual BCC emails
    if campaign.bcc:
        bcc_list.extend([email.strip() for email in campaign.bcc.split(',') if email.strip()])
    # Add BCC group emails
    for group in campaign.bcc_groups.all():
        bcc_contacts = Contact.objects.filter(group=group, is_active=True)
        bcc_list.extend([contact.email for contact in bcc_contacts])
    
    # Remove duplicates while preserving order
    cc_list = list(dict.fromkeys(cc_list))
    bcc_list = list(dict.fromkeys(bcc_list))
    
    # Check if there are any recipients at all
    if not recipients and not cc_list and not bcc_list:
        return {
            'success': False,
            'message': 'No recipients found (no To, CC, or BCC recipients)',
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
    
    # If there are no main recipients, send one email with only CC/BCC
    if not recipients:
        return send_cc_bcc_only_email(campaign, from_email, reply_to, cc_list, bcc_list)
    
    if send_individually:
        # Send individual emails to each recipient
        return send_individual_emails(campaign, recipients, from_email, reply_to, cc_list, bcc_list)
    else:
        # Send one email with all recipients in BCC
        return send_bcc_email(campaign, recipients, from_email, reply_to, cc_list, bcc_list)


def send_cc_bcc_only_email(campaign, from_email, reply_to, cc_list, bcc_list):
    """
    Send one email with only CC/BCC recipients (no main To recipients)
    
    Args:
        campaign: EmailCampaign instance
        from_email: str, formatted from email
        reply_to: list or None
        cc_list: list of CC email addresses
        bcc_list: list of BCC email addresses
    
    Returns:
        dict: Statistics about sent emails
    """
    try:
        # Create email message with no "To" field, only CC and BCC
        msg = EmailMultiAlternatives(
            subject=campaign.subject,
            body=campaign.text_content or strip_html_tags(campaign.html_content),
            from_email=from_email,
            to=[],  # Empty To field
            cc=cc_list or [],
            bcc=bcc_list or [],
            reply_to=reply_to,
        )
        
        # Attach HTML content
        if campaign.html_content:
            msg.attach_alternative(campaign.html_content, "text/html")
        
        # Send the email
        msg.send(fail_silently=False)
        
        # Calculate total recipients
        total_recipients = len(cc_list) + len(bcc_list)
        
        # Update campaign status
        campaign.status = 'sent'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        return {
            'success': True,
            'message': f'Successfully sent to {len(cc_list)} CC and {len(bcc_list)} BCC recipients',
            'sent': total_recipients,
            'failed': 0,
        }
        
    except Exception as e:
        # Update campaign status
        campaign.status = 'failed'
        campaign.completed_at = timezone.now()
        campaign.save()
        
        return {
            'success': False,
            'message': f'Failed to send: {str(e)}',
            'sent': 0,
            'failed': len(cc_list) + len(bcc_list),
        }


def send_bcc_email(campaign, recipients, from_email, reply_to, cc_list=None, bcc_list=None):
    """
    Send individual emails efficiently (each recipient sees their own email in To field)
    
    Note: Despite the function name, this now sends individual emails
    to ensure each recipient sees their own email in the "To" field.
    It's more efficient than the personalized individual sending.
    
    Args:
        campaign: EmailCampaign instance
        recipients: QuerySet of Contact objects
        from_email: str, formatted from email
        reply_to: list or None
        cc_list: list of CC email addresses
        bcc_list: list of BCC email addresses
    
    Returns:
        dict: Statistics about sent emails
    """
    sent_count = 0
    failed_count = 0
    
    for contact in recipients:
        try:
            # Create email message for this specific recipient
            msg = EmailMultiAlternatives(
                subject=campaign.subject,
                body=campaign.text_content or strip_html_tags(campaign.html_content),
                from_email=from_email,
                to=[contact.email],  # Each recipient in their own "To" field
                cc=cc_list or [],
                bcc=bcc_list or [],
                reply_to=reply_to,
            )
            
            # Attach HTML content
            if campaign.html_content:
                msg.attach_alternative(campaign.html_content, "text/html")
            
            # Send the email
            msg.send(fail_silently=False)
            
            # Create successful email log
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'sent',
                    'sent_at': timezone.now(),
                }
            )
            sent_count += 1
            
        except Exception as e:
            # Log the failure for this contact
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'failed',
                    'error_message': str(e),
                }
            )
            failed_count += 1
    
    # Update campaign status
    if failed_count == 0:
        campaign.status = 'sent'
    elif sent_count == 0:
        campaign.status = 'failed'
    else:
        campaign.status = 'sent'  # Partially sent
    
    campaign.completed_at = timezone.now()
    campaign.save()
    
    return {
        'success': sent_count > 0,
        'message': f'Successfully sent to {sent_count} recipients, {failed_count} failed',
        'sent': sent_count,
        'failed': failed_count,
    }


def send_individual_emails(campaign, recipients, from_email, reply_to, cc_list=None, bcc_list=None):
    """
    Send individual emails to each recipient
    
    Args:
        campaign: EmailCampaign instance
        recipients: QuerySet of Contact objects
        from_email: str, formatted from email
        reply_to: list or None
        cc_list: list of CC email addresses
        bcc_list: list of BCC email addresses
    
    Returns:
        dict: Statistics about sent emails
    """
    sent_count = 0
    failed_count = 0
    
    for contact in recipients:
        try:
            # Personalize content (can be enhanced with template variables)
            html_content = campaign.html_content
            text_content = campaign.text_content or strip_html_tags(campaign.html_content)
            
            # Replace common placeholders
            replacements = {
                '{{first_name}}': contact.first_name or '',
                '{{last_name}}': contact.last_name or '',
                '{{full_name}}': contact.get_full_name(),
                '{{email}}': contact.email,
            }
            
            for placeholder, value in replacements.items():
                html_content = html_content.replace(placeholder, value)
                text_content = text_content.replace(placeholder, value)
            
            # Create email message
            msg = EmailMultiAlternatives(
                subject=campaign.subject,
                body=text_content,
                from_email=from_email,
                to=[contact.email],
                cc=cc_list or [],
                bcc=bcc_list or [],
                reply_to=reply_to,
            )
            
            # Attach HTML content
            if html_content:
                msg.attach_alternative(html_content, "text/html")
            
            # Send the email
            msg.send(fail_silently=False)
            
            # Create successful email log
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'sent',
                    'sent_at': timezone.now(),
                }
            )
            sent_count += 1
            
        except Exception as e:
            # Log the failure for this contact
            EmailLog.objects.update_or_create(
                campaign=campaign,
                contact=contact,
                defaults={
                    'status': 'failed',
                    'error_message': str(e),
                }
            )
            failed_count += 1
    
    # Update campaign status
    if failed_count == 0:
        campaign.status = 'sent'
    elif sent_count == 0:
        campaign.status = 'failed'
    else:
        campaign.status = 'sent'  # Partially sent
    
    campaign.completed_at = timezone.now()
    campaign.save()
    
    return {
        'success': sent_count > 0,
        'message': f'Sent to {sent_count} recipients, {failed_count} failed',
        'sent': sent_count,
        'failed': failed_count,
    }


def get_campaign_recipients(campaign):
    """
    Get all unique recipients for a campaign
    
    Args:
        campaign: EmailCampaign instance
    
    Returns:
        QuerySet: Unique active contacts
    """
    # Get contact IDs from groups
    group_contact_ids = Contact.objects.filter(
        group__in=campaign.contact_groups.all(),
        is_active=True
    ).values_list('id', flat=True)
    
    # Get individual contact IDs
    individual_contact_ids = campaign.individual_contacts.filter(
        is_active=True
    ).values_list('id', flat=True)
    
    # Combine and get unique contact IDs
    all_contact_ids = set(group_contact_ids) | set(individual_contact_ids)
    
    # Return queryset of unique contacts
    return Contact.objects.filter(id__in=all_contact_ids)


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
