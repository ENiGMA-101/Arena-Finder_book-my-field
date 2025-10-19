# Run this as a standalone script or in Django shell

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile

def make_user_field_owner(username):
    try:
        user = User.objects.get(username=username)
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'age': 18,
                'gender': 'Male',
                'mobile': '',
                'address': '',
                'emergency_contact': '',
                'is_field_owner': False
            }
        )
        
        profile.is_field_owner = True
        profile.save()
        
        print(f"✅ SUCCESS: {username} is now a field owner!")
        print(f"Profile created: {created}")
        print(f"Is field owner: {profile.is_field_owner}")
        
    except User.DoesNotExist:
        print(f"❌ ERROR: User '{username}' not found!")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    # Make ENiGMA-101 a field owner
    make_user_field_owner('ENiGMA-101')