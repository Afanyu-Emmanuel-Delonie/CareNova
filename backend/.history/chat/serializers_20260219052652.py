from rest_framework import serializers
from .models import ChatGroup, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.profile.get_full_name')
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'timestamp', 'is_read', 'attachment', 'is_me']

    def get_is_me(self, obj):
        return obj.sender == self.context['request'].user

class ChatGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    
    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'description', 'icon', 'member_count']