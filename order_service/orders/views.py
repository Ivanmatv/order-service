from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, Product, OrderItem
from .serializers import OrderItemSerializer, OrderDetailSerializer


class AddOrderItemView(APIView):
    def post(self, request, order_id):
        serializer = OrderItemSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            with transaction.atomic():
                order = get_object_or_404(Order, id=order_id)
                product = get_object_or_404(Product, id=product_id)

                if product.quantity < quantity:
                    return Response({
                        'error': 'Insufficient stock',
                        'available': product.quantity
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                existing_item = OrderItem.objects.filter(
                    order=order, 
                    product=product
                ).first()
                
                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.full_clean()
                    existing_item.save()
                else:
                    new_item = OrderItem(
                        order=order,
                        product=product,
                        quantity=quantity
                    )
                    new_item.full_clean()
                    new_item.save()
                
                product.quantity -= quantity
                product.save()
                
                return Response({
                    'success': True,
                    'message': 'Product added to order successfully'
                }, status=status.HTTP_200_OK)
                
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderDetailView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)

class OrderItemsView(APIView):
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        items = order.items.select_related('product').all()
        
        items_data = []
        for item in items:
            items_data.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.product.price)
            })
        
        return Response({
            'order_id': order.id,
            'customer': order.customer.name,
            'items': items_data
        })