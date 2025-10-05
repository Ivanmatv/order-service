from rest_framework import serializers
from .models import OrderItem, Order


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'quantity', 'price']


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name')

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'created_at', 'items']