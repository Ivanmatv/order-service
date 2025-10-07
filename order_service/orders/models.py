from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy


class Category(models.Model):
    name = models.CharField(gettext_lazy('name'), max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    created_at = models.DateTimeField(gettext_lazy('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(gettext_lazy('updated at'), auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = gettext_lazy('category')
        verbose_name_plural = gettext_lazy('categories')
        indexes = [
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        return self.name

    def get_full_path(self):
        """Возвращает полный путь категории"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name

    def clean(self):
        if self.parent and self.parent.id == self.id:
            raise ValidationError(gettext_lazy("Категория не может быть родительской для самой себя"))

        if self.parent:
            current = self.parent
            while current:
                if current == self:
                    raise ValidationError(gettext_lazy("Circular dependency detected in category hierarchy"))
                current = current.parent


class Customer(models.Model):
    name = models.CharField(gettext_lazy('name'), max_length=255)
    email = models.EmailField(gettext_lazy('email'), blank=True)
    phone = models.CharField(gettext_lazy('phone'), max_length=20, blank=True)
    address = models.TextField(gettext_lazy('address'))
    created_at = models.DateTimeField(gettext_lazy('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(gettext_lazy('updated at'), auto_now=True)

    class Meta:
        db_table = 'customers'
        verbose_name = gettext_lazy('customer')
        verbose_name_plural = gettext_lazy('customers')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(gettext_lazy('name'), max_length=255)
    description = models.TextField(gettext_lazy('description'), blank=True)
    quantity = models.IntegerField(gettext_lazy('quantity'))
    price = models.DecimalField(gettext_lazy('price'), max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(gettext_lazy('cost price'), max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=gettext_lazy('category'))
    is_active = models.BooleanField(gettext_lazy('is active'), default=True)
    created_at = models.DateTimeField(gettext_lazy('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(gettext_lazy('updated at'), auto_now=True)

    class Meta:
        db_table = 'products'
        verbose_name = gettext_lazy('product')
        verbose_name_plural = gettext_lazy('products')
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gte=0),
                name='check_quantity_positive'
            ),
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='check_price_positive'
            ),
        ]
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
            models.Index(fields=['quantity']),
        ]

    @property
    def in_stock(self):
        return self.quantity > 0

    @property
    def low_stock(self):
        return 0 < self.quantity <= 10


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', gettext_lazy('Pending')
        CONFIRMED = 'confirmed', gettext_lazy('Confirmed')
        PROCESSING = 'processing', gettext_lazy('Processing')
        SHIPPED = 'shipped', gettext_lazy('Shipped')
        DELIVERED = 'delivered', gettext_lazy('Delivered')
        CANCELLED = 'cancelled', gettext_lazy('Cancelled')

    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, verbose_name=gettext_lazy('customer'))
    status = models.CharField(
        gettext_lazy('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    total_amount = models.DecimalField(
        gettext_lazy('total amount'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    notes = models.TextField(gettext_lazy('notes'), blank=True)
    created_at = models.DateTimeField(gettext_lazy('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(gettext_lazy('updated at'), auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = gettext_lazy('order')
        verbose_name_plural = gettext_lazy('orders')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['customer', 'created_at']),
            models.Index(fields=['total_amount']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.customer.name} ({self.status})"

    def calculate_total(self):
        """Пересчитывает общую сумму заказа"""
        return sum(item.total_price for item in self.items.all())

    def save(self, *args, **kwargs):
        if self.pk:  # Если заказ уже существует
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name=gettext_lazy('order'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name=gettext_lazy('product'))
    quantity = models.IntegerField(gettext_lazy('quantity'))
    unit_price = models.DecimalField(gettext_lazy('unit price'), max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(gettext_lazy('created at'), auto_now_add=True)

    class Meta:
        db_table = 'order_items'
        verbose_name = gettext_lazy('order item')
        verbose_name_plural = gettext_lazy('order items')
        constraints = [
            models.CheckConstraint(
                check=models.Q(quantity__gt=0),
                name='check_order_quantity_positive'
            ),
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_order_product'
            )
        ]
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['product']),
        ]

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(gettext_lazy("Quantity must be positive"))

        if not self.unit_price:
            self.unit_price = self.product.price

        # Проверяем наличие товара при создании/изменении
        if self.pk:
            original = OrderItem.objects.get(pk=self.pk)
            quantity_change = self.quantity - original.quantity
        else:
            quantity_change = self.quantity

        if self.product.quantity < quantity_change:
            raise ValidationError(
                gettext_lazy("Insufficient stock. Available: %(available)s, requested: %(requested)s") % {
                    'available': self.product.quantity,
                    'requested': quantity_change
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        # Обновляем общую сумму заказа
        if self.order:
            self.order.save()