from django.core.management.base import BaseCommand
from fields.models import Field, FieldTimeSlot
from datetime import time


class Command(BaseCommand):
    help = 'Create default time slots for all fields'

    def handle(self, *args, **options):
        # Default time slots (you can modify these)
        default_slots = [
            (time(6, 0), time(7, 0)),   # 6:00 AM - 7:00 AM
            (time(7, 0), time(8, 0)),   # 7:00 AM - 8:00 AM
            (time(8, 0), time(9, 0)),   # 8:00 AM - 9:00 AM
            (time(9, 0), time(10, 0)),  # 9:00 AM - 10:00 AM
            (time(10, 0), time(11, 0)), # 10:00 AM - 11:00 AM
            (time(11, 0), time(12, 0)), # 11:00 AM - 12:00 PM
            (time(14, 0), time(15, 0)), # 2:00 PM - 3:00 PM
            (time(15, 0), time(16, 0)), # 3:00 PM - 4:00 PM
            (time(16, 0), time(17, 0)), # 4:00 PM - 5:00 PM
            (time(17, 0), time(18, 0)), # 5:00 PM - 6:00 PM
            (time(18, 0), time(19, 0)), # 6:00 PM - 7:00 PM
            (time(19, 0), time(20, 0)), # 7:00 PM - 8:00 PM
            (time(20, 0), time(21, 0)), # 8:00 PM - 9:00 PM
            (time(21, 0), time(22, 0)), # 9:00 PM - 10:00 PM
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