from django.contrib.auth.models import User
from django.db import models

class Student(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название", blank=True)
    course = models.IntegerField(verbose_name="Курс", blank=True, null=True)  # Сделаем поле course допускающим NULL
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", null=True, blank=True)

    group = models.CharField(max_length=50, blank=True)    # Добавлен max_length
    number = models.CharField(max_length=50, blank=True)   # Добавлен max_length

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"
        db_table = "students"

class Decree(models.Model):
    STATUS_CHOICES = (
        (1, 'Введён'),
        (2, 'В работе'),
        (3, 'Завершен'),
        (4, 'Отклонен'),
        (5, 'Удален')
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateTimeField(verbose_name="Дата создания", blank=True, null=True)
    date_formation = models.DateTimeField(verbose_name="Дата формирования", blank=True, null=True)
    date_complete = models.DateTimeField(verbose_name="Дата завершения", blank=True, null=True)

    date = models.DateField(verbose_name="Дата", blank=True, null=True)

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Модератор", related_name='moderator', blank=True, null=True)

    def __str__(self):
        return "Приказ №" + str(self.pk)

    class Meta:
        verbose_name = "Приказ"
        verbose_name_plural = "Приказы"
        db_table = "decrees"
        ordering = ('-date_formation', )

class StudentDecree(models.Model):
    student = models.ForeignKey(Student, models.CASCADE, blank=True, null=True)
    decree = models.ForeignKey(Decree, models.CASCADE, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "student_decree"
        unique_together = ('student', 'decree')
 