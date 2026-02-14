from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile, PatientProfile, DoctorProfile, LabTechnicianProfile, AdminProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing profiles for existing users'

    def handle(self, *args, **kwargs):
        users = User.objects.all()
        created_count = 0
        
        for user in users:
            # Create UserProfile if missing
            if not hasattr(user, 'profile'):
                UserProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created UserProfile for {user.email}'))
                created_count += 1
            
            # Create role-specific profile based on user_type
            if user.user_type == 'patient' and not hasattr(user, 'patient_profile'):
                PatientProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created PatientProfile for {user.email}'))
                created_count += 1
                
            elif user.user_type == 'doctor' and not hasattr(user, 'doctor_profile'):
                DoctorProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created DoctorProfile for {user.email}'))
                created_count += 1
                
            elif user.user_type == 'staff' and not hasattr(user, 'lab_technician_profile'):
                LabTechnicianProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created LabTechnicianProfile for {user.email}'))
                created_count += 1
                
            elif user.user_type == 'admin' and not hasattr(user, 'admin_profile'):
                AdminProfile.objects.create(user=user)
                self.stdout.write(self.style.SUCCESS(f'Created AdminProfile for {user.email}'))
                created_count += 1
        
        if created_count == 0:
            self.stdout.write(self.style.WARNING('No missing profiles found.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully created {created_count} profiles!'))