from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier
    instead of username.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model for CareNova application.
    Uses email as the primary identifier instead of username.
    """
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    # Basic Information
    email = models.EmailField(
        verbose_name='Email Address',
        max_length=255,
        unique=True,
        db_index=True,
        help_text='Required. A valid email address.'
    )
    first_name = models.CharField(
        verbose_name='First Name',
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        verbose_name='Last Name',
        max_length=150,
        blank=True
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    # Profile Information
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text='User date of birth'
    )
    address = models.TextField(
        blank=True,
        help_text='User address'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        blank=True,
        null=True,
        help_text='User profile picture'
    )
    
    # User Type/Role (for healthcare system)
    USER_TYPE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
        ('staff', 'Staff'),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='patient',
        help_text='Type of user in the system'
    )
    
    # Permissions and Status
    is_active = models.BooleanField(
        verbose_name='Active Status',
        default=True,
        help_text='Designates whether this user should be treated as active. '
                  'Unselect this instead of deleting accounts.'
    )
    is_staff = models.BooleanField(
        verbose_name='Staff Status',
        default=False,
        help_text='Designates whether the user can log into the admin site.'
    )
    is_verified = models.BooleanField(
        verbose_name='Email Verified',
        default=False,
        help_text='Designates whether the user has verified their email address.'
    )
    
    # Timestamps
    date_joined = models.DateTimeField(
        verbose_name='Date Joined',
        default=timezone.now,
        help_text='Date and time when the user registered'
    )
    last_login = models.DateTimeField(
        verbose_name='Last Login',
        blank=True,
        null=True,
        help_text='Last time the user logged in'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='Last time the user information was updated'
    )
    
    # Manager
    objects = UserManager()
    
    # Settings for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required by default
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name if full_name else self.email
    
    def get_short_name(self):
        """
        Return the short name for the user.
        """
        return self.first_name if self.first_name else self.email.split('@')[0]
    
    @property
    def age(self):
        """
        Calculate and return the user's age based on date_of_birth.
        """
        if self.date_of_birth:
            today = timezone.now().date()
            age = today.year - self.date_of_birth.year
            if today.month < self.date_of_birth.month or \
               (today.month == self.date_of_birth.month and today.day < self.date_of_birth.day):
                age -= 1
            return age
        return None


class UserProfile(models.Model):
    """
    Extended profile information for users.
    This is separate to keep the User model clean and allow for optional extended info.
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        primary_key=True
    )
    
    # Additional Health Information (for patients)
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        help_text='Blood group of the patient'
    )
    emergency_contact_name = models.CharField(
        max_length=255,
        blank=True,
        help_text='Name of emergency contact person'
    )
    emergency_contact_phone = models.CharField(
        max_length=17,
        blank=True,
        help_text='Phone number of emergency contact'
    )
    emergency_contact_relationship = models.CharField(
        max_length=100,
        blank=True,
        help_text='Relationship with emergency contact'
    )
    
    # Professional Information (for doctors/nurses/staff)
    license_number = models.CharField(
        max_length=100,
        blank=True,
        unique=True,
        null=True,
        help_text='Professional license number'
    )
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Medical specialization (for doctors)'
    )
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text='Department or unit'
    )
    years_of_experience = models.PositiveIntegerField(
        blank=True,
        null=True,
        help_text='Years of professional experience'
    )
    
    # Additional Fields
    bio = models.TextField(
        blank=True,
        help_text='Short biography or description'
    )
    
    # Settings
    notifications_enabled = models.BooleanField(
        default=True,
        help_text='Receive email notifications'
    )
    sms_notifications_enabled = models.BooleanField(
        default=False,
        help_text='Receive SMS notifications'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f'Profile of {self.user.email}'


class PatientProfile(models.Model):
    """
    Extended profile specifically for patients.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        limit_choices_to={'user_type': 'patient'}
    )
    
    # Medical Information
    blood_group = models.CharField(
        max_length=5,
        blank=True,
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ]
    )
    allergies = models.TextField(blank=True, help_text='List of known allergies')
    chronic_conditions = models.TextField(blank=True, help_text='Chronic medical conditions')
    current_medications = models.TextField(blank=True, help_text='Current medications')
    
    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, blank=True)
    emergency_contact_phone = models.CharField(max_length=17, blank=True)
    emergency_contact_relationship = models.CharField(max_length=100, blank=True)
    
    # Insurance
    insurance_provider = models.CharField(max_length=255, blank=True)
    insurance_policy_number = models.CharField(max_length=100, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'patient_profiles'
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'
    
    def __str__(self):
        return f'Patient Profile - {self.user.get_full_name()}'


class DoctorProfile(models.Model):
    """
    Extended profile specifically for doctors.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        limit_choices_to={'user_type': 'doctor'}
    )
    
    # Professional Information
    license_number = models.CharField(max_length=100, unique=True)
    specialization = models.CharField(max_length=200)
    sub_specialization = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Education
    medical_school = models.CharField(max_length=255, blank=True)
    graduation_year = models.PositiveIntegerField(blank=True, null=True)
    certifications = models.TextField(blank=True, help_text='Professional certifications')
    
    # Work Details
    department = models.CharField(max_length=200, blank=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    available_for_consultation = models.BooleanField(default=True)
    
    # Additional
    bio = models.TextField(blank=True, help_text='Professional biography')
    languages_spoken = models.CharField(max_length=255, blank=True, help_text='Comma-separated languages')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'doctor_profiles'
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'
    
    def __str__(self):
        return f'Dr. {self.user.get_full_name()} - {self.specialization}'


class LabTechnicianProfile(models.Model):
    """
    Extended profile specifically for lab technicians.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='lab_technician_profile',
        limit_choices_to={'user_type': 'staff'}
    )
    
    # Professional Information
    license_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    certifications = models.TextField(blank=True, help_text='Professional certifications')
    specialization = models.CharField(
        max_length=200,
        blank=True,
        help_text='Lab specialization (e.g., Hematology, Microbiology)'
    )
    years_of_experience = models.PositiveIntegerField(default=0)
    
    # Work Details
    department = models.CharField(max_length=200, default='Laboratory')
    shift_timing = models.CharField(
        max_length=50,
        blank=True,
        help_text='e.g., Morning, Evening, Night'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lab_technician_profiles'
        verbose_name = 'Lab Technician Profile'
        verbose_name_plural = 'Lab Technician Profiles'
    
    def __str__(self):
        return f'Lab Tech - {self.user.get_full_name()}'


class AdminProfile(models.Model):
    """
    Extended profile specifically for admin users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='admin_profile',
        limit_choices_to={'user_type': 'admin'}
    )
    
    # Administrative Information
    employee_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    department = models.CharField(max_length=200, default='Administration')
    designation = models.CharField(max_length=200, blank=True)
    
    # Permissions
    can_manage_users = models.BooleanField(default=True)
    can_manage_appointments = models.BooleanField(default=True)
    can_manage_billing = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'admin_profiles'
        verbose_name = 'Admin Profile'
        verbose_name_plural = 'Admin Profiles'
    
    def __str__(self):
        return f'Admin - {self.user.get_full_name()}'    
