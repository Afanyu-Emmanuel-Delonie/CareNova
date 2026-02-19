from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer
from django.db.models import Q, Max
from .serializers import MessageSerializer
from django.contrib.auth import get_user_model

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
    def list(self, request):
        """Get a list of all people the user has chatted with."""
        user = request.user
        # Logic to find unique participants in private messages
        pass

    @action(detail=False, methods=['get'], url_path='history/(?P<other_user_id>\d+)')
    def history(self, request, other_user_id=None):
        """Get message history between me and another user (Doctor or Admin)."""
        messages = Message.objects.filter(
            models.Q(sender=request.user, receiver_id=other_user_id) |
            models.Q(sender_id=other_user_id, receiver=request.user)
        ).filter(group__isnull=True)
        
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)