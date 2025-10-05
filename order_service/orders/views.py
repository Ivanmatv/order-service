from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, Product, OrderItem
from .serializers import OrderItemSerializer, OrderDetailSerializer


class AddOrderItemView(APIView):
    permission_classes = [IsAuthenticated]
    
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
                    existing_item.save()
                else:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity
                    )
                
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
    permission_classes = [IsAuthenticated]
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)
