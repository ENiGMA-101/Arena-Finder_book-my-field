from django.db import models
from django.contrib.auth.models import User
from fields.models import Field, FieldTimeSlot
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Booking(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    booking_date = models.DateField()
    time_slot = models.ForeignKey(FieldTimeSlot, on_delete=models.CASCADE)
    players_count = models.PositiveIntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    special_requirements = models.TextField(blank=True)
    emergency_contact_visible = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.field.name} - {self.booking_date}"

    class Meta:
        unique_together = ('field', 'booking_date', 'time_slot')


class Payment(models.Model):
    PAYMENT_METHODS = (
        ('bkash', 'bKash'),
        ('nagad', 'Nagad'),
        ('upay', 'Upay'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    mobile_number = models.CharField(max_length=15)
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.user.username} - {self.transaction_id}"

    @staticmethod
    def get_payment_method_details():
        """Get payment method configuration"""
        return {
            'bkash': {'name': 'bKash', 'color': '#E2136E'},
            'nagad': {'name': 'Nagad', 'color': '#F7941D'},
            'upay': {'name': 'Upay', 'color': '#00A651'}
        }

    @staticmethod
    def validate_mobile(mobile):
        """Validate Bangladeshi mobile number"""
        if not mobile:
            return False
        mobile = mobile.replace(' ', '').replace('-', '')
        return len(mobile) == 11 and mobile.startswith('01') and mobile.isdigit()

    @staticmethod
    def validate_pin(pin):
        """Validate 4-digit PIN"""
        return pin and len(pin) == 4 and pin.isdigit()

    @staticmethod
    def generate_transaction_id(payment_method):
        """Generate unique transaction ID"""
        prefixes = {'bkash': 'BK', 'nagad': 'NG', 'upay': 'UP'}
        prefix = prefixes.get(payment_method, 'TXN')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{prefix}{timestamp}{hash(timestamp) % 1000:03d}"

    @classmethod
    def process_payment(cls, booking, payment_method, mobile, pin):
        """
        Process payment for a booking
        Returns: {'success': bool, 'message': str, 'transaction_id': str, ...}
        """
        # Validate inputs
        if not cls.validate_mobile(mobile):
            return {'success': False, 'message': 'Invalid mobile number format'}

        if not cls.validate_pin(pin):
            return {'success': False, 'message': 'PIN must be 4 digits'}

        payment_methods = cls.get_payment_method_details()
        if payment_method not in payment_methods:
            return {'success': False, 'message': 'Invalid payment method'}

        try:
            transaction_id = cls.generate_transaction_id(payment_method)

            # Create or update payment
            payment, created = cls.objects.get_or_create(
                booking=booking,
                defaults={
                    'payment_method': payment_method,
                    'mobile_number': mobile,
                    'transaction_id': transaction_id,
                    'amount': booking.total_cost,
                    'status': 'Completed'
                }
            )

            # Update booking status
            booking.status = 'Confirmed'
            booking.save()

            return {
                'success': True,
                'transaction_id': transaction_id,
                'payment_method': payment_methods[payment_method]['name'],
                'amount': booking.total_cost,
                'booking': booking
            }

        except Exception as e:
            logger.error(f"Payment processing error: {str(e)}")
            return {'success': False, 'message': 'Payment processing failed'}


class TeamFormation(models.Model):
    SKILL_LEVELS = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    looking_for_players = models.BooleanField(default=False)
    required_players = models.PositiveIntegerField(default=0)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS, blank=True)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking.user.username}'s Team - {self.booking.field.name}"


class JoinRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    team_formation = models.ForeignKey(TeamFormation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} -> {self.team_formation.booking.user.username}'s team"

    class Meta:
        unique_together = ('team_formation', 'user')