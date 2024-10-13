# views.py
import requests 
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import *
from .serializers import *

# Вспомогательные функции
def get_draft_decree():
    return Decree.objects.filter(status=1).first()

def get_user():
    return User.objects.filter(is_superuser=False).first()

def get_moderator():
    return User.objects.filter(is_superuser=True).first()


# Студенты API

@api_view(["GET"])
def search_students(request):
    """
    Поиск студентов по имени с фильтрацией и возвращение черновика заявки.
    """
    name = request.GET.get("name", "")
    students = Students.objects.filter(status=1).filter(name__icontains=name) if name else Students.objects.filter(status=1)
    serializer = StudentSerializer(students, many=True)

    draft_decree = get_draft_decree()

    resp = {
        "students": serializer.data,
        "draft_decree": draft_decree.pk if draft_decree else None
    }

    return Response(resp)


@api_view(["GET"])
def get_student_by_id(request, student_id):
    """
    Получение информации о конкретном студенте.
    """
    if not Students.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Students.objects.get(pk=student_id)
    serializer = StudentSerializer(student)

    return Response(serializer.data)


@api_view(["PUT"])
def update_student(request, student_id):
    """
    Обновление информации о студенте.
    """
    if not Students.objects.filter(pk=student_id, status=1).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Students.objects.get(pk=student_id)

    image = request.data.get("image")
    if image is not None:
        student.image = image
        student.save()

    serializer = StudentSerializer(student, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_student(request):
    """
    Создание нового студента без изображения.
    """
    student = Students.objects.create(
        name=request.data.get("name"),
        course=request.data.get("course"),
        group=request.data.get("group"),
        number=request.data.get("number"),
        image=None,  # Без изображения при создании
        debt_count=request.data.get("debt_count", 0),
        status=1  # Действует по умолчанию
    )

    serializer = StudentSerializer(student)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
def delete_student(request, student_id):
    """
    Логическое удаление студента (смена статуса на 'Удалена').
    """
    if not Students.objects.filter(pk=student_id, status=1).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Students.objects.get(pk=student_id)
    student.status = 2  # 'Удалена'
    student.save()

    serializer = StudentSerializer(student)

    return Response(serializer.data, status=status.HTTP_200_OK)

def add_student_image(request, student_id):
    if not Students.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Students.objects.get(pk=student_id)
    response = requests.get(student.image.replace("localhost", "minio"))

    return HttpResponse(response, content_type="image/png")

@api_view(["POST"])
def update_student_image(request, student_id):
    if not Students.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Students.objects.get(pk=student_id)

    image = request.data.get("image")
    if image is not None:
        student.image = image
        student.save()

    serializer = StudentSerializer(student)

    return Response(serializer.data)

# Заявки (Decree) API

@api_view(["GET"])
def search_decrees(request):
    """
    Получение списка заявок с фильтрацией по статусу и диапазону дат формирования.
    Исключаются удаленные заявки.
    """
    status_filter = request.GET.get("status")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    decrees = Decree.objects.exclude(status=5)  # Исключаем 'Удалена'

    if status_filter:
        decrees = decrees.filter(status=status_filter)

    if start_date and parse_datetime(start_date):
        decrees = decrees.filter(date_formation__gte=parse_datetime(start_date))

    if end_date and parse_datetime(end_date):
        decrees = decrees.filter(date_formation__lte=parse_datetime(end_date))

    serializer = DecreeSerializer(decrees, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def get_decree_by_id(request, decree_id):
    """
    Получение информации о конкретной заявке.
    """
    if not Decree.objects.filter(pk=decree_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree)

    return Response(serializer.data)

@api_view(["PUT"])
def update_decree(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["PUT"])
def form_decree(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 1:  # Проверка, что заявка находится в статусе черновика
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree.status = 2  # Изменение статуса на "В работе"
    decree.date_formation = timezone.now()  # Установка даты формирования
    decree.save()

    serializer = DecreeSerializer(decree, many=False)

    return Response(serializer.data)

@api_view(["PUT"])
def complete_decree(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data.get("status"))

    if request_status not in [3, 4]:  # Только статус "Завершена" или "Отклонена"
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 2:  # Проверка, что заявка находится "В работе"
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Проставляем дату завершения и статус
    decree.date_complete = timezone.now()
    decree.status = request_status

    # Назначаем модератора
    decree.moderator = get_moderator()


    decree.save()

    serializer = DecreeSerializer(decree, many=False)

    return Response(serializer.data)



@api_view(["DELETE"])
def delete_decree(request, decree_id):
    """
    Логическое удаление заявки (смена статуса на 'Удалена').
    """
    if not Decree.objects.filter(pk=decree_id).exclude(status=5).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    user = get_user()

    if decree.owner != user:
        return Response({"detail": "Нет прав для удаления этой заявки."}, status=status.HTTP_403_FORBIDDEN)

    decree.status = 5  # Удалена
    decree.date_complete = timezone.now()
    decree.save()

    return Response(status=status.HTTP_204_NO_CONTENT)



# Связи м-м

@api_view(["DELETE"])
def delete_student_from_decree(request, decree_id, student_id):
    if not DecreeStudents.objects.filter(decree_id=decree_id, student_id=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Удаление студента из заявки
    decree_student = DecreeStudents.objects.get(decree_id=decree_id, student_id=student_id)
    decree_student.delete()

    # Проверка, если после удаления студентов больше нет
    decree = Decree.objects.get(pk=decree_id)
    if DecreeStudents.objects.filter(decree_id=decree_id).count() == 0:
        decree.delete()  # Удаление заявки, если в ней нет студентов
        return Response(status=status.HTTP_204_NO_CONTENT)

    # Возвращаем обновленный список студентов в заявке
    serializer = DecreeSerializer(decree)
    return Response(serializer.data["students"])

@api_view(["PUT"])
def update_student_in_decree(request, decree_id, student_id):
    if not DecreeStudents.objects.filter(decree_id=decree_id, student_id=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree_student = DecreeStudents.objects.get(decree_id=decree_id, student_id=student_id)

    # Обновляем значение количества/параметра
    new_count = request.data.get('count')
    if new_count is not None:
        decree_student.count = new_count
        decree_student.save()

    serializer = DecreeStudentSerializer(decree_student)
    return Response(serializer.data)


# Пользователи API

@api_view(["POST"])
def register(request):
    """
    Регистрация нового пользователя.
    """
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST"])
def login_view(request):
    """
    Аутентификация пользователя.
    """
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(username=serializer.validated_data['username'], password=serializer.validated_data['password'])
    if user is None:
        return Response({"detail": "Неверные учетные данные."}, status=status.HTTP_401_UNAUTHORIZED)


    return Response({"detail": "Успешный вход."}, status=status.HTTP_200_OK)


@api_view(["POST"])
def logout_view(request):
    """
    Деавторизация пользователя.
    """

    return Response({"detail": "Успешный выход."}, status=status.HTTP_200_OK)


@api_view(["PUT"])
def update_user(request, user_id):
    """
    Обновление информации о пользователе.
    """
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = User.objects.get(pk=user_id)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_409_CONFLICT)

    serializer.save()
    return Response(serializer.data, status=status.HTTP_200_OK)


