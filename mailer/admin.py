from django.contrib import admin
from .models import ContactGroup, Contact, EmailCampaign, EmailLog, EmailTemplate


@admin.register(ContactGroup)
class ContactGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'get_contact_count', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'group', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'group', 'created_at', 'user']
    search_fields = ['email', 'first_name', 'last_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'status', 'get_total_recipients', 'get_sent_count', 'get_open_rate', 'created_at']
    list_filter = ['status', 'created_at', 'user']
    search_fields = ['name', 'subject']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at']
    filter_horizontal = ['contact_groups', 'individual_contacts']
    fieldsets = (
        ('Campaign Info', {
            'fields': ('user', 'name', 'status')
        }),
        ('Email Settings', {
            'fields': ('subject', 'from_email', 'from_name', 'reply_to')
        }),
        ('Content', {
            'fields': ('html_content', 'text_content')
        }),
        ('Recipients', {
            'fields': ('contact_groups', 'individual_contacts')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'started_at', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ['campaign', 'contact', 'status', 'opened', 'clicked', 'sent_at', 'created_at']
    list_filter = ['status', 'opened', 'clicked', 'created_at']
    search_fields = ['contact__email', 'campaign__name']
    readonly_fields = ['created_at', 'sent_at', 'opened_at', 'clicked_at']


@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['name', 'description', 'subject']
    readonly_fields = ['created_at', 'updated_at']
