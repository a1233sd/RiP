import uuid

from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .management.commands.fill_db import calc
from .permissions import *
from .redis import session_storage
from .serializers import *
from .utils import identity_user, get_session


def get_draft_decree(request):
    user = identity_user(request)

    if user is None:
        return None

    decree = Decree.objects.filter(owner=user).filter(status=1).first()

    return decree


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'query',
            openapi.IN_QUERY,
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
def search_students(request):
    student_name = request.GET.get("student_name", "")

    students = Student.objects.filter(status=1)

    if student_name:
        students = students.filter(name__icontains=student_name)

    serializer = StudentsSerializer(students, many=True)

    draft_decree = get_draft_decree(request)

    resp = {
        "students": serializer.data,
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
@permission_classes([IsModerator])
def update_student(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    serializer = StudentSerializer(student, data=request.data)

    if serializer.is_valid(raise_exception=True):
        serializer.save()

    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsModerator])
def create_student(request):
    serializer = StudentSerializer(data=request.data, partial=False)

    serializer.is_valid(raise_exception=True)

    Student.objects.create(**serializer.validated_data)

    students = Student.objects.filter(status=1)
    serializer = StudentSerializer(students, many=True)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsModerator])
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
@permission_classes([IsAuthenticated])
def add_student_to_decree(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    draft_decree = get_draft_decree(request)

    if draft_decree is None:
        draft_decree = Decree.objects.create()
        draft_decree.date_created = timezone.now()
        draft_decree.owner = identity_user(request)
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
@permission_classes([IsModerator])
def update_student_image(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    image = request.data.get("image")

    if image is None:
        return Response(status.HTTP_400_BAD_REQUEST)

    student.image = image
    student.save()

    serializer = StudentSerializer(student)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_decrees(request):
    status_id = int(request.GET.get("status", 0))
    date_formation_start = request.GET.get("date_formation_start")
    date_formation_end = request.GET.get("date_formation_end")

    decrees = Decree.objects.exclude(status__in=[1, 5])

    user = identity_user(request)
    if not user.is_superuser:
        decrees = decrees.filter(owner=user)

    if status_id > 0:
        decrees = decrees.filter(status=status_id)

    if date_formation_start and parse_datetime(date_formation_start):
        decrees = decrees.filter(date_formation__gte=parse_datetime(date_formation_start))

    if date_formation_end and parse_datetime(date_formation_end):
        decrees = decrees.filter(date_formation__lt=parse_datetime(date_formation_end))

    serializer = DecreesSerializer(decrees, many=True)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_decree_by_id(request, decree_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree)

    return Response(serializer.data)


@swagger_auto_schema(method='put', request_body=DecreeSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_decree(request, decree_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)
    serializer = DecreeSerializer(decree, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_status_user(request, decree_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
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
@permission_classes([IsModerator])
def update_status_admin(request, decree_id):
    if not Decree.objects.filter(pk=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    request_status = int(request.data["status"])

    if request_status not in [3, 4]:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 2:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request_status == 3:
        decree.number = calc()

    decree.status = request_status
    decree.date_complete = timezone.now()
    decree.moderator = identity_user(request)
    decree.save()

    serializer = DecreeSerializer(decree)

    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_decree(request, decree_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    decree = Decree.objects.get(pk=decree_id)

    if decree.status != 1:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    decree.status = 5
    decree.save()

    return Response(status=status.HTTP_200_OK)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_student_from_decree(request, decree_id, student_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not StudentDecree.objects.filter(decree_id=decree_id, student_id=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = StudentDecree.objects.get(decree_id=decree_id, student_id=student_id)
    item.delete()

    decree = Decree.objects.get(pk=decree_id)

    serializer = DecreeSerializer(decree)
    students = serializer.data["students"]

    return Response(students)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_student_decree(request, decree_id, student_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not StudentDecree.objects.filter(student_id=student_id, decree_id=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = StudentDecree.objects.get(student_id=student_id, decree_id=decree_id)

    serializer = StudentDecreeSerializer(item)

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=ReprimandSerializer)
@api_view(["POST"])
@permission_classes([IsModerator])
def add_reprimand(request, student_id):
    if not Student.objects.filter(pk=student_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    student = Student.objects.get(pk=student_id)

    # Получаем данные из запроса
    reason = request.data.get("reason")
    if not reason:
        return Response({"error": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Создаём выговор
    reprimand = Reprimand.objects.create(
        student=student,
        reason=reason,
        issued_by=identity_user(request),
    )

    serializer = ReprimandSerializer(reprimand)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])

def get_reprimand_by_student_id(request, student_id):
    """
    Получить выговоры студента по его ID. 
    """
    # Проверяем, существует ли студент
    if not Student.objects.filter(pk=student_id).exists():
        return Response({"error": "Студент не найден."}, status=status.HTTP_404_NOT_FOUND)

    # Получаем выговоры студента
    reprimands = Reprimand.objects.filter(student_id=student_id)

    if not reprimands.exists():
        return Response({"error": "Выговоры для данного студента не найдены."}, status=status.HTTP_404_NOT_FOUND)

    # Сериализуем данные
    serializer = ReprimandSerializer(reprimands, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(method='PUT', request_body=StudentDecreeSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_student_in_decree(request, decree_id, student_id):
    user = identity_user(request)

    if not Decree.objects.filter(pk=decree_id, owner=user).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    if not StudentDecree.objects.filter(student_id=student_id, decree_id=decree_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    item = StudentDecree.objects.get(student_id=student_id, decree_id=decree_id)

    serializer = StudentDecreeSerializer(item, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()

    return Response(serializer.data)


@swagger_auto_schema(method='post', request_body=UserLoginSerializer)
@api_view(["POST"])
def login(request):
    serializer = UserLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(**serializer.data)
    if user is None:
        return Response(status=status.HTTP_401_UNAUTHORIZED)

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_200_OK)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@swagger_auto_schema(method='post', request_body=UserRegisterSerializer)
@api_view(["POST"])
def register(request):
    serializer = UserRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    user = serializer.save()

    session_id = str(uuid.uuid4())
    session_storage.set(session_id, user.id)

    serializer = UserSerializer(user)
    response = Response(serializer.data, status=status.HTTP_201_CREATED)
    response.set_cookie("session_id", session_id, samesite="lax")

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    session = get_session(request)
    session_storage.delete(session)

    response = Response(status=status.HTTP_200_OK)
    response.delete_cookie('session_id')

    return response


@swagger_auto_schema(method='PUT', request_body=UserSerializer)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_user(request, user_id):
    if not User.objects.filter(pk=user_id).exists():
        return Response(status=status.HTTP_404_NOT_FOUND)

    user = identity_user(request)

    if user.pk != user_id:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    if not serializer.is_valid():
        return Response(status=status.HTTP_409_CONFLICT)

    serializer.save()

    return Response(serializer.data, status=status.HTTP_200_OK)
