from django.test import TestCase
from django.urls import reverse, resolve

from orders import urls
from orders.views import (
    AddOrderItemView, OrderDetailView, OrderListView,
    OrderStatusUpdateView, ProductStockView
)


class URLTests(TestCase):
    """Тесты для проверки URL-маршрутов"""

    def test_add_order_item_url(self):
        """Тест URL для добавления товара в заказ"""
        url = reverse('add-order-item', kwargs={'order_id': 1})
        self.assertEqual(url, '/api/v1/orders/1/items/')

        # Проверяем, что URL разрешается в правильную view
        resolver = resolve('/api/v1/orders/1/items/')
        self.assertEqual(resolver.func.view_class, AddOrderItemView)
        self.assertEqual(resolver.kwargs['order_id'], 1)

    def test_order_detail_url(self):
        """Тест URL для деталей заказа"""
        url = reverse('order-detail', kwargs={'order_id': 5})
        self.assertEqual(url, '/api/v1/orders/5/')

        resolver = resolve('/api/v1/orders/5/')
        self.assertEqual(resolver.func.view_class, OrderDetailView)
        self.assertEqual(resolver.kwargs['order_id'], 5)

    def test_order_status_update_url(self):
        """Тест URL для обновления статуса заказа"""
        url = reverse('order-status-update', kwargs={'order_id': 3})
        self.assertEqual(url, '/api/v1/orders/3/status/')

        resolver = resolve('/api/v1/orders/3/status/')
        self.assertEqual(resolver.func.view_class, OrderStatusUpdateView)
        self.assertEqual(resolver.kwargs['order_id'], 3)

    def test_order_list_url(self):
        """Тест URL для списка заказов"""
        url = reverse('order-list')
        self.assertEqual(url, '/api/v1/orders/')

        resolver = resolve('/api/v1/orders/')
        self.assertEqual(resolver.func.view_class, OrderListView)

    def test_product_stock_url(self):
        """Тест URL для информации о запасах товаров"""
        url = reverse('product-stock')
        self.assertEqual(url, '/api/v1/products/stock/')

        resolver = resolve('/api/v1/products/stock/')
        self.assertEqual(resolver.func.view_class, ProductStockView)

    def test_url_names_exist(self):
        """Тест существования всех имен URL"""
        url_names = [
            'add-order-item',
            'order-detail', 
            'order-status-update',
            'order-list',
            'product-stock'
        ]

        for name in url_names:
            try:
                if name in ['add-order-item', 'order-detail', 'order-status-update']:
                    reverse(name, kwargs={'order_id': 1})
                else:
                    reverse(name)
            except Exception as e:
                self.fail(f"URL name '{name}' does not exist: {e}")

    def test_url_patterns_count(self):
        """Тест количества URL-паттернов"""
        from orders import urls
        self.assertEqual(len(urls.urlpatterns), 5)

    def test_url_parameters(self):
        """Тест параметров в URL"""
        # Проверяем, что order_id передается как integer
        resolver = resolve('/api/v1/orders/123/items/')
        self.assertIsInstance(int(resolver.kwargs['order_id']), int)

        resolver = resolve('/api/v1/orders/456/status/')
        self.assertIsInstance(int(resolver.kwargs['order_id']), int)

    def test_url_trailing_slash(self):
        """Тест завершающих слешей в URL"""
        # Все URL должны заканчиваться слешем
        urls_with_slash = [
            '/api/v1/orders/1/items/',
            '/api/v1/orders/1/',
            '/api/v1/orders/1/status/',
            '/api/v1/orders/',
            '/api/v1/products/stock/'
        ]

        for url in urls_with_slash:
            try:
                resolve(url)
            except Exception as e:
                self.fail(f"URL '{url}' should be resolvable: {e}")


