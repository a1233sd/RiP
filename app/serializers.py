# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Students
        fields = "__all__"
        read_only_fields = ['id', 'status']

    def validate(self, attrs):
        # Запрет на изменение системных полей
        if 'status' in attrs:
            raise serializers.ValidationError("Нельзя изменять поле status напрямую.")
        return attrs


class DecreeStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=Students.objects.filter(status=1),
        source='student',
        write_only=True
    )

    class Meta:
        model = DecreeStudents
        fields = ['id', 'decree', 'student', 'student_id', 'count']
        read_only_fields = ['id', 'decree', 'student']
        extra_kwargs = {
            'decree': {'read_only': True},
            'student': {'read_only': True},
        }


class DecreeSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()
    students = DecreeStudentSerializer(source='decreestudents_set', many=True, read_only=True)

    class Meta:
        model = Decree
        fields = '__all__'
        read_only_fields = ['id', 'owner', 'moderator', 'date_created', 'status', 'date_formation', 'date_complete']

    def get_owner(self, decree):
        # Проверяем наличие владельца, иначе возвращаем None
        return decree.owner.username if decree.owner else None

    def get_moderator(self, decree):
        # Проверяем наличие модератора, иначе возвращаем None
        return decree.moderator.username if decree.moderator else None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'date_joined', 'username')
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'username')
        extra_kwargs = {
            'password': {'write_only': True},
            'id': {'read_only': True},
        }

    def create(self, validated_data):
        # Используем create_user для создания пользователя
        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            username=validated_data['username'],
            password=validated_data['password']  # create_user сам вызывает set_password
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
