from django.core.management.base import BaseCommand
from twilio.rest import Client

# Twilio configuration (replace with your credentials)
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = 'your_twilio_phone_number'

class Command(BaseCommand):
    help = 'Send an example low stock alert SMS'

    def handle(self, *args, **kwargs):
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = "Alert: The stock for Example Product is low (5 remaining). Please restock soon."
        try:
            client.messages.create(
                body=message,
                from_=TWILIO_PHONE_NUMBER,
                to='+919951518580'  # Replace with the desired phone number
            )
            self.stdout.write(self.style.SUCCESS('Example SMS sent successfully to +919951518580'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed to send SMS: {e}"))
