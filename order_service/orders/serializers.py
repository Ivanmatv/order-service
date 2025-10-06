from rest_framework import serializers

from .models import OrderItem, Order, Product


class OrderItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def validate_product_id(self, value):
        if not Product.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Product does not exist or is not active")
        return value


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, source='total_price')

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product_id', 'product_name',
            'quantity', 'unit_price', 'total_price'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemDetailSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.name')
    customer_email = serializers.CharField(source='customer.email')
    status_display = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = [
            'id', 'customer_name', 'customer_email', 'status',
            'status_display', 'total_amount', 'notes',
            'created_at', 'updated_at', 'items'
        ]


class OrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.Status.choices)

    def validate_status(self, value):
        if value not in dict(Order.Status.choices):
            raise serializers.ValidationError("Invalid status")
        return value


class ProductStockSerializer(serializers.ModelSerializer):
    in_stock = serializers.BooleanField(source='in_stock')
    low_stock = serializers.BooleanField(source='low_stock')
    category_name = serializers.CharField(source='category.name')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'quantity', 'price', 
            'in_stock', 'low_stock', 'category_name', 'is_active'
        ]