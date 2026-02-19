from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import ChatGroup, Message, UserPresence, BlockedUser, PatientComplaint


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.profile.get_full_name')
    is_me = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'timestamp', 'is_read', 'attachment', 'is_me']

    @extend_schema_field(bool)
    def get_is_me(self, obj):
        return obj.sender == self.context['request'].user


class ChatGroupSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(source='members.count', read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatGroup
        fields = ['id', 'name', 'description', 'icon', 'member_count', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at']


class UserPresenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPresence
        fields = ['status', 'last_seen']
        read_only_fields = ['last_seen']


class BlockedUserSerializer(serializers.ModelSerializer):
    blocked_user_name = serializers.SerializerMethodField()

    class Meta:
        model = BlockedUser
        fields = ['id', 'blocked_user', 'blocked_user_name', 'reason', 'created_at']
        read_only_fields = ['created_at']

    @extend_schema_field(str)
    def get_blocked_user_name(self, obj):
        profile = obj.blocked_user.profile
        return f"{profile.first_name} {profile.last_name}"


class PatientComplaintSerializer(serializers.ModelSerializer):
    reported_by_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = PatientComplaint
        fields = [
            'id', 'reported_by', 'reported_by_name',
            'patient', 'patient_name',
            'description', 'status', 'admin_notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['reported_by', 'status', 'admin_notes', 'created_at', 'updated_at']

    @extend_schema_field(str)
    def get_reported_by_name(self, obj):
        profile = obj.reported_by.profile
        return f"{profile.first_name} {profile.last_name}"

    @extend_schema_field(str)
    def get_patient_name(self, obj):
        profile = obj.patient.profile
        return f"{profile.first_name} {profile.last_name}"