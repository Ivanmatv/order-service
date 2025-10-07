# order-service# Order Service

## Описание проекта

**Order Service** — это веб-приложение на основе Django и Django REST Framework для управления заказами, товарами, категориями и клиентами. Проект предоставляет REST API для выполнения операций с заказами, таких как создание, обновление статуса, добавление товаров в заказ, а также просмотр информации о запасах товаров. Приложение включает административную панель для удобного управления данными.

Проект разработан с учетом современных практик веб-разработки, включая тестирование, логирование, аутентификацию и пагинацию. Поддерживается локализация, что делает приложение готовым к использованию на разных языках.

## Основные функции

- **Управление заказами**:
  - Создание и просмотр заказов
  - Добавление/обновление товаров в заказах
  - Обновление статуса заказов
- **Управление товарами**:
  - Просмотр запасов товаров
  - Фильтрация товаров по низкому запасу или отсутствию в наличии
- **Управление категориями**:
  - Иерархическая структура категорий
  - Защита от циклических зависимостей
- **Управление клиентами**:
  - Хранение информации о клиентах (имя, email, телефон, адрес)
- **Административная панель**:
  - Удобный интерфейс для управления всеми моделями
  - Отображение статуса товаров и заказов с цветовой индикацией
  - Действия для массового обновления (например, активация/деактивация товаров)
- **Аутентификация и авторизация**:
  - Поддержка токенов (JWT и Django REST Framework Token Authentication)
  - Ограничение доступа к API только для аутентифицированных пользователей
- **Тестирование**:
  - Полный набор тестов для моделей, сериализаторов, представлений и URL
- **Логирование**:
  - Логирование операций и ошибок в файл и консоль

## Технологии

- **Python 3.8+**
- **Django 4.x**
- **Django REST Framework**
- **SQLite** (для разработки) / **PostgreSQL** (для продакшена)
- **Simple JWT** для аутентификации
- **Factory Boy** для генерации тестовых данных
- **Logging** для записи логов
- **dotenv** для управления конфигурацией

## Установка

### Требования

- Python 3.8 или выше
- pip
- Виртуальное окружение (рекомендуется)
- PostgreSQL (для продакшена, опционально)

### Инструкции

1. **Клонируйте репозиторий**:
   ```bash
   git clone <repository-url>
   cd order_service
   ```

2. **Создайте и активируйте виртуальное окружение**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/MacOS
   venv\Scripts\activate     # Windows
   ```

3. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Создайте файл `.env`** в корне проекта и настройте переменные окружения:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   DB_ENGINE=django.db.backends.postgresql
   DB_NAME=postgres
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   DB_HOST=localhost
   DB_PORT=5432
   ```

   Для генерации `SECRET_KEY` можно использовать:
   ```python
   from django.core.management.utils import get_random_secret_key
   print(get_random_secret_key())
   ```

5. **Примените миграции**:
   ```bash
   python manage.py migrate
   ```

6. **Создайте суперпользователя (для доступа к админ-панели)**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Запустите сервер разработки**:
   ```bash
   python manage.py runserver
   ```

   Приложение будет доступно по адресу: `http://localhost:8000`

## Использование

### API

API доступно по адресу `/api/v1/`. Основные эндпоинты:

