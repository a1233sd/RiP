# urls.py

from django.urls import path
from .views import *

urlpatterns = [
    # API-маршруты для студентов
    path('api/students/search/', search_students, name='api_search_students'),  # GET список студентов с фильтрацией 
    path('api/students/<int:student_id>/', get_student_by_id, name='api_get_student'),  # GET одна
    path('api/students/create/', create_student, name='api_create_student'),  # POST добавление без изображения
    path('api/students/<int:student_id>/update/', update_student, name='api_update_student'),  # PUT изменение
    path('api/students/<int:student_id>/delete/', delete_student, name='api_delete_student'),  # DELETE удаление + изображение
    path('api/students/<int:student_id>/add_image/', add_student_image, name='api_add_student_image'),  # POST для добавления/обновления изображения
    path('api/students/<int:student_id>/update_image/', update_student_image, name='api_update_student_image'),  # POST добавление изображения

    # API-маршруты для заявок (Decree)
    path('api/decrees/', search_decrees, name='api_search_decrees'),  # GET список заявок с фильтрацией
    path('api/decrees/<int:decree_id>/', get_decree_by_id, name='api_get_decree'),  # GET конкретной заявки
    path('api/decrees/<int:decree_id>/update/', update_decree, name='api_update_decree'),  # PUT изменение заявки
    path('api/decrees/<int:decree_id>/form/', form_decree, name='api_form_decree'),  # PUT формирование заявки пользователем
    path('api/decrees/<int:decree_id>/complete/', complete_decree, name='api_complete_decree'),  # PUT модератор
    path('api/decrees/<int:decree_id>/delete/', delete_decree, name='api_delete_decree'),  # DELETE удаление заявки

    #Связи м-м
    path('api/decrees/<int:decree_id>/remove_student/<int:student_id>/', delete_student_from_decree, name='api_delete_student_from_decree'),# delete Удаление студента из заявки (без использования PK м-м)
    path('api/decrees/<int:decree_id>/update_student/<int:student_id>/', update_student_in_decree, name='api_update_student_in_decree'),# put Изменение количества/параметра в м-м

    # API-маршруты для пользователей
    path('api/users/register/', register, name='api_register'),  # POST регистрация
    path('api/users/login/', login_view, name='api_login'),  # POST аутентификация
    path('api/users/logout/', logout_view, name='api_logout'),  # POST деавторизация
    path('api/users/<int:user_id>/update/', update_user, name='api_update_user'),  # PUT обновление пользователя
]
