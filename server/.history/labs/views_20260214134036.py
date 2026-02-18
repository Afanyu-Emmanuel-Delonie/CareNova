from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormDataParser
from .models import LabResult
from .serializers import LabResultSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions


class LabUploadView(CreateAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormDataParser]
    
    @extend_schema(
        summary="Upload Lab Result",
        description="Allows patients to upload an image of their lab results. Requires a Bearer Token.",
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'result_photo': {'type': 'string', 'format': 'binary'},
                    'description': {'type': 'string'}
                }
            }
        },
        responses={
            201: LabResultSerializer,
            401: OpenApiResponse(description="Unauthorized - Token missing or invalid"),
        },
        tags=['Labs']
    )
    
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)
        
class PatientLabListView(ListAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List My Lab Results",
        description="Returns a list of all lab results uploaded by the authenticated patient.",
        responses={200: LabResultSerializer(many=True)},
        tags=['Labs']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return LabResult.objects.filter(patient=self.request.user)

class isDoctor(permissions.BasePermission):
    def has    


