from django.contrib.auth.models import User
from django.db import models


class Student(models.Model):
    STATUS_CHOICES = (
        (1, 'Действует'),
        (2, 'Удалена'),
    )

    name = models.CharField(max_length=100, verbose_name="Название")
    course = models.TextField(max_length=500, verbose_name="Курс")
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    image = models.ImageField(verbose_name="Фото", blank=True, null=True)

    group = models.CharField(max_length=50, verbose_name="Группа", blank=True, null=True)
    number = models.CharField(max_length=50, verbose_name="Номер", blank=True, null=True)

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

    owner = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Создатель", related_name='owner', null=True)
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, verbose_name="Ректор", related_name='moderator', blank=True, null=True)

    date = models.DateField(blank=True, null=True)
    number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return "Приказ №" + str(self.pk)

    class Meta:
        verbose_name = "Приказ"
        verbose_name_plural = "Приказы"
        db_table = "decrees"
        ordering = ('-date_formation',)


class StudentDecree(models.Model):
    student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, blank=True, null=True)
    decree = models.ForeignKey(Decree, on_delete=models.DO_NOTHING, blank=True, null=True)
    value = models.IntegerField(verbose_name="Поле м-м", default=0)

    def __str__(self):
        return "м-м №" + str(self.pk)

    class Meta:
        verbose_name = "м-м"
        verbose_name_plural = "м-м"
        db_table = "student_decree"
        constraints = [
            models.UniqueConstraint(fields=['student', 'decree'], name="student_decree_constraint")
        ]


class Reprimand(models.Model):
    STATUS_CHOICES = (
        (1, 'Вынесен'),
        (2, 'Аннулирован'),
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name="reprimands",
        verbose_name="Студент"
    )
    reason = models.TextField(verbose_name="Причина", max_length=500)
    date_issued = models.DateField(verbose_name="Дата вынесения", auto_now_add=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    issued_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Кем вынесен"
    )

    def __str__(self):
        return f"Выговор {self.pk} для {self.student.name}"

    class Meta:
        verbose_name = "Выговор"
        verbose_name_plural = "Выговоры"
        db_table = "reprimands"
        ordering = ('-date_issued',)
