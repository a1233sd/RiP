from django.contrib import admin
from .models import *

# Регистрация модели Students в админке
admin.site.register(Students)
admin.site.register(Decree)
admin.site.register(DecreeStudents)