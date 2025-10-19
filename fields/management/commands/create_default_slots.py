from django.core.management.base import BaseCommand
from fields.models import Field, FieldTimeSlot
from datetime import time


class Command(BaseCommand):
    help = 'Create default 90-minute time slots for all fields'

    def handle(self, *args, **options):
        # Default 90-minute time slots from 6 AM to 11 PM
        default_slots = [
            (time(6, 0), time(7, 30)),   # 6:00 AM - 7:30 AM
            (time(7, 30), time(9, 0)),   # 7:30 AM - 9:00 AM
            (time(9, 0), time(10, 30)),  # 9:00 AM - 10:30 AM
            (time(10, 30), time(12, 0)), # 10:30 AM - 12:00 PM
            (time(12, 0), time(13, 30)), # 12:00 PM - 1:30 PM
            (time(13, 30), time(15, 0)), # 1:30 PM - 3:00 PM
            (time(15, 0), time(16, 30)), # 3:00 PM - 4:30 PM
            (time(16, 30), time(18, 0)), # 4:30 PM - 6:00 PM
            (time(18, 0), time(19, 30)), # 6:00 PM - 7:30 PM
            (time(19, 30), time(21, 0)), # 7:30 PM - 9:00 PM
            (time(21, 0), time(22, 30)), # 9:00 PM - 10:30 PM
        ]

        fields = Field.objects.all()
        
        for field in fields:
            self.stdout.write(f"Creating time slots for field: {field.name}")
            
            for start_time, end_time in default_slots:
                # Check if time slot already exists
                if not FieldTimeSlot.objects.filter(
                    field=field,
                    start_time=start_time,
                    end_time=end_time
                ).exists():
                    FieldTimeSlot.objects.create(
                        field=field,
                        start_time=start_time,
                        end_time=end_time,
                        is_available=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created time slot: {start_time} - {end_time} for {field.name}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS('Successfully created time slots for all fields!')
        )