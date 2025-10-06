from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count

from .models import Category, Customer, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'product_count', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    
    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Количество товаров'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'order_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    def order_count(self, obj):
        return obj.order_set.count()
    order_count.short_description = 'Количество заказов'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'quantity', 'price', 
        'stock_status', 'is_active', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['quantity', 'price', 'is_active']
    actions = ['activate_products', 'deactivate_products']
    
    def stock_status(self, obj):
        if obj.quantity == 0:
            return format_html('<span style="color: red;">❌ Нет в наличии</span>')
        elif obj.quantity <= 10:
            return format_html('<span style="color: orange;">⚠️ Мало</span>')
        else:
            return format_html('<span style="color: green;">✓ В наличии</span>')
    stock_status.short_description = 'Статус'
    
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} товаров активировано')
    activate_products.short_description = "Активировать выбранные товары"
    
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} товаров деактивировано')
    deactivate_products.short_description = "Деактивировать выбранные товары"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ['unit_price', 'total_price_display']
    fields = ['product', 'quantity', 'unit_price', 'total_price_display']
    
    def total_price_display(self, obj):
        return f"{obj.total_price:.2f} ₽"
    total_price_display.short_description = 'Общая стоимость'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'customer_link', 'status_badge', 'total_amount', 
        'items_count', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'customer']
    search_fields = ['customer__name', 'id']
    readonly_fields = ['created_at', 'updated_at', 'total_amount']
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped']
    
    def customer_link(self, obj):
        url = reverse('admin:orders_customer_change', args=[obj.customer.id])
        return format_html('<a href="{}">{}</a>', url, obj.customer.name)
    customer_link.short_description = 'Клиент'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'confirmed': 'blue', 
            'processing': 'orange',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    
    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = 'Товаров'
    
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status=Order.Status.PROCESSING)
        self.message_user(request, f'{updated} заказов переведено в обработку')
    mark_as_processing.short_description = "Перевести в обработку"
    
    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status=Order.Status.SHIPPED)
        self.message_user(request, f'{updated} заказов переведено в отправленные')
    mark_as_shipped.short_description = "Перевести в отправленные"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order_link', 'product', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order', 'created_at']
    readonly_fields = ['created_at']
    
    def order_link(self, obj):
        url = reverse('admin:orders_order_change', args=[obj.order.id])
        return format_html('<a href="{}">Заказ #{}</a>', url, obj.order.id)
    order_link.short_description = 'Заказ'
    
    def total_price(self, obj):
        return f"{obj.total_price:.2f} ₽"
    total_price.short_description = 'Общая стоимость'


admin.site.site_header = "Order Service Administration"
admin.site.site_title = "Order Service Admin"
admin.site.index_title = "Добро пожаловать в панель управления"