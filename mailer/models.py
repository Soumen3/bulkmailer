from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Contact/Recipient models
class ContactGroup(models.Model):
    """Group/List of contacts for organizing recipients"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contact_groups')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'name']

    def __str__(self):
        return f"{self.name} ({self.contact_set.count()} contacts)"

    def get_contact_count(self):
        return self.contact_set.count()


class Contact(models.Model):
    """Individual email contact/recipient"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    group = models.ForeignKey(ContactGroup, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'email']

    def __str__(self):
        if self.first_name or self.last_name:
            return f"{self.first_name} {self.last_name} <{self.email}>"
        return self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


# Email Campaign models
class EmailCampaign(models.Model):
    """Email campaign/broadcast"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('paused', 'Paused'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='campaigns')
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)
    from_email = models.EmailField()
    from_name = models.CharField(max_length=100, blank=True)
    reply_to = models.EmailField(blank=True)
    cc = models.TextField(blank=True, help_text="Comma-separated email addresses for CC")
    bcc = models.TextField(blank=True, help_text="Comma-separated email addresses for BCC")
    
    # Email content
    html_content = models.TextField(blank=True, help_text="HTML version of the email")
    text_content = models.TextField(blank=True, help_text="Plain text version (optional)")
    
    # Recipients
    contact_groups = models.ManyToManyField(ContactGroup, blank=True, related_name='campaigns')
    individual_contacts = models.ManyToManyField(Contact, blank=True, related_name='campaigns')
    
    # CC and BCC as groups
    cc_groups = models.ManyToManyField(ContactGroup, blank=True, related_name='cc_campaigns')
    bcc_groups = models.ManyToManyField(ContactGroup, blank=True, related_name='bcc_campaigns')
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.status}"

    def get_total_recipients(self):
        """Calculate total number of recipients"""
        # Get all contact IDs from groups
        group_contact_ids = Contact.objects.filter(
            group__in=self.contact_groups.all(),
            is_active=True
        ).values_list('id', flat=True)
        
        # Get all individual contact IDs
        individual_contact_ids = self.individual_contacts.filter(
            is_active=True
        ).values_list('id', flat=True)
        
        # Combine and get unique contact IDs
        all_contact_ids = set(group_contact_ids) | set(individual_contact_ids)
        
        return len(all_contact_ids)

    def get_sent_count(self):
        return self.email_logs.filter(status='sent').count()

    def get_failed_count(self):
        return self.email_logs.filter(status='failed').count()

    def get_opened_count(self):
        return self.email_logs.filter(opened=True).count()

    def get_clicked_count(self):
        return self.email_logs.filter(clicked=True).count()

    def get_delivery_rate(self):
        total = self.get_total_recipients()
        if total == 0:
            return 0
        return round((self.get_sent_count() / total) * 100, 2)

    def get_open_rate(self):
        sent = self.get_sent_count()
        if sent == 0:
            return 0
        return round((self.get_opened_count() / sent) * 100, 2)

    def get_click_rate(self):
        sent = self.get_sent_count()
        if sent == 0:
            return 0
        return round((self.get_clicked_count() / sent) * 100, 2)


class EmailLog(models.Model):
    """Log of individual email sends"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sending', 'Sending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('bounced', 'Bounced'),
    ]

    campaign = models.ForeignKey(EmailCampaign, on_delete=models.CASCADE, related_name='email_logs')
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='email_logs')
    
    # Delivery status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Engagement tracking
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['campaign', 'contact']

    def __str__(self):
        return f"{self.campaign.name} -> {self.contact.email} ({self.status})"


class EmailTemplate(models.Model):
    """Reusable email templates"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=300)
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
