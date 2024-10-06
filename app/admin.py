from django.contrib import admin
from .models import Students

# Регистрация модели Students в админке
admin.site.register(Students)
