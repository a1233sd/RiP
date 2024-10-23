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
    name = request.GET.get("name", "")

    students = Student.objects.filter(status=1).filter(name__icontains=name)

    serializer = StudentSerializer(students, many=True)

    draft_decree = get_draft_decree()

    resp = {
        "students": serializer.data,
        "students_count": len(serializer.data),
        "draft_decree_id": draft_decree.pk if draft_decree else None
    }

    return Response(resp)


@api_view(["GET"])
def get_student_by_id(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)
    serializer = StudentSerializer(student)

    return Response(serializer.data)


@api_view(["PUT"])
def update_student(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    image = request.data.get("image")
    if image is not None:
        student.image = image
        student.save()

    serializer = StudentSerializer(student, data=request.data, many=False, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
def create_student(request):
    """
    Создание нового студента без изображения.
    """
    student = Student.objects.create(
        name=request.data.get("name"),
        course=request.data.get("course"),
        group=request.data.get("group"),
        number=request.data.get("number"),
        image=None,  # Без изображения при создании
        status=1  # Действует по умолчанию
    )

    serializer = StudentSerializer(student)

    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(["DELETE"])
def delete_student(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)
    student.status = 2
    student.save()

    student = Student.objects.filter(status=1)
    serializer = StudentSerializer(student, many=True)

    return Response(serializer.data)

@api_view(["POST"])
def add_student_to_decree(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    draft_decree = get_draft_decree()

    if draft_decree is None:
        draft_decree = Decree.objects.create()
        draft_decree.date_created = timezone.now()
        draft_decree.owner = get_user()
        draft_decree.save()

    if StudentDecree.objects.filter(decree=draft_decree, student=student).exists():
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    item = StudentDecree.objects.create()
    item.decree = draft_decree
    item.student = student
    item.save()

    serializer = DecreeSerializer(draft_decree)
    return Response(serializer.data["students"])

@api_view(["POST"])
def update_student_image(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

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

    decrees = Decree.objects

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
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree)

    return Response(serializer.data)

@api_view(["PUT"])
def update_decree(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

@api_view(["PUT"])
def update_status_user(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree.status = 2
    decree.date_formation = timezone.now()
    decree.save()

    serializer = DecreeSerializer(decree)

    return Response(serializer.data)


@api_view(["PUT"])
def update_status_admin(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree.status = request_status
    decree.date_complete = timezone.now()
    decree.save()

    serializer = DecreeSerializer(decree)

    return Response(serializer.data)




@api_view(["DELETE"])
def delete_decree(request, decree_id):
    
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree.status = 5
    decree.save()

    return Response(status=status.HTTP_200_OK)

# Связи м-м

@api_view(["DELETE"])
def delete_student_from_decree(request, decree_id, student_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not StudentDecree.objects.filter(decree_id=decree_id, student_id=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = StudentDecree.objects.get(decree_id=decree_id, student_id=student_id)
    item.delete()

    decree = Decree.objects.get(pk=decree_id)

    serializer = DecreeSerializer(decree)
    students = serializer.data["students"]

    if len(students) == 0:
        decree.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(students)

@api_view(["PUT"])
def update_student_in_decree(request, decree_id, student_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not StudentDecree.objects.filter(student_id=student_id, decree_id=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = StudentDecree.objects.get(student_id=student_id, decree_id=decree_id)

    serializer = StudentDecreeSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)

# Пользователи API

@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

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


