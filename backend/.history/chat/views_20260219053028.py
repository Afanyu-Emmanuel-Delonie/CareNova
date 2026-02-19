from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer
from django.db.models import Q, Max
from django.contrib.auth import get_user_model

User = get_user_model()
class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all()
    serializer_class = ChatGroupSerializer

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        group.members.add(request.user)
        return Response({"message": f"You have joined {group.name}"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        group = self.get_object()
        messages = group.messages.all()[:50] # Get last 50 messages
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)
    
class PrivateChatViewSet(viewsets.ViewSet):
    """
    Handles One-on-One messaging between Patients, Doctors, and Admins.
    """

    def list(self, request):
        """
        Returns an 'Inbox' view: all unique users the current user has 
        exchanged private messages with, along with the last message timestamp.
        """
        user = request.user
        
        # Get all private messages where the user is either sender or receiver
        private_messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user),
            group__isnull=True
        )

        # Identify unique chat partners
        # We find the maximum timestamp for each conversation to sort the inbox
        participants = User.objects.filter(
            Q(sent_messages__receiver=user) | Q(received_private_messages__sender=user)
        ).distinct().annotate(
            last_message_at=Max(
                Q(sent_messages__timestamp=Max('sent_messages__timestamp'), sent_messages__receiver=user) |
                Q(received_private_messages__timestamp=Max('received_private_messages__timestamp'), received_private_messages__sender=user)
            )
        ).order_by('-last_message_at')

        inbox_data = []
        for participant in participants:
            # Get the very last message exchanged with this specific person
            last_msg = Message.objects.filter(
                Q(sender=user, receiver=participant) | Q(sender=participant, receiver=user),
                group__isnull=True
            ).latest('timestamp')

            inbox_data.append({
                "user_id": participant.id,
                "full_name": f"{participant.profile.first_name} {participant.profile.last_name}",
                "role": participant.role,
                "last_message": last_msg.content[:50], # Preview of the message
                "timestamp": last_msg.timestamp,
                "unread_count": Message.objects.filter(sender=participant, receiver=user, is_read=False).count()
            })

        return Response(inbox_data)

    @action(detail=False, methods=['get'], url_path='history/(?P<other_user_id>[^/.]+)')
    def history(self, request, other_user_id=None):
        """
        Retrieves the full conversation history between the user and a specific partner.
        Automatically marks received messages as 'read'.
        """
        user = request.user
        
        # 1. Fetch the messages
        messages = Message.objects.filter(
            Q(sender=user, receiver_id=other_user_id) |
            Q(sender_id=other_user_id, receiver=user),
            group__isnull=True
        ).order_by('timestamp')

        # 2. Mark incoming messages as read
        messages.filter(receiver=user, is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='send')
    def send_private_message(self, request):
        """
        Endpoint to send a new private message.
        """
        receiver_id = request.data.get('receiver_id')
        content = request.data.get('content')
        attachment = request.FILES.get('attachment')

        if not receiver_id or not content:
            return Response({"error": "Receiver and content are required."}, status=400)

        message = Message.objects.create(
            sender=request.user,
            receiver_id=receiver_id,
            content=content,
            attachment=attachment
        )

        serializer = MessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)