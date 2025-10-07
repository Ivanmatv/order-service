from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from orders.models import OrderItem, Product
from .factories import (
    OrderItemFactory, UserFactory, OrderFactory, ProductFactory, 
    CustomerFactory, CategoryFactory
)


class AddOrderItemViewTest(APITestCase):
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.customer = CustomerFactory()
        self.order = OrderFactory(customer=self.customer)
        self.product = ProductFactory(quantity=10, price=100)

        self.url = reverse('add-order-item', kwargs={'order_id': self.order.id})

    def test_add_item_to_order_success(self):
        """Успешное добавление товара в заказ"""
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

        # Проверяем, что позиция создана
        order_item = OrderItem.objects.filter(order=self.order, product=self.product).first()
        self.assertIsNotNone(order_item)
        self.assertEqual(order_item.quantity, 2)

        # Проверяем, что количество товара уменьшилось
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 8)

    def test_add_item_insufficient_stock(self):
        """Попытка добавить товар при недостаточном количестве"""
        data = {
            'product_id': self.product.id,
            'quantity': 20  # Больше чем есть в наличии
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Insufficient stock')

    def test_add_item_update_existing(self):
        """Обновление существующей позиции в заказе"""
        # Сначала добавляем товар
        OrderItemFactory(order=self.order, product=self.product, quantity=1)

        # Затем добавляем еще
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }

        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['action'], 'updated')

        # Проверяем, что количество обновилось
        order_item = OrderItem.objects.get(order=self.order, product=self.product)
        self.assertEqual(order_item.quantity, 3)

    def test_add_item_unauthorized(self):
        """Попытка доступа без авторизации"""
        client = APIClient()  # Неавторизованный клиент
        data = {
            'product_id': self.product.id,
            'quantity': 1
        }

        response = client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderDetailViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.order = OrderFactory()
        self.url = reverse('order-detail', kwargs={'order_id': self.order.id})

    def test_get_order_detail(self):
        """Получение деталей заказа"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.order.id)
        self.assertIn('customer_name', response.data)
        self.assertIn('items', response.data)

    def test_get_nonexistent_order(self):
        """Попытка получить несуществующий заказ"""
        url = reverse('order-detail', kwargs={'order_id': 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductStockViewTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.category = CategoryFactory()
        Product.objects.all().delete()

        self.product_normal_stock = ProductFactory(quantity=15, category=self.category)
        self.product_low_stock = ProductFactory(quantity=5, category=self.category)
        self.product_out_of_stock = ProductFactory(quantity=0, category=self.category)
        self.product_exactly_10 = ProductFactory(quantity=10, category=self.category)

        self.url = reverse('product-stock')

    def test_get_all_products(self):
        """Получение всех товаров"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['products']), 4)

    def test_filter_low_stock(self):
        """Фильтрация товаров с низким запасом"""
        response = self.client.get(self.url, {'low_stock': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['products']), 2)
        self.assertEqual(response.data['low_stock_count'], 2)

    def test_filter_out_of_stock(self):
        """Фильтрация товаров, которых нет в наличии"""
        response = self.client.get(self.url, {'out_of_stock': 'true'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['products']), 1)
        self.assertEqual(response.data['out_of_stock_count'], 1)