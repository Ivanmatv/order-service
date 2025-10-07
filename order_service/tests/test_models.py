from django.test import TestCase
from django.core.exceptions import ValidationError

from orders.models import Order
from .factories import (
    CategoryFactory, CustomerFactory, ProductFactory,
    OrderFactory, OrderItemFactory
)


class CategoryModelTest(TestCase):
    def test_create_category(self):
        """Тест создания категории"""
        category = CategoryFactory(name="Электроника")
        self.assertEqual(category.name, "Электроника")
        self.assertIsNone(category.parent)

    def test_category_str(self):
        """Тест строкового представления категории"""
        category = CategoryFactory(name="Книги")
        self.assertEqual(str(category), "Книги")

    def test_category_hierarchy(self):
        """Тест иерархии категорий"""
        parent = CategoryFactory(name="Parent")
        child = CategoryFactory(name="Child", parent=parent)

        self.assertEqual(child.parent, parent)
        self.assertEqual(parent.children.first(), child)

    def test_category_circular_reference(self):
        """Тест защиты от циклических ссылок"""
        category1 = CategoryFactory(name="Категория 1")
        category2 = CategoryFactory(name="Категория 2", parent=category1)

        # Попытка создать циклическую ссылку
        category1.parent = category2
        with self.assertRaises(ValidationError):
            category1.full_clean()


class CustomerModelTest(TestCase):
    def test_create_customer(self):
        """Тест создания клиента"""
        customer = CustomerFactory(
            name="Иван Матвеев",
            email="ivan@example.com"
        )
        self.assertEqual(customer.name, "Иван Матвеев")
        self.assertEqual(customer.email, "ivan@example.com")

    def test_customer_str(self):
        """Тест строкового представления клиента"""
        customer = CustomerFactory(name="Иван Матвеев")
        self.assertEqual(str(customer), "Иван Матвеев")


class ProductModelTest(TestCase):
    def test_create_product(self):
        """Тест создания товара"""
        product = ProductFactory(
            name="Ноутбук",
            quantity=5,
            price=999.99
        )
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.quantity, 5)
        self.assertEqual(product.price, 999.99)
        self.assertTrue(product.is_active)

    def test_product_stock_properties(self):
        """Тест свойств наличия товара"""
        # Товар в наличии
        product_in_stock = ProductFactory(quantity=15)
        self.assertTrue(product_in_stock.in_stock)
        self.assertFalse(product_in_stock.low_stock)

        # Товар с низким запасом
        product_low_stock = ProductFactory(quantity=5)
        self.assertTrue(product_low_stock.in_stock)
        self.assertTrue(product_low_stock.low_stock)

        # Товара нет в наличии
        product_out_of_stock = ProductFactory(quantity=0)
        self.assertFalse(product_out_of_stock.in_stock)
        self.assertFalse(product_out_of_stock.low_stock)

    def test_product_negative_quantity(self):
        """Тест валидации отрицательного количества"""
        product = ProductFactory.build(quantity=-5)
        with self.assertRaises(ValidationError):
            product.full_clean()


class OrderModelTest(TestCase):
    def test_create_order(self):
        """Тест создания заказа"""
        order = OrderFactory()
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.total_amount, 0)

    def test_order_str(self):
        """Тест строкового представления заказа"""
        customer = CustomerFactory(name="Тестовый покупатель")
        order = OrderFactory(customer=customer)
        self.assertIn("Тестовый покупатель", str(order))
        self.assertIn("pending", str(order))

    def test_order_total_calculation(self):
        """Тест расчета общей суммы заказа"""
        order = OrderFactory()
        product1 = ProductFactory(price=100)
        product2 = ProductFactory(price=200)

        OrderItemFactory(order=order, product=product1, quantity=2, unit_price=100)
        OrderItemFactory(order=order, product=product2, quantity=1, unit_price=200)

        # Пересчитываем сумму
        order.save()

        self.assertEqual(order.total_amount, 400)  # 2*100 + 1*200


class OrderItemModelTest(TestCase):
    def test_create_order_item(self):
        """Тест создания позиции заказа"""
        order_item = OrderItemFactory(quantity=3)
        self.assertEqual(order_item.quantity, 3)
        self.assertEqual(order_item.total_price, order_item.unit_price * 3)

    def test_order_item_validation(self):
        """Тест валидации позиции заказа"""
        product = ProductFactory(quantity=15)
        order_item = OrderItemFactory(product=product, quantity=10)

        try:
            order_item.full_clean()
        except ValidationError:
            self.fail("OrderItem validation failed when it should have passed")

        product2 = ProductFactory(quantity=5)
        invalid_order_item = OrderItemFactory.build(
            order=order_item.order, 
            product=product2, 
            quantity=10
        )
        with self.assertRaises(ValidationError):
            invalid_order_item.full_clean()

    def test_unique_order_product_constraint(self):
        """Тест уникальности товара в заказе"""
        order = OrderFactory()
        product = ProductFactory()

        OrderItemFactory(order=order, product=product)

        # Попытка добавить тот же товар второй раз
        with self.assertRaises(Exception):
            OrderItemFactory(order=order, product=product)