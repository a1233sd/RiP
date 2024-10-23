import random

from django.core.management.base import BaseCommand
from minio import Minio

from ...models import *
from .utils import random_date, random_timedelta


def add_users():
    User.objects.create_user("user", "user@user.com", "1234", first_name="user", last_name="user")
    User.objects.create_superuser("root", "root@root.com", "1234", first_name="root", last_name="root")

    for i in range(1, 10):
        User.objects.create_user(f"user{i}", f"user{i}@user.com", "1234", first_name=f"user{i}", last_name=f"user{i}")
        User.objects.create_superuser(f"root{i}", f"root{i}@root.com", "1234", first_name=f"user{i}", last_name=f"user{i}")

    print("Пользователи созданы")


def add_students():
    Student.objects.create(
        name="Хомякова Дарья Артёмовна",
        course=2,
        group="ИУ1-31Б",
        number="23У023",
        image="1.png"
    )

    Student.objects.create(
        name="Грибова Малика Максимовна",
        course=3,
        group="РК2-51Б",
        number="22Р034",
        image="2.png"
    )

    Student.objects.create(
        name="Любимов Матвей Степанович",
        course=1,
        group="Э6-11Б",
        number="24Э143",
        image="3.png"
    )

    Student.objects.create(
        name="Зубков Андрей Иванович",
        course=3,
        group="ИУ5Ц-71Б",
        number="21Ц010",
        image="4.png"
    )

    Student.objects.create(
        name="Никонов Михаил Леонидович",
        course=3,
        group="ЮР2-51Б",
        number="22Ю054",
        image="5.png"
    )

    Student.objects.create(
        name="Горбин Никита Петрович",
        course=4,
        group="СМ8-72Б",
        number="21С089",
        image="6.png"
    )

    client = Minio("minio:9000", "minio", "minio123", secure=False)
    client.fput_object('images', '1.png', "app/static/images/1.png")
    client.fput_object('images', '2.png', "app/static/images/2.png")
    client.fput_object('images', '3.png', "app/static/images/3.png")
    client.fput_object('images', '4.png', "app/static/images/4.png")
    client.fput_object('images', '5.png', "app/static/images/5.png")
    client.fput_object('images', '6.png', "app/static/images/6.png")
    client.fput_object('images', 'default.png', "app/static/images/default.png")

    print("Услуги добавлены")


def add_decrees():
    users = User.objects.filter(is_staff=False)
    moderators = User.objects.filter(is_staff=True)

    if len(users) == 0 or len(moderators) == 0:
        print("Заявки не могут быть добавлены. Сначала добавьте пользователей с помощью команды add_users")
        return

    students = Student.objects.all()

    for _ in range(30):
        status = random.randint(2, 5)
        owner = random.choice(users)
        add_decree(status, students, owner, moderators)

    add_decree(1, students, users[0], moderators)
    add_decree(2, students, users[0], moderators)

    print("Заявки добавлены")


def add_decree(status, students, owner, moderators):
    decree = Decree.objects.create()
    decree.status = status

    if decree.status in [3, 4]:
        decree.date_complete = random_date()
        decree.date_formation = decree.date_complete - random_timedelta()
        decree.date_created = decree.date_formation - random_timedelta()
    else:
        decree.date_formation = random_date()
        decree.date_created = decree.date_formation - random_timedelta()

    decree.owner = owner
    decree.moderator = random.choice(moderators)

    for student in random.sample(list(students), 3):
        item = StudentDecree(
            decree=decree,
            student=student,
            value=random.randint(1, 10)
        )
        item.save()

    decree.save()


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        add_users()
        add_students()
        add_decrees()
