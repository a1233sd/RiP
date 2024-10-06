from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('students/<int:student_id>/', student, name='student'),
    path('decrees/<int:decree_id>/', view_decree, name='view_decree'),
    path('decree/<int:decree_id>/delete/', delete_decree, name='delete_decree'),
    path('decree/<int:decree_id>/', view_decree, name='view_decree'),
    path('decree/<int:decree_id>/deleted/', view_deleted_decree, name='view_deleted_decree'),
    path('add-to-decree/<int:student_id>/', add_to_decree, name='add_to_decree'),
    path('decree/<int:decree_id>/remove/<int:student_id>/', remove_from_decree, name='remove_from_decree'),
    path('decree/<int:decree_id>/student/<int:student_id>/update-debt/', update_debt, name='update_debt'),  # Добавлен маршрут для обновления долгов
]