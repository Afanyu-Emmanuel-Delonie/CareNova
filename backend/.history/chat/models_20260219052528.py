import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatGroup(models.Model):
    """Support groups for specific conditions (e.g., 'Heart Health')."""
    name = models.CharField(max_length=255)
    description = models.TextField()
    # Image for the group icon
    icon = models.ImageField(upload_to='chat_groups/', null=True, blank=True)
    members = models.ManyToManyField(User, related_name='medical_groups')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    """Base message logic for both group and private chats."""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # If null, it's a private message. If set, it's a group message.
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='messages')
    
    # For private chats
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_private_messages')
    
    # Attachment for prescriptions or reports
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']