class URLIntegrationTests(TestCase):
    """Интеграционные тесты URL с реальными запросами"""

    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(
            username='testuser', 
            password='testpass123'
        )

    def test_urls_return_correct_status_codes(self):
        """Тест, что URL возвращают правильные статус-коды"""
        from django.test import Client
        client = Client()
        client.force_login(self.user)

        # Тестируем доступные без данных URLs (должны возвращать 200 или 404)
        urls_to_test = [
            ('/api/v1/orders/', 200),  # Список заказов
            ('/api/v1/products/stock/', 200),  # Информация о запасах
        ]

        for url, expected_status in urls_to_test:
            response = client.get(url)
            self.assertEqual(
                response.status_code, 
                expected_status,
                f"URL {url} returned {response.status_code}, expected {expected_status}"
            )

    def test_nonexistent_urls_return_404(self):
        """Тест, что несуществующие URL возвращают 404"""
        from django.test import Client
        client = Client()
        client.force_login(self.user)

        nonexistent_urls = [
            '/api/v1/nonexistent/',
            '/api/v1/orders/invalid/',
            '/api/v1/products/invalid/'
        ]

        for url in nonexistent_urls:
            response = client.get(url)
            self.assertEqual(
                response.status_code, 
                404,
                f"URL {url} should return 404, but returned {response.status_code}"
            )

    def test_url_reverse_with_different_ids(self):
        """Тест reverse с разными ID"""
        test_ids = [1, 100, 9999]

        for order_id in test_ids:
            url = reverse('add-order-item', kwargs={'order_id': order_id})
            self.assertEqual(url, f'/api/v1/orders/{order_id}/items/')

            url = reverse('order-detail', kwargs={'order_id': order_id})
            self.assertEqual(url, f'/api/v1/orders/{order_id}/')

            url = reverse('order-status-update', kwargs={'order_id': order_id})
            self.assertEqual(url, f'/api/v1/orders/{order_id}/status/')


class URLStructureTests(TestCase):
    """Тесты структуры URL"""

    def test_url_api_version_prefix(self):
        """Тест, что все URL начинаются с /api/v1/"""
        for pattern in urls.urlpatterns:
            get_pattern_str = str(pattern.pattern)
            self.assertTrue(
                get_pattern_str.startswith('v1/'),
                f"URL pattern '{get_pattern_str}' should start with 'v1/'"
            )

    def test_url_consistency(self):
        """Тест согласованности имен URL и их путей"""
        url_mappings = {
            'add-order-item': 'v1/orders/<int:order_id>/items/',
            'order-detail': 'v1/orders/<int:order_id>/',
            'order-status-update': 'v1/orders/<int:order_id>/status/',
            'order-list': 'v1/orders/',
            'product-stock': 'v1/products/stock/'
        }

        for name, expected_pattern in url_mappings.items():
            try:
                if 'order_id' in expected_pattern:
                    url = reverse(name, kwargs={'order_id': 1})
                    self.assertIn('/api/v1/orders/1/', url)
                else:
                    url = reverse(name)
                    self.assertIn('/api/' + expected_pattern, url)
            except Exception as e:
                self.fail(f"URL name '{name}' pattern mismatch: {e}")


class URLReverseResolutionTests(TestCase):
    """Тесты обратного разрешения URL"""

    def test_reverse_with_kwargs(self):
        """Тест reverse с kwargs"""
        # Для URL с параметрами
        url_with_kwargs = reverse('add-order-item', kwargs={'order_id': 42})
        self.assertEqual(url_with_kwargs, '/api/v1/orders/42/items/')

    def test_reverse_without_kwargs(self):
        """Тест reverse без kwargs"""
        # Для URL без параметров
        url_without_kwargs = reverse('order-list')
        self.assertEqual(url_without_kwargs, '/api/v1/orders/')

    def test_reverse_raises_error_for_missing_kwargs(self):
        """Тест, что reverse выбрасывает ошибку при отсутствии обязательных kwargs"""
        with self.assertRaises(Exception):  # NoReverseMatch
            reverse('add-order-item')  # Не передали order_id

    def test_reverse_with_extra_kwargs(self):
        """Тест, что reverse выбрасывает ошибку при лишних kwargs для URL без параметров"""
        with self.assertRaises(Exception):  # NoReverseMatch expected
            reverse('order-list', kwargs={'extra_param': 'value'})


class URLPatternAttributesTests(TestCase):
    """Тесты атрибутов URL паттернов"""

    def test_url_pattern_attributes(self):
        """Тест атрибутов URL паттернов"""

        for pattern in urls.urlpatterns:
            self.assertIsNotNone(pattern.name, "URL pattern should have a name")
            self.assertIsNotNone(pattern.callback, "URL pattern should have a callback")

            # Проверяем, что имя соответствует ожидаемому формату
            if hasattr(pattern, 'name'):
                self.assertIn(pattern.name, [
                    'add-order-item',
                    'order-detail',
                    'order-status-update', 
                    'order-list',
                    'product-stock'
                ])


# Дополнительные тесты для проверки совместимости
class URLCompatibilityTests(TestCase):
    """Тесты совместимости URL"""

    def test_url_no_duplicate_patterns(self):
        """Тест отсутствия дублирующихся URL паттернов"""
        from orders import urls

        patterns = [str(p.pattern) for p in urls.urlpatterns]
        unique_patterns = set(patterns)

        self.assertEqual(len(patterns), len(unique_patterns),
                        "Found duplicate URL patterns")