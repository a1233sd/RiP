# models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Студенты
class Students(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )
    name = models.CharField(max_length=255)
    course = models.IntegerField()
    group = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    image = models.CharField(max_length=255, blank=True, null=True)
    debt_count = models.IntegerField(null=True, blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")

    class Meta:
        db_table = 'students'
        constraints = [
            models.UniqueConstraint(fields=['name', 'number'], name='unique_name_number')
        ]

    def __str__(self):
        return self.name


# Заявка 
class Decree(models.Model):
    STATUS_CHOICES = (
        (1, 'Черновик'),
        (2, 'В работе'),
        (3, 'Завершена'),
        (4, 'Отклонена'),
        (5, 'Удалена'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='decree_owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='decree_moderator')

    students = models.ManyToManyField(Students, through='DecreeStudents')

    def __str__(self):
        return f"Заявка №{self.pk} от {self.date_created}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ('-date_created',)
        db_table = "decrees"


# Связь студенты-заявка 
class DecreeStudents(models.Model):
    decree = models.ForeignKey(Decree, on_delete=models.CASCADE, verbose_name="Заявка")
    student = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name="Студент")
    count = models.CharField(verbose_name= "м-м", blank=True, null=True)

    def __str__(self):
        return f"Связь студент {self.student.id} - заявка {self.decree.id}"

    class Meta:
        verbose_name = "Связь студент-заявка"
        verbose_name_plural = "Связи студент-заявка"
        db_table = "decree_students"
        unique_together = ('decree', 'student')