- **GET /api/v1/orders/**: Получение списка заказов (с пагинацией и фильтрацией по статусу)
- **GET /api/v1/orders/<order_id>/**: Получение деталей заказа
- **POST /api/v1/orders/<order_id>/items/**: Добавление/обновление товаров в заказе
- **PATCH /api/v1/orders/<order_id>/status/**: Обновление статуса заказа
- **GET /api/v1/products/stock/**: Получение информации о запасах товаров (с фильтрацией по низкому запасу или отсутствию)

**Аутентификация**:

Все API-запросы требуют заголовок `Authorization`. Вы можете использовать:

1. **JWT-токен**:
   - Получите токен через `/api/auth/token/`:
     ```bash
     curl -X POST http://localhost:8000/api/auth/token/ \
       -d "username=<your-username>&password=<your-password>"
     ```
   - Используйте токен в заголовке: `Authorization: Bearer <your-jwt-token>`

2. **Токен Django REST Framework**:
   - Получите токен через `/api/auth/api-token-auth/`:
     ```bash
     curl -X POST http://localhost:8000/api/auth/api-token-auth/ \
       -d "username=<your-username>&password=<your-password>"
     ```
   - Используйте токен в заголовке: `Authorization: Token <your-token>`

3. **Обновление JWT-токена**:
   - Если у вас есть refresh-токен, обновите access-токен:
     ```bash
     curl -X POST http://localhost:8000/api/auth/token/refresh/ \
       -d "refresh=<your-refresh-token>"
     ```
## Эндпоинты

### 1. Получение списка заказов
- **URL**: `/api/v1/orders/`
- **Метод**: GET
- **Описание**: Возвращает список заказов с пагинацией и возможностью фильтрации по статусу.
- **Параметры запроса**:
  - `status` (опционально): Фильтр по статусу заказа (например, `pending`, `processing`, `shipped`, `delivered`, `cancelled`).
  - `page` (опционально, по умолчанию `1`): Номер страницы.
  - `page_size` (опционально, по умолчанию `20`): Количество записей на странице.
- **Заголовки**:
  - `Authorization: Bearer <your-jwt-token>`
- **Пример запроса**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/orders/?status=pending&page=1&page_size=10 \
    -H "Authorization: Bearer <your-jwt-token>"
  ```
- **Пример ответа**:
  ```json
  {
    "orders": [
      {
        "id": 1,
        "customer_name": "Иван Иванов",
        "customer_email": "ivan@example.com",
        "status": "pending",
        "status_display": "Ожидает",
        "total_amount": "400.00",
        "notes": "",
        "created_at": "2025-10-07T12:00:00Z",
        "updated_at": "2025-10-07T12:00:00Z",
        "items": [
          {
            "id": 1,
            "product_id": 1,
            "product_name": "Ноутбук",
            "quantity": 2,
            "unit_price": "200.00",
            "total_price": "400.00"
          }
        ]
      }
    ],
    "page": 1,
    "page_size": 10,
    "total_orders": 1,
    "has_next": false
  }
  ```
- **Коды ответа**:
  - `200 OK`: Успешный запрос.
  - `401 Unauthorized`: Отсутствует или неверный токен.
  - `500 Internal Server Error`: Ошибка сервера.

### 2. Получение деталей заказа
- **URL**: `/api/v1/orders/<order_id>/`
- **Метод**: GET
- **Описание**: Возвращает детали конкретного заказа, включая связанные товары.
- **Параметры пути**:
  - `order_id`: ID заказа (целое число).
- **Заголовки**:
  - `Authorization: Bearer <your-jwt-token>`
- **Пример запроса**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/orders/1/ \
    -H "Authorization: Bearer <your-jwt-token>"
  ```
- **Пример ответа**:
  ```json
  {
    "id": 1,
    "customer_name": "Иван Иванов",
    "customer_email": "ivan@example.com",
    "status": "pending",
    "status_display": "Ожидает",
    "total_amount": "400.00",
    "notes": "",
    "created_at": "2025-10-07T12:00:00Z",
    "updated_at": "2025-10-07T12:00:00Z",
    "items": [
      {
        "id": 1,
        "product_id": 1,
        "product_name": "Ноутбук",
        "quantity": 2,
        "unit_price": "200.00",
        "total_price": "400.00"
      }
    ]
  }
  ```
- **Коды ответа**:
  - `200 OK`: Успешный запрос.
  - `404 Not Found`: Заказ не найден.
  - `401 Unauthorized`: Отсутствует или неверный токен.
  - `500 Internal Server Error`: Ошибка сервера.

### 3. Добавление/обновление товара в заказе
- **URL**: `/api/v1/orders/<order_id>/items/`
- **Метод**: POST
- **Описание**: Добавляет новый товар в заказ или обновляет количество существующего товара. Уменьшает количество товара на складе.
- **Параметры пути**:
  - `order_id`: ID заказа (целое число).
- **Тело запроса**:
  - `product_id` (обязательно): ID товара (целое число, >= 1).
  - `quantity` (обязательно): Количество товара (целое число, >= 1).
- **Заголовки**:
  - `Authorization: Bearer <your-jwt-token>`
  - `Content-Type: application/json`
- **Пример запроса**:
  ```bash
  curl -X POST http://localhost:8000/api/v1/orders/1/items/ \
    -H "Authorization: Bearer <your-jwt-token>" \
    -H "Content-Type: application/json" \
    -d '{"product_id": 1, "quantity": 2}'
  ```
- **Пример ответа**:
  ```json
  {
    "success": true,
    "message": "Product added to order successfully",
    "order_total": 400.0,
    "action": "created"
  }
  ```
- **Коды ответа**:
  - `200 OK`: Товар успешно добавлен или обновлен.
  - `400 Bad Request`: Неверные данные (например, недостаточно товара на складе, несуществующий продукт).
  - `401 Unauthorized`: Отсутствует или неверный токен.
  - `403 Forbidden`: Недостаточно прав.
  - `404 Not Found`: Заказ или товар не найден.
  - `500 Internal Server Error`: Ошибка сервера.

### 4. Обновление статуса заказа
- **URL**: `/api/v1/orders/<order_id>/status/`
- **Метод**: PATCH
- **Описание**: Обновляет статус заказа (например, `pending`, `processing`, `shipped`, `delivered`, `cancelled`).
- **Параметры пути**:
  - `order_id`: ID заказа (целое число).
- **Тело запроса**:
  - `status` (обязательно): Новый статус заказа (должен быть из `Order.Status.choices`).
- **Заголовки**:
  - `Authorization: Bearer <your-jwt-token>`
  - `Content-Type: application/json`
- **Пример запроса**:
  ```bash
  curl -X PATCH http://localhost:8000/api/v1/orders/1/status/ \
    -H "Authorization: Bearer <your-jwt-token>" \
    -H "Content-Type: application/json" \
    -d '{"status": "processing"}'
  ```
- **Пример ответа**:
  ```json
  {
    "success": true,
    "message": "Order status updated to processing",
    "order_id": 1,
    "old_status": "pending",
    "new_status": "processing"
  }
  ```
- **Коды ответа**:
  - `200 OK`: Статус успешно обновлен.
  - `400 Bad Request`: Неверный статус.
  - `401 Unauthorized`: Отсутствует или неверный токен.
  - `403 Forbidden`: Недостаточно прав.
  - `404 Not Found`: Заказ не найден.
  - `500 Internal Server Error`: Ошибка сервера.

### 5. Получение информации о запасах товаров
- **URL**: `/api/v1/products/stock/`
- **Метод**: GET
- **Описание**: Возвращает список активных товаров с информацией о запасах. Поддерживает фильтрацию по низкому запасу или отсутствию товаров.
- **Параметры запроса**:
  - `low_stock` (опционально): `true` для фильтрации товаров с низким запасом (`0 < quantity <= 10`).
  - `out_of_stock` (опционально): `true` для фильтрации товаров, отсутствующих на складе (`quantity = 0`).
- **Заголовки**:
  - `Authorization: Bearer <your-jwt-token>`
- **Пример запроса (все товары)**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/products/stock/ \
    -H "Authorization: Bearer <your-jwt-token>"
  ```
- **Пример запроса (товары с низким запасом)**:
  ```bash
  curl -X GET http://localhost:8000/api/v1/products/stock/?low_stock=true \
    -H "Authorization: Bearer <your-jwt-token>"
  ```
- **Пример ответа**:
  ```json
  {
    "products": [
      {
        "id": 1,
        "name": "Ноутбук",
        "quantity": 5,
        "price": "999.99",
        "in_stock": true,
        "low_stock": true,
        "category_name": "Электроника",
        "is_active": true
      }
    ],
    "total_count": 1,
    "low_stock_count": 1,
    "out_of_stock_count": 0
  }
  ```
- **Коды ответа**:
  - `200 OK`: Успешный запрос.
  - `401 Unauthorized`: Отсутствует или неверный токен.
  - `403 Forbidden`: Недостаточно прав.
  - `500 Internal Server Error`: Ошибка сервера.

### Админ-панель

Доступна по адресу `/admin/`. Войдите с учетной записью суперпользователя для управления:

- Категориями (иерархическая структура)
- Клиентами
- Товарами (с возможностью редактирования количества, цены и статуса активности)
- Заказами и их позициями

## Тестирование

Проект включает полный набор тестов для проверки функциональности.

Запустите тесты:
```bash
python manage.py test
```

Тесты покрывают:
- Модели (валидация, создание, расчеты)
- Сериализаторы (валидация данных)
- Представления (API-запросы)
- URL (корректность маршрутов)

## Структура проекта

```
order_service/
├── orders/
│   ├── admin.py        # Конфигурация админ-панели
│   ├── apps.py        # Конфигурация приложения
│   ├── factories.py   # Фабрики для тестов
│   ├── models.py      # Модели данных
│   ├── serializers.py # Сериализаторы для API
│   ├── tests/         # Тесты
│   ├── urls.py        # Маршруты API
│   └── views.py       # Представления API
├── order_service/
│   ├── settings.py    # Настройки проекта
│   ├── urls.py        # Основные маршруты
│   └── wsgi.py        # WSGI конфигурация
├── manage.py          # Управление Django
├── requirements.txt   # Зависимости
└── README.md          # Документация
```

## Логирование

Логи записываются в:
- Консоль (уровень DEBUG)
- Файл `logs/django.log` (уровень INFO)

## Продакшен

Для продакшена:
1. Установите `DEBUG=False` в `.env`.
2. Настройте PostgreSQL вместо SQLite.
3. Используйте сервер, такой как Gunicorn, и настройте Nginx как обратный прокси.

## Лицензия

Проект распространяется под лицензией MIT.