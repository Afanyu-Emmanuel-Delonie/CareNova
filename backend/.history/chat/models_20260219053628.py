import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatGroup(models.Model):
    """Support groups for specific conditions (e.g., 'Heart Health')."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.ImageField(upload_to='chat_groups/', null=True, blank=True)
    members = models.ManyToManyField(User, related_name='medical_groups')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_groups',
        help_text="Admin user who created this group.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    """Base message logic for both group and private chats."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    group = models.ForeignKey(
        ChatGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages',
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_private_messages',
    )
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        target = f"group:{self.group}" if self.group else f"user:{self.receiver}"
        return f"{self.sender} → {target} @ {self.timestamp:%Y-%m-%d %H:%M}"


class UserPresence(models.Model):
    """Tracks whether a user is online, away, or offline."""

    class PresenceStatus(models.TextChoices):
        ONLINE = 'ONLINE', 'Online'
        AWAY = 'AWAY', 'Away'
        OFFLINE = 'OFFLINE', 'Offline'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='presence')
    status = models.CharField(
        max_length=10,
        choices=PresenceStatus.choices,
        default=PresenceStatus.OFFLINE,
    )
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} — {self.status}"


class BlockedUser(models.Model):
    """
    Records a block placed by a doctor or admin against a patient.
    Blocked patients cannot send private messages to the blocker.
    """
    blocked_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocks_issued',
        help_text="Doctor or admin who issued the block.",
    )
    blocked_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blocks_received',
        help_text="Patient who was blocked.",
    )
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['blocked_by', 'blocked_user'],
                name='unique_block_per_pair',
            )
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.blocked_by} blocked {self.blocked_user}"


class PatientComplaint(models.Model):
    """
    Allows a doctor to file a formal complaint about a patient's behaviour
    to be reviewed by an admin.
    """
    class ComplaintStatus(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        UNDER_REVIEW = 'UNDER_REVIEW', 'Under Review'
        RESOLVED = 'RESOLVED', 'Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed'

    reported_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints_filed',
        help_text="Doctor who filed the complaint.",
    )
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints_received',
        help_text="Patient being reported.",
    )
    description = models.TextField(help_text="Description of the disruptive or spammy behaviour.")
    status = models.CharField(
        max_length=15,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.OPEN,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal admin notes on resolution.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Complaint by {self.reported_by} against {self.patient} [{self.status}]"