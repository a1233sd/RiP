from django.db import models

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

class Decree(models.Model):
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Черновик')
    students = models.ManyToManyField(Students, through='DecreeStudents')

    def __str__(self):
        return f"Decree {self.id} - {self.status}"

class DecreeStudents(models.Model):
    decree = models.ForeignKey(Decree, on_delete=models.CASCADE)
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)

    class Meta:
        unique_together = ('decree', 'student')  # Составной уникальный ключ
