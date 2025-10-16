"""
Management command to send an email campaign
"""
from django.core.management.base import BaseCommand
from mailer.models import EmailCampaign
from mailer.email_utils import send_campaign_emails


class Command(BaseCommand):
    help = 'Send an email campaign by ID'

    def add_arguments(self, parser):
        parser.add_argument(
            'campaign_id',
            type=int,
            help='ID of the campaign to send',
        )
        parser.add_argument(
            '--individual',
            action='store_true',
            help='Send individual emails instead of BCC',
        )

    def handle(self, *args, **options):
        campaign_id = options['campaign_id']
        send_individually = options['individual']
        
        try:
            campaign = EmailCampaign.objects.get(id=campaign_id)
        except EmailCampaign.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Campaign with ID {campaign_id} not found'))
            return
        
        self.stdout.write(self.style.WARNING(f'Sending campaign: {campaign.name}'))
        self.stdout.write(f'Subject: {campaign.subject}')
        self.stdout.write(f'From: {campaign.from_email}')
        
        total_recipients = campaign.get_total_recipients()
        self.stdout.write(f'Recipients: {total_recipients}')
        
        if send_individually:
            self.stdout.write('Mode: Individual emails (personalized)')
        else:
            self.stdout.write('Mode: BCC (bulk)')
        
        self.stdout.write('')
        
        # Confirm before sending
        confirm = input('Do you want to proceed? (yes/no): ')
        if confirm.lower() not in ['yes', 'y']:
            self.stdout.write(self.style.WARNING('Campaign sending cancelled'))
            return
        
        self.stdout.write(self.style.WARNING('Sending emails...'))
        
        # Send the campaign
        result = send_campaign_emails(campaign, send_individually=send_individually)
        
        if result['success']:
            self.stdout.write(self.style.SUCCESS(f"✓ {result['message']}"))
            self.stdout.write(f"Sent: {result['sent']}")
            self.stdout.write(f"Failed: {result['failed']}")
        else:
            self.stdout.write(self.style.ERROR(f"✗ {result['message']}"))
            self.stdout.write(f"Sent: {result['sent']}")
            self.stdout.write(f"Failed: {result['failed']}")
