from django.urls import path
from .views import *

urlpatterns = [
    path('', index),
    path('students/<int:student_id>/', student),
    path('decrees/<int:decree_id>/', decree),
]