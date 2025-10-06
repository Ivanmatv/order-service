from django.urls import path
from .views import (
    AddOrderItemView, OrderDetailView, OrderListView,
    OrderStatusUpdateView, ProductStockView
)

urlpatterns = [
    path('v1/orders/<int:order_id>/items/', AddOrderItemView.as_view(), name='add-order-item'),
    path('v1/orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('v1/orders/<int:order_id>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('v1/orders/', OrderListView.as_view(), name='order-list'),
    path('v1/products/stock/', ProductStockView.as_view(), name='product-stock'),
]