from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Order, OrderItem
from .serializers import OrderSerializer
from pharmacy.models import Product

class OrderCreateView(CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Create a new order (Checkout)",
        description="Submit a list of items to purchase. Validates prescriptions for restricted medicine.",
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Prescription missing or insufficient stock.")
        },
        tags=['Orders']
    )
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        items_data = data.get('items', [])

        if not items_data:
            return Response({"error": "No items in order"}, status=status.HTTP_400_BAD_REQUEST)

        # Initialize the order
        order = Order.objects.create(user=user, total_price=0)
        total = 0

        for item in items_data:
            product = Product.objects.get(id=item['product_id'])
            qty = item['quantity']

            # Stock check
            if product.stock < qty:
                transaction.set_rollback(True) 
                return Response({"error": f"Insufficient stock for {product.name}"}, status=status.HTTP_400_BAD_REQUEST)

            # Calculate price
            item_price = product.price * qty
            total += item_price

            # Create the order item
            OrderItem.objects.create(
                order=order,
                product=product,
                price=product.price,
                quantity=qty
            )

            # Reduce inventory
            product.stock -= qty
            product.save()

        order.total_price = total
        order.save()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)