from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import uuid
import random
from datetime import timedelta
from django.conf import settings

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError("uaser must have an email address")
        
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_supperuser", True)
        extra_fields.setdefault("role", "ADMIN")
        
        return self.create_user(email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ("PATIENT", "Patient"),
        ("DOCTOR", "Doctor"),
        ("LAB_TECH", "Lab Technician"),
        ("ADMIN", "Admin"),
    )
    
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return self.email

# this section will cover the patients profile 
class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    
    blood_group = models.CharField(max_length=5, blank=True)
    allegies = models.TextField(blank=True)
    chronic_diseases = models.TextField(blank=True)
    
    def __str__(self):
        return f"Patient: {self.user.email}"
    
# this section covers the doctors profile 
class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100)
    years_of_experience = models.IntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Doctor: {self.user.email}"
    
class LabTechnicianProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)

    lab_name = models.CharField(max_length=255)
    certification_id = models.CharField(max_length=100)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"Lab Tech: {self.user.email}"
    
class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20)

    def __str__(self):
        return f"Admin: {self.user.email}"

# this section will cover the OTP for user registration, forgot password and others 
class OTP(models.Model):
    OTP_TYPE_CHOICES = (
        ("EMAIL_VERIFICATION", "Email Verification"),
        ("PASSWORD_RESET", "Password Reset"),
        ("LOGIN_OTP", "Login OTP"),
    )
    
    id = 
