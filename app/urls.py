from django.urls import path
from .views import *

urlpatterns = [

    # Набор методов для услуг
  
    # GET список с фильтрацией
    # Возвращает список услуг с возможностью фильтрации, включая id заявки-черновика пользователя и количество услуг в заявке
    path('api/students/', search_students, name='search_students'),  # GET

    # GET одна запись
    # Возвращает информацию о конкретной услуге по id
    path('api/students/<int:student_id>/', get_student_by_id, name='get_student_by_id'),  # GET

    # POST добавление (без изображения)
    # Создаёт новую услугу без изображения
    path('api/students/create/', create_student, name='create_student'),  # POST

    # PUT изменение
    # Обновляет данные услуги по id
    path('api/students/<int:student_id>/update/', update_student, name='update_student'),  # PUT

    # POST добавление изображения
    # Добавляет или обновляет изображение для услуги по id
    path('api/students/<int:student_id>/update_image/', update_student_image, name='update_student_image'),  # POST

    # DELETE удаление
    # Удаляет услугу по id. Удаление изображения встроено в метод удаления услуги
    path('api/students/<int:student_id>/delete/', delete_student, name='delete_student'),  # DELETE

    # POST добавление в заявку-черновик
    # Добавляет услугу в заявку-черновик. Создаётся пустая заявка с автоматически установленными полями
    path('api/students/<int:student_id>/add_to_decree/', add_student_to_decree, name='add_student_to_decree'),  # POST

    # Набор методов для заявок

    # GET список заявок с фильтрацией по диапазону даты формирования и статусу
    # Возвращает список заявок, исключая удалённые и черновики, с фильтрацией
    path('api/decrees/', search_decrees, name='search_decrees'),  # GET

    # GET одна запись заявки
    # Возвращает информацию о конкретной заявке по id, включая список её услуг с изображениями
    path('api/decrees/<int:decree_id>/', get_decree_by_id, name='get_decree_by_id'),  # GET

    # PUT изменение полей заявки по теме
    # Обновляет поля заявки по id
    path('api/decrees/<int:decree_id>/update/', update_decree, name='update_decree'),  # PUT

    # PUT сформировать заявку создателем
    # Устанавливает дату формирования заявки и изменяет её статус
    path('api/decrees/<int:decree_id>/update_status_user/', update_status_user, name='update_status_user'),  # PUT

    # PUT завершить/отклонить заявку модератором
    # Устанавливает модератора, дату завершения и изменяет статус заявки
    path('api/decrees/<int:decree_id>/update_status_admin/', update_status_admin, name='update_status_admin'),  # PUT

    # DELETE удаление заявки (установка даты формирования)
    # Логически удаляет заявку по id, устанавливая соответствующий статус
    path('api/decrees/<int:decree_id>/delete/', delete_decree, name='delete_decree'),  # DELETE


    # Набор методов для м-м

    # PUT изменение количества/порядка/значения в м-м (без PK м-м)
    # Обновляет данные конкретной услуги в заявке
    path('api/decrees/<int:decree_id>/update_student/<int:student_id>/', update_student_in_decree, name='update_student_in_decree'),  # PUT

    # DELETE удаление из заявки (без PK м-м)
    # Удаляет конкретную услугу из заявки
    path('api/decrees/<int:decree_id>/delete_student/<int:student_id>/', delete_student_from_decree, name='delete_student_from_decree'),  # DELETE

    # ===========================
    # API-маршруты для пользователей
    # ===========================

    # POST регистрация
    # Регистрация нового пользователя
    path('api/users/register/', register, name='api_register'),  # POST

    # POST аутентификация
    # Аутентификация пользователя (логин)
    path('api/users/login/', login_view, name='api_login'),  # POST

    # POST деавторизация
    # Деавторизация пользователя (лог-аут)
    path('api/users/logout/', logout_view, name='api_logout'),  # POST

    # PUT пользователя (личный кабинет)
    # Обновляет данные пользователя по id
    path('api/users/<int:user_id>/update/', update_user, name='api_update_user'),  # PUT
]
