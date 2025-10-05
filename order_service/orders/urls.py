from django.urls import path

from .views import AddOrderItemView, OrderDetailView, OrderItemsView

urlpatterns = [
    path('v1/orders/<int:order_id>/items/', AddOrderItemView.as_view(), name='add-order-item'),
    path('v1/orders/<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('v1/orders/<int:order_id>/items/list/', OrderItemsView.as_view(), name='order-items-list'),
]