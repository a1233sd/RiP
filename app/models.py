from django.db import models
from django.contrib.auth.models import User

# Студенты
class Students(models.Model):
    name = models.CharField(max_length=255)
    course = models.IntegerField()
    group = models.CharField(max_length=50)
    number = models.CharField(max_length=50)
    image = models.CharField(max_length=255)
    debt_count = models.IntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'students'
        constraints = [
            models.UniqueConstraint(fields=['name', 'number'], name='unique_name_number')
        ]

    def __str__(self):
        return self.name


# Заявка (аналог проводки)
class Decree(models.Model):
    STATUS_CHOICES = (
        (1, 'Черновик'),
        (2, 'В работе'),
        (3, 'Завершена'),
        (4, 'Отклонена'),
        (5, 'Удалена'),
    )

    status = models.IntegerField(choices=STATUS_CHOICES, default=1, verbose_name="Статус")
    date_created = models.DateField(auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, related_name='decree_owner')
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Модератор", null=True, related_name='decree_moderator')

    students = models.ManyToManyField(Students, through='DecreeStudents')

    def __str__(self):
        return f"Заявка №{self.pk} от {self.date_created}"

    def get_students(self):
        return [
            setattr(item.student, "count", item.count) or item.student
            for item in DecreeStudents.objects.filter(decree=self)
        ]

    def get_status(self):
        return dict(self.STATUS_CHOICES).get(self.status)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ('-date_created',)
        db_table = "decrees"


# Связь студенты-заявка (аналог связи корабль-проводка)
class DecreeStudents(models.Model):
    decree = models.ForeignKey(Decree, on_delete=models.CASCADE, verbose_name="Заявка")
    student = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name="Студент")
    count = models.IntegerField(default=1)

    def __str__(self):
        return f"Связь студент {self.student.id} - заявка {self.decree.id}"

    class Meta:
        verbose_name = "Связь студент-заявка"
        verbose_name_plural = "Связи студент-заявка"
        db_table = "decree_students"
        unique_together = ('decree', 'student')
