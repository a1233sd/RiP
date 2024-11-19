from django.contrib import admin

from .models import *

admin.site.register(Student)
admin.site.register(Decree)
admin.site.register(StudentDecree)
admin.site.register(Reprimand)
