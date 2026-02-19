from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ChatGroup, Message
from .serializers import ChatGroupSerializer, MessageSerializer

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
    
