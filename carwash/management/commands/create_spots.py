from django.core.management.base import BaseCommand
from carwash.models import WashingSpot

class Command(BaseCommand):
    help = 'Creates washing spots for all services'

    def handle(self, *args, **kwargs):
        services = ['express', 'full', 'detailing']
        
        for service in services:
            for number in range(1, 11):
                WashingSpot.objects.get_or_create(
                    number=number,
                    service=service,
                    defaults={'is_active': True}
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully created washing spots')) 