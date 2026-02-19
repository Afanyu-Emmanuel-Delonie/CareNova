from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

from .models import BlockedUser, ChatGroup, Message, PatientComplaint, UserPresence
from .serializers import (
    BlockedUserSerializer,
    ChatGroupSerializer,
    MessageSerializer,
    PatientComplaintSerializer,
    UserPresenceSerializer,
)

User = get_user_model()


# ──────────────────────────────────────────────────────────────
# Group Chat
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List all chat groups",
        description="Returns all available support chat groups with member counts.",
        responses={200: ChatGroupSerializer(many=True)},
        tags=["Chat — Groups"],
    ),
    create=extend_schema(
        summary="Create a chat group",
        description=(
            "Admin-only. Creates a new support group and automatically adds the creator as a member. "
            "The creator is recorded on the group for audit purposes."
        ),
        request=ChatGroupSerializer,
        responses={
            201: ChatGroupSerializer,
            403: OpenApiResponse(description="Only admins can create groups."),
        },
        tags=["Chat — Groups"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a chat group",
        responses={
            200: ChatGroupSerializer,
            404: OpenApiResponse(description="Group not found."),
        },
        tags=["Chat — Groups"],
    ),
    update=extend_schema(
        summary="Update a chat group",
        request=ChatGroupSerializer,
        responses={
            200: ChatGroupSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Chat — Groups"],
    ),
    partial_update=extend_schema(
        summary="Partially update a chat group",
        request=ChatGroupSerializer,
        responses={
            200: ChatGroupSerializer,
            400: OpenApiResponse(description="Validation error."),
        },
        tags=["Chat — Groups"],
    ),
    destroy=extend_schema(
        summary="Delete a chat group",
        responses={
            204: OpenApiResponse(description="Group deleted."),
            404: OpenApiResponse(description="Group not found."),
        },
        tags=["Chat — Groups"],
    ),
)
class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all().prefetch_related("members")
    serializer_class = ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        group = serializer.save(created_by=self.request.user)
        group.members.add(self.request.user)

    @extend_schema(
        summary="Join a chat group",
        description="Adds the authenticated user to the group's member list. Safe to call multiple times.",
        request=None,
        responses={
            200: OpenApiResponse(description="Joined group successfully."),
            404: OpenApiResponse(description="Group not found."),
        },
        tags=["Chat — Groups"],
    )
    @action(detail=True, methods=["post"])
    def join(self, request, pk=None):
        group = self.get_object()
        group.members.add(request.user)
        return Response({"message": "Joined group successfully."}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="List group messages",
        description=(
            "Returns all messages in this group ordered by timestamp, "
            "with sender info resolved. Includes the full message history."
        ),
        responses={200: MessageSerializer(many=True)},
        tags=["Chat — Groups"],
    )
    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        group = self.get_object()
        qs = Message.objects.filter(group=group).select_related("sender").order_by("timestamp")
        return Response(MessageSerializer(qs, many=True, context={"request": request}).data)


# ──────────────────────────────────────────────────────────────
# Private Chat
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="Inbox — list recent private messages",
        description=(
            "Returns the 100 most recent private messages the authenticated user has sent or received, "
            "ordered newest-first. Use the history action to fetch a conversation with a specific user."
        ),
        responses={200: MessageSerializer(many=True)},
        tags=["Chat — Private"],
    ),
)
class PrivateChatViewSet(viewsets.GenericViewSet):
    """
    Handles one-on-one messaging between patients, doctors, and admins.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        qs = Message.objects.filter(
            Q(sender=request.user) | Q(receiver=request.user),
            group__isnull=True,
        ).select_related("sender", "receiver").order_by("-timestamp")[:100]
        return Response(MessageSerializer(qs, many=True, context={"request": request}).data)

    @extend_schema(
        summary="Send a private message",
        description=(
            "Sends a new private message to a specified user. "
            "Optionally accepts a file attachment (e.g. prescriptions, lab reports). "
            "Returns 403 if the recipient has blocked the sender."
        ),
        request=MessageSerializer,
        parameters=[
            OpenApiParameter(
                name="receiver",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the recipient user.",
                required=True,
            ),
            OpenApiParameter(
                name="content",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Text body of the message.",
                required=True,
            ),
        ],
        responses={
            201: MessageSerializer,
            400: OpenApiResponse(description="receiver and content are required."),
            403: OpenApiResponse(description="You are blocked by this user."),
            404: OpenApiResponse(description="Receiver not found."),
        },
        tags=["Chat — Private"],
    )
    @action(detail=False, methods=["post"])
    def send_private_message(self, request):
        receiver_id = request.data.get("receiver")
        content = request.data.get("content")
        if not receiver_id or not content:
            return Response({"error": "receiver and content are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            receiver = User.objects.get(pk=receiver_id)
        except User.DoesNotExist:
            return Response({"error": "Receiver not found."}, status=status.HTTP_404_NOT_FOUND)

        if BlockedUser.objects.filter(blocked_by=receiver, blocked_user=request.user).exists():
            return Response({"error": "You are blocked by this user."}, status=status.HTTP_403_FORBIDDEN)

        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
            attachment=request.data.get("attachment"),
        )
        return Response(
            MessageSerializer(message, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Get conversation history with a user",
        description=(
            "Returns the full ordered message history between the authenticated user and the specified partner. "
            "Both sides of the conversation are included. Messages are returned oldest-first."
        ),
        parameters=[
            OpenApiParameter(
                name="other_user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description="ID of the other participant in the conversation.",
                required=True,
            ),
        ],
        responses={
            200: MessageSerializer(many=True),
            404: OpenApiResponse(description="User not found."),
        },
        tags=["Chat — Private"],
    )
    @action(detail=False, methods=["get"], url_path=r"history/(?P<other_user_id>\d+)")
    def history(self, request, other_user_id=None):
        qs = Message.objects.filter(
            group__isnull=True,
        ).filter(
            Q(sender=request.user, receiver_id=other_user_id)
            | Q(sender_id=other_user_id, receiver=request.user)
        ).select_related("sender", "receiver").order_by("timestamp")
        return Response(MessageSerializer(qs, many=True, context={"request": request}).data)


# ──────────────────────────────────────────────────────────────
# Presence
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List all user presence records",
        description="Returns presence status and last-seen timestamp for all users.",
        responses={200: UserPresenceSerializer(many=True)},
        tags=["Chat — Presence"],
    ),
    retrieve=extend_schema(
        summary="Get a specific user's presence",
        responses={
            200: UserPresenceSerializer,
            404: OpenApiResponse(description="Presence record not found."),
        },
        tags=["Chat — Presence"],
    ),
)
class UserPresenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserPresence.objects.select_related("user")
    serializer_class = UserPresenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Set own presence status",
        description=(
            "Allows the authenticated user to set their own status to ONLINE, AWAY, or OFFLINE. "
            "Creates the presence record automatically on first call. "
            "`last_seen` is updated automatically on every save."
        ),
        request=UserPresenceSerializer,
        responses={
            200: UserPresenceSerializer,
            400: OpenApiResponse(description="Invalid status value. Must be ONLINE, AWAY, or OFFLINE."),
        },
        tags=["Chat — Presence"],
    )
    @action(detail=False, methods=["post"])
    def set_status(self, request):
        status_value = request.data.get("status")
        allowed = {choice[0] for choice in UserPresence.PresenceStatus.choices}
        if status_value not in allowed:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        presence, _ = UserPresence.objects.get_or_create(user=request.user)
        presence.status = status_value
        presence.save(update_fields=["status", "last_seen"])
        return Response(UserPresenceSerializer(presence).data, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────
# Blocking
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List blocked users",
        description=(
            "Returns all block records issued by the authenticated user. "
            "Admins see all blocks across the platform."
        ),
        responses={200: BlockedUserSerializer(many=True)},
        tags=["Chat — Moderation"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a block record",
        responses={
            200: BlockedUserSerializer,
            404: OpenApiResponse(description="Block record not found."),
        },
        tags=["Chat — Moderation"],
    ),
)
class BlockedUserViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = BlockedUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return BlockedUser.objects.select_related("blocked_by", "blocked_user").all()
        return BlockedUser.objects.select_related("blocked_by", "blocked_user").filter(blocked_by=self.request.user)

    @extend_schema(
        summary="Block a user",
        description=(
            "Allows a doctor or admin to block a patient from sending them private messages. "
            "If the user is already blocked, updates the reason if a new one is provided."
        ),
        request=BlockedUserSerializer,
        parameters=[
            OpenApiParameter(
                name="blocked_user",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the user to block.",
                required=True,
            ),
            OpenApiParameter(
                name="reason",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Optional reason for the block.",
                required=False,
            ),
        ],
        responses={
            201: BlockedUserSerializer,
            400: OpenApiResponse(description="blocked_user is required."),
            403: OpenApiResponse(description="Only doctors and admins can block users."),
            404: OpenApiResponse(description="Target user not found."),
        },
        tags=["Chat — Moderation"],
    )
    @action(detail=False, methods=["post"])
    def block_user(self, request):
        if request.user.role not in {"DOCTOR", "ADMIN"}:
            return Response({"error": "Only doctors/admins can block users."}, status=status.HTTP_403_FORBIDDEN)

        blocked_user_id = request.data.get("blocked_user")
        reason = request.data.get("reason", "")
        if not blocked_user_id:
            return Response({"error": "blocked_user is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target = User.objects.get(pk=blocked_user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        block, _ = BlockedUser.objects.get_or_create(
            blocked_by=request.user,
            blocked_user=target,
            defaults={"reason": reason},
        )
        if reason and block.reason != reason:
            block.reason = reason
            block.save(update_fields=["reason"])

        return Response(BlockedUserSerializer(block).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Unblock a user",
        description="Removes an existing block. Returns 404 if the block record does not exist.",
        request=None,
        parameters=[
            OpenApiParameter(
                name="blocked_user",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID of the user to unblock.",
                required=True,
            ),
        ],
        responses={
            200: OpenApiResponse(description="User unblocked successfully."),
            400: OpenApiResponse(description="blocked_user is required."),
            404: OpenApiResponse(description="Block record not found."),
        },
        tags=["Chat — Moderation"],
    )
    @action(detail=False, methods=["post"])
    def unblock_user(self, request):
        blocked_user_id = request.data.get("blocked_user")
        if not blocked_user_id:
            return Response({"error": "blocked_user is required."}, status=status.HTTP_400_BAD_REQUEST)

        deleted, _ = BlockedUser.objects.filter(
            blocked_by=request.user, blocked_user_id=blocked_user_id
        ).delete()
        if not deleted:
            return Response({"error": "Block record not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "User unblocked successfully."}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────────────────────
# Patient Complaints
# ──────────────────────────────────────────────────────────────

@extend_schema_view(
    list=extend_schema(
        summary="List complaints",
        description=(
            "Doctors see only the complaints they have filed. "
            "Admins see all complaints across the platform."
        ),
        responses={200: PatientComplaintSerializer(many=True)},
        tags=["Chat — Moderation"],
    ),
    retrieve=extend_schema(
        summary="Retrieve a complaint",
        responses={
            200: PatientComplaintSerializer,
            404: OpenApiResponse(description="Complaint not found."),
        },
        tags=["Chat — Moderation"],
    ),
)
class PatientComplaintViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PatientComplaintSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return PatientComplaint.objects.select_related("reported_by", "patient").all()
        return PatientComplaint.objects.select_related("reported_by", "patient").filter(reported_by=self.request.user)

    @extend_schema(
        summary="File a complaint against a patient",
        description=(
            "Allows a doctor to file a formal complaint about a patient's disruptive or spammy behaviour. "
            "Requires `patient` (user ID) and `description`. "
            "The complaint is created with OPEN status and queued for admin review."
        ),
        request=PatientComplaintSerializer,
        responses={
            201: PatientComplaintSerializer,
            400: OpenApiResponse(description="patient and description are required, or validation error."),
            403: OpenApiResponse(description="Only doctors can file complaints."),
            404: OpenApiResponse(description="Patient user not found."),
        },
        tags=["Chat — Moderation"],
    )
    @action(detail=False, methods=["post"])
    def file_complaint(self, request):
        if request.user.role != "DOCTOR":
            return Response({"error": "Only doctors can file complaints."}, status=status.HTTP_403_FORBIDDEN)

        patient_id = request.data.get("patient")
        description = request.data.get("description")
        if not patient_id or not description:
            return Response({"error": "patient and description are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            patient = User.objects.get(pk=patient_id)
        except User.DoesNotExist:
            return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

        complaint = PatientComplaint.objects.create(
            reported_by=request.user,
            patient=patient,
            description=description,
        )
        return Response(PatientComplaintSerializer(complaint).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Resolve or update a complaint (admin)",
        description=(
            "Admin-only. Updates the status and/or admin notes on a complaint. "
            "Valid status values: OPEN, UNDER_REVIEW, RESOLVED, DISMISSED. "
            "Returns 400 if an unrecognised status value is submitted."
        ),
        request=PatientComplaintSerializer,
        responses={
            200: PatientComplaintSerializer,
            400: OpenApiResponse(description="Invalid status value."),
            403: OpenApiResponse(description="Admin access only."),
            404: OpenApiResponse(description="Complaint not found."),
        },
        tags=["Chat — Moderation"],
    )
    @action(detail=True, methods=["patch"])
    def resolve_complaint(self, request, pk=None):
        if not request.user.is_staff:
            return Response({"error": "Admin access only."}, status=status.HTTP_403_FORBIDDEN)

        complaint = self.get_object()
        new_status = request.data.get("status")
        admin_notes = request.data.get("admin_notes", "")
        allowed = {choice[0] for choice in PatientComplaint.ComplaintStatus.choices}

        if new_status and new_status not in allowed:
            return Response({"error": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        if new_status:
            complaint.status = new_status
        if admin_notes:
            complaint.admin_notes = admin_notes
        complaint.save()
        return Response(PatientComplaintSerializer(complaint).data, status=status.HTTP_200_OK)