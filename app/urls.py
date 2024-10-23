from django.urls import path
from .views import *

urlpatterns = [
    # Набор методов для услуг
    path('api/students/', search_students),  # GET
    path('api/students/<int:student_id>/', get_student_by_id),  # GET
    path('api/students/<int:student_id>/update/', update_student),  # PUT
    path('api/students/<int:student_id>/update_image/', update_student_image),  # POST
    path('api/students/<int:student_id>/delete/', delete_student),  # DELETE
    path('api/students/create/', create_student),  # POST
    path('api/students/<int:student_id>/add_to_decree/', add_student_to_decree),  # POST

    # Набор методов для заявок
    path('api/decrees/', search_decrees),  # GET
    path('api/decrees/<int:decree_id>/', get_decree_by_id),  # GET
    path('api/decrees/<int:decree_id>/update/', update_decree),  # PUT
    path('api/decrees/<int:decree_id>/update_status_user/', update_status_user),  # PUT
    path('api/decrees/<int:decree_id>/update_status_admin/', update_status_admin),  # PUT
    path('api/decrees/<int:decree_id>/delete/', delete_decree),  # DELETE

    # Набор методов для м-м
    path('api/decrees/<int:decree_id>/students/<int:student_id>/', get_student_decree),  # GET
    path('api/decrees/<int:decree_id>/update_student/<int:student_id>/', update_student_in_decree),  # PUT
    path('api/decrees/<int:decree_id>/delete_student/<int:student_id>/', delete_student_from_decree),  # DELETE

    # Набор методов для аутентификации и авторизации
    path("api/users/register/", register),  # POST
    path("api/users/login/", login),  # POST
    path("api/users/logout/", logout),  # POST
    path("api/users/<int:user_id>/update/", update_user)  # PUT
]
