"""
Management command to test email sending configuration
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Test email sending configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Email address to send test email to',
            default=settings.EMAIL_HOST_USER,
        )

    def handle(self, *args, **options):
        to_email = options['to']
        
        self.stdout.write(self.style.WARNING(f'Testing email configuration...'))
        self.stdout.write(f'From: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'To: {to_email}')
        self.stdout.write(f'SMTP Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
        
        try:
            send_mail(
                subject='BulkMailer Test Email',
                message='This is a test email from BulkMailer. If you received this, your email configuration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            
            self.stdout.write(self.style.SUCCESS(f'✓ Test email sent successfully to {to_email}'))
            self.stdout.write(self.style.SUCCESS('Email configuration is working!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to send test email'))
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
            self.stdout.write('')
            self.stdout.write('Common issues:')
            self.stdout.write('1. Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py')
            self.stdout.write('2. For Gmail, make sure you are using an App Password')
            self.stdout.write('3. Check if your SMTP port and host are correct')
            self.stdout.write('4. Verify EMAIL_USE_TLS setting')
