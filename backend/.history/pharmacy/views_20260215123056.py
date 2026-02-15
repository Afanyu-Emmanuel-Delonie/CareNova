from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from drf_spectacular.utils import extend_schema

class ProductListView(ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny] 

    @extend_schema(
        summary="List all medicines",
        description="Public endpoint to browse available medications and products.",
        tags=['Pharmacy']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ProductCreateView(CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser] 

    @extend_schema(
        summary="Add new product (Admin Only)",
        description="Allows staff to add new medications to the catalog.",
        tags=['Pharmacy Admin']
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class ProductDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

    @extend_schema(
        summary="Retrieve, update or delete a product",
        description="Public GET, but PUT/PATCH/DELETE restricted to Admins.",
        tags=['Pharmacy']
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)