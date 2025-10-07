import logging

from django.forms import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Order, Product, OrderItem
from .serializers import (
    OrderItemSerializer,
    OrderDetailSerializer,
    OrderStatusSerializer,
    ProductStockSerializer
)

logger = logging.getLogger(__name__)


class OrderItemThrottle(UserRateThrottle):
    rate = '100/hour'


class AddOrderItemView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [OrderItemThrottle]

    def post(self, request, order_id):
        serializer = OrderItemSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Validation error for order {order_id}: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            with transaction.atomic():
                order = get_object_or_404(
                    Order.objects.select_for_update(), 
                    id=order_id
                )
                product = get_object_or_404(
                    Product.objects.select_for_update(),
                    id=product_id,
                    is_active=True
                )

                if product.quantity < quantity:
                    logger.warning(
                        f"Insufficient stock for product {product_id}. "
                        f"Requested: {quantity}, Available: {product.quantity}"
                    )
                    return Response({
                        'error': 'Insufficient stock',
                        'available': product.quantity,
                        'product_name': product.name
                    }, status=status.HTTP_400_BAD_REQUEST)

                existing_item = OrderItem.objects.filter(
                    order=order,
                    product=product
                ).first()

                if existing_item:
                    existing_item.quantity += quantity
                    existing_item.full_clean()
                    existing_item.save()
                    action = 'updated'
                else:
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        unit_price=product.price
                    )
                    action = 'created'

                product.quantity -= quantity
                product.save()

                logger.info(
                    f"Order item {action} for order {order_id}, "
                    f"product {product_id}, quantity {quantity} by user {request.user.username}"
                )

                order.refresh_from_db()

                return Response({
                    'success': True,
                    'message': 'Product added to order successfully',
                    'order_total': float(order.total_amount),
                    'action': action
                }, status=status.HTTP_200_OK)

        except ValidationError as e:
            logger.error(f"Validation error in order {order_id}: {str(e)}")
            return Response({
                'error': 'Validation error',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error adding item to order {order_id}: {str(e)}", exc_info=True)
            return Response({
                'error': 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = get_object_or_404(
                Order.objects.select_related('customer')
                           .prefetch_related('items__product'),
                id=order_id
            )
            serializer = OrderDetailSerializer(order)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Error retrieving order {order_id}: {str(e)}")
            return Response({
                'error': 'Error retrieving order'
            }, status=status.HTTP_404_NOT_FOUND)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = Order.objects.select_related('customer').order_by('-created_at')

            status_filter = request.query_params.get('status')
            if status_filter:
                orders = orders.filter(status=status_filter)

            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 20))
            start = (page - 1) * page_size
            end = start + page_size

            paginated_orders = orders[start:end]
            serializer = OrderDetailSerializer(paginated_orders, many=True)

            return Response({
                'orders': serializer.data,
                'page': page,
                'page_size': page_size,
                'total_orders': orders.count(),
                'has_next': end < orders.count()
            })

        except Exception as e:
            logger.error(f"Error listing orders: {str(e)}")
            return Response({
                'error': 'Error retrieving orders list'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, order_id):
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = get_object_or_404(Order, id=order_id)
                new_status = serializer.validated_data['status']
                old_status = order.status

                order.status = new_status
                order.save()

                logger.info(
                    f"Order {order_id} status changed from {old_status} to {new_status} "
                    f"by user {request.user.username}"
                )

                return Response({
                    'success': True,
                    'message': f'Order status updated to {new_status}',
                    'order_id': order_id,
                    'old_status': old_status,
                    'new_status': new_status
                })

        except Exception as e:
            logger.error(f"Error updating order {order_id} status: {str(e)}")
            return Response({
                'error': 'Error updating order status'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductStockView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            products = Product.objects.select_related('category').filter(is_active=True)

            low_stock_only = request.query_params.get('low_stock')
            if low_stock_only and low_stock_only.lower() == 'true':
                products = products.filter(quantity__lte=10, quantity__gt=0)

            out_of_stock = request.query_params.get('out_of_stock')
            if out_of_stock and out_of_stock.lower() == 'true':
                products = products.filter(quantity=0)

            serializer = ProductStockSerializer(products, many=True)
            return Response({
                'products': serializer.data,
                'total_count': products.count(),
                'low_stock_count': products.filter(quantity__lte=10, quantity__gt=0).count(),
                'out_of_stock_count': products.filter(quantity=0).count()
            })

        except Exception as e:
            logger.error(f"Error retrieving product stock: {str(e)}")
            return Response({
                'error': 'Error retrieving product stock'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
