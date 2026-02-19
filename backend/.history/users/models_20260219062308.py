from datetime import timedelta
from django.db import models
from django.db.models import Avg
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import random

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_field):
        if not email:
            raise ValueError("User must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_field)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    class Roles(models.TextChoices):
        PATIENT = 'PATIENT', 'Patient'
        DOCTOR = 'DOCTOR', 'Doctor'
        ADMIN = 'ADMIN', 'Admin'
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.PATIENT)
    
    is_verified = models.BooleanField(default=False)  
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True) 
    is_flagged = models.BooleanField(default=False) 
    ban_reason = models.TextField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  
    
    def generate_otp(self):
        """Generates a 6-digit code and saves it to the user."""
        code = str(random.randint(100000, 999999))
        self.otp = code
        self.otp_created_at = timezone.now()
        self.save()
        return code

    def verify_otp(self, received_otp):
        """Checks if the OTP is correct and not older than 5 minutes."""
        if not self.otp or not self.otp_created_at:
            return False
        
        # Check expiration (5 minutes)
        if timezone.now() > self.otp_created_at + timedelta(minutes=5):
            self.otp = None
            self.save()
            return False
            
        if self.otp == received_otp:
            self.otp = None
            self.save()
            return True
            
        return False
    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class DoctorProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='doctor_data')
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)

    @property
    def average_rating(self):
        avg_value = self.reviews.aggregate(avg=Avg('rating'))['avg']
        return avg_value or 0
    
    def __str__(self):
        return f"Dr. {self.profile.last_name}| {self.specialization}"
    
class PatientProfile(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='patient_data')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Patient: {self.profile.first_name}"
    
 
