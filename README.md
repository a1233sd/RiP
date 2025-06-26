# R_and_P (Система управления студентами и приказами)

## Описание проекта
**R_and_P** — это веб-приложение для управления студентами и административными приказами, построенное на Django REST Framework. Система предназначена для учебных заведений и позволяет управлять базой данных студентов, создавать и обрабатывать административные приказы, а также вести учет дисциплинарных взысканий.

### Основные возможности
- 👨‍🎓 **Управление студентами**: создание, редактирование, удаление записей студентов  
- 📋 **Система приказов**: создание, формирование и обработка административных приказов  
- ⚖️ **Дисциплинарные меры**: ведение учета выговоров и взысканий  
- 🔐 **Система аутентификации**: регистрация, авторизация и управление пользователями  
- 🖼️ **Загрузка изображений**: поддержка фотографий студентов через MinIO  
- 📊 **API-документация**: автоматическая генерация документации через Swagger  

## Технологический стек

### Backend (Python/Django)
    # Основные технологии
    Django==4.2.7               # Основной веб-фреймворк  
    djangorestframework==3.14.0 # REST API  
    drf-yasg==1.21.7            # Swagger-документация  
    django-redis==5.4.0         # Кэширование и сессии  

### База данных и хранилище
- **PostgreSQL 16.0** — основная база данных  
- **Redis** — кэширование и управление сессиями  
- **MinIO** — хранение файлов и изображений  

### Инфраструктура
- **Docker & Docker Compose** — контейнеризация  
- **Nginx** — обратный прокси-сервер  
- **pgAdmin** — администрирование базы данных  

## Структура проекта
    R_and_P/
    ├── app/                    # Основное Django-приложение
    │   ├── models.py           # Модели данных (Student, Decree, Reprimand)
    │   ├── views.py            # API-endpoints и бизнес-логика
    │   ├── serializers.py      # DRF-сериализаторы
    │   ├── permissions.py      # Разрешения и права доступа
    │   ├── urls.py             # URL-маршруты
    │   ├── utils.py            # Вспомогательные функции
    │   ├── redis.py            # Конфигурация Redis
    │   └── management/         # Django-команды
    ├── lab4/                   # Конфигурация Django-проекта
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── docker-compose.yml      # Контейнеры
    ├── Dockerfile              # Образ Django-приложения
    ├── requirements.txt        # Python-зависимости
    ├── nginx.conf              # Конфигурация Nginx
    └── servers.json            # Настройки pgAdmin  

## Модели данных

### Student (Студент)
    class Student(models.Model):
        name = models.CharField(max_length=100, verbose_name="ФИО")
        course = models.TextField(max_length=500, verbose_name="Курс")
        status = models.IntegerField(choices=STATUS_CHOICES, default=1)
        image = models.ImageField(verbose_name="Фото", blank=True, null=True)
        group = models.CharField(max_length=50, verbose_name="Группа")
        number = models.CharField(max_length=50, verbose_name="Номер")

### Decree (Приказ)
    class Decree(models.Model):
        status = models.IntegerField(choices=STATUS_CHOICES, default=1)
        date_created = models.DateTimeField(verbose_name="Дата создания")
        date_formation = models.DateTimeField(verbose_name="Дата формирования")
        date_complete = models.DateTimeField(verbose_name="Дата завершения")
        owner = models.ForeignKey(User, related_name='owner')
        moderator = models.ForeignKey(User, related_name='moderator')

### Reprimand (Выговор)
    class Reprimand(models.Model):
        student = models.ForeignKey(Student, related_name="reprimands")
        reason = models.TextField(verbose_name="Причина", max_length=500)
        date_issued = models.DateField(verbose_name="Дата вынесения")
        status = models.IntegerField(choices=STATUS_CHOICES, default=1)
        issued_by = models.ForeignKey(User, verbose_name="Кем вынесен")

## API Endpoints

### Управление студентами
    GET    /api/students/                     # Список студентов
    GET    /api/students/{id}/                # Информация о студенте
    POST   /api/students/create/              # Создание студента
    PUT    /api/students/{id}/update/         # Обновление студента
    DELETE /api/students/{id}/delete/         # Удаление студента
    POST   /api/students/{id}/update_image/   # Загрузка фото

### Управление приказами
    GET    /api/decrees/                      # Список приказов
    GET    /api/decrees/{id}/                 # Информация о приказе
    PUT    /api/decrees/{id}/update/          # Обновление приказа
    PUT    /api/decrees/{id}/update_status_user/   # Формирование приказа
    PUT    /api/decrees/{id}/update_status_admin/  # Завершение/отклонение
    DELETE /api/decrees/{id}/delete/          # Удаление приказа

### Управление выговорами
    POST   /api/students/{id}/add_reprimand/  # Добавление выговора
    GET    /api/students/{id}/reprimands/     # Список выговоров студента

### Аутентификация
    POST   /api/users/register/               # Регистрация
    POST   /api/users/login/                  # Вход
    POST   /api/users/logout/                 # Выход
    PUT    /api/users/{id}/update/            # Обновление профиля

## Установка и запуск

### Требования
- Docker и Docker Compose  
- Python 3.8+ (для локальной разработки)  

### Быстрый старт с Docker
1. Клонировать репозиторий  
    git clone https://github.com/a1233sd/R_and_P.git  
    cd R_and_P  
    git checkout Moderator  
2. Собрать и запустить контейнеры  
    docker-compose up --build  
3. Доступ к сервисам  
    - Django API: http://localhost:8000  
    - Swagger:   http://localhost:8000/swagger/  
    - pgAdmin:   http://localhost:5050  
    - MinIO:     http://localhost:9001  

### Локальная разработка
1. Создать виртуальную среду  
    python -m venv venv  
    source venv/bin/activate  # Linux/Mac  
    venv\Scripts\activate     # Windows  
2. Установить зависимости  
    pip install -r req.txt  
3. Настроить базу данных  
    python manage.py makemigrations  
    python manage.py migrate  
    python manage.py fill_db     # Заполнение тестовыми данными  
4. Создать суперпользователя  
    python manage.py createsuperuser  
5. Запуск сервера разработки  
    python manage.py runserver  

## Конфигурация

### Переменные окружения (settings.py)
    # База данных
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': 'postgres',
            'HOST': 'pgdb',
            'PORT': '5432'
        }
    }

    # Redis для кэширования
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://redis",
        }
    }

    # MinIO для хранения файлов
    AWS_STORAGE_BUCKET_NAME = 'images'
    AWS_ACCESS_KEY_ID = 'minio'
    AWS_SECRET_ACCESS_KEY = 'minio123'
    AWS_S3_ENDPOINT_URL = "http://minio:9000"

## Система разрешений
Проект использует пользовательские разрешения:  
- **IsAuthenticated** — доступ только после аутентификации  
- **IsModerator** — доступ только модераторам  

    # Пример во views.py
    @permission_classes([IsAuthenticated])
    def search_decrees(request):
        ...

    @permission_classes([IsModerator])
    def create_student(request):
        ...

## Тестирование API
Коллекция Postman `Lab3.postman_collection.json` содержит готовые запросы.  
Импортируйте файл в Postman и укажите базовый URL `http://localhost:8000`.

## Производственное развертывание

### Docker Compose
    docker-compose run --build
