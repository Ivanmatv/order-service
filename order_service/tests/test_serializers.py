from django.test import TestCase

from orders.serializers import OrderItemSerializer, OrderStatusSerializer
from .factories import ProductFactory


class OrderItemSerializerTest(TestCase):
    def test_valid_data(self):
        """Тест валидных данных"""
        product = ProductFactory(is_active=True)

        data = {
            'product_id': product.id,
            'quantity': 2
        }

        serializer = OrderItemSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_product_id(self):
        """Тест невалидного ID товара"""
        data = {
            'product_id': 999,  # Несуществующий товар
            'quantity': 1
        }

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('product_id', serializer.errors)

    def test_inactive_product(self):
        """Тест неактивного товара"""
        product = ProductFactory(is_active=False)

        data = {
            'product_id': product.id,
            'quantity': 1
        }

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_invalid_quantity(self):
        """Тест невалидного количества"""
        product = ProductFactory()

        data = {
            'product_id': product.id,
            'quantity': 0  # Должно быть >= 1
        }

        serializer = OrderItemSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('quantity', serializer.errors)


class OrderStatusSerializerTest(TestCase):
    def test_valid_status(self):
        """Тест валидного статуса"""
        data = {'status': 'processing'}
        serializer = OrderStatusSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_status(self):
        """Тест невалидного статуса"""
        data = {'status': 'invalid_status'}
        serializer = OrderStatusSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('status', serializer.errors)