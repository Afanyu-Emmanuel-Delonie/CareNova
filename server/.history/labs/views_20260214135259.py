from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser # Fixed name here
from .permissions import IsDoctor # Fixed relative import
from .models import LabResult
from .serializers import LabResultSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse

class LabUploadView(CreateAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser] # Fixed name here
    
    @extend_schema(
        summary="Upload Lab Result",
        description="Allows patients to upload an image of their lab results.",
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
        responses={201: LabResultSerializer},
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

class DoctorLabListView(ListAPIView):
    serializer_class = LabResultSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    @extend_schema(
        summary="List All Unreviewed Lab Results",
        description="Allows doctors to see all lab results that have not been reviewed yet.",
        tags=['Doctor Portal']
    )
    def get_queryset(self):
        return LabResult.objects.filter(is_reviewed=False)


