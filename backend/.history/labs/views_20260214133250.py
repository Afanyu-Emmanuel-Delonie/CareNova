from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormDataParser
from .models import LabResult
from .serializers import LabResultSerializer


