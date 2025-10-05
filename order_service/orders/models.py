from django.db import models
from django.core.exceptions import ValidationError


class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        db_table = 'categories'
    
    def __str__(self):
        return self.name
    
    def clean(self):
        if self.parent and self.parent.id == self.id:
            raise ValidationError("Category cannot be a parent of itself")


class Customer(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    
    class Meta:
        db_table = 'customers'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    
    class Meta:
        db_table = 'products'
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
    
    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'orders'
    
    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    
    class Meta:
        db_table = 'order_items'
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
    
    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be positive")
        
        # Проверяем наличие товара при создании/изменении
        if self.pk:
            original = OrderItem.objects.get(pk=self.pk)
            quantity_change = self.quantity - original.quantity
        else:
            quantity_change = self.quantity

        if self.product.quantity < quantity_change:
            raise ValidationError(
                f"Insufficient stock. Available: {self.product.quantity}, requested: {quantity_change}"
            )