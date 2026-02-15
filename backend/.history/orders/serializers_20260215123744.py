from rest_framework import serializers
from .models import Order, OrderItem
from pharmacy.models import Product
from consultations.models import Prescription

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'items', 'total_price', 'status', 'created_at']
        read_only_fields = ['total_price', 'status']

    def validate(self, data):
        user = self.context['request'].user
        items = self.initial_data.get('items') 

        for item in items:
            product = Product.objects.get(id=item['product_id'])
            
            if product.requires_prescription:
                # Look for an active prescription for this specific medicine for this user
                has_prescription = Prescription.objects.filter(
                    diagnosis__patient=user,
                    medicine_name__icontains=product.name 
                ).exists()

                if not has_prescription:
                    raise serializers.ValidationError(
                        f"You cannot purchase {product.name} without a valid digital prescription."
                    )
        return data