from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from labs.permissions import IsDoctor
from .models import Diagnosis
from .serializers import DiagnosisSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import DiagnosisSerializer
from .models import Diagnosis


class CreateDiagnosisView(CreateAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    @extend_schema(
        summary="Submit Medical Diagnosis",
        description="Allows a doctor to submit a diagnosis for a specific lab result. "
                    "This action automatically marks the lab result as reviewed.",
        request=DiagnosisSerializer,
        responses={
            201: DiagnosisSerializer,
            400: OpenApiResponse(description="Invalid data or lab result already reviewed."),
            403: OpenApiResponse(description="Only doctors can perform this action.")
        },
        tags=['Consultations']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        lab_result = serializer.validated_data['lab_result']
        serializer.save(
            doctor=self.request.user,
            patient=lab_result.patient
        )
        lab_result.is_reviewed = True
        lab_result.save()

class AddPrescriptionView(CreateAPIView):
    serializer_class = 

class PatientMedicalHistoryView(ListAPIView):
    serializer_class = DiagnosisSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="View Medical History",
        description="Returns a list of all diagnoses received by the authenticated patient.",
        responses={200: DiagnosisSerializer(many=True)},
        tags=['Consultations']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Diagnosis.objects.filter(patient=self.request.user)