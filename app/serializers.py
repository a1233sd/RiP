from rest_framework import serializers

from .models import *


class StudentsSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, student):
        if student.image:
            return student.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Student
        fields = ("id", "name", "status", "group", "image")


class StudentSerializer(StudentsSerializer):
    class Meta(StudentsSerializer.Meta):
        model = Student
        fields = StudentsSerializer.Meta.fields + ("course", )


class DecreesSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    moderator = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Decree
        fields = "__all__"


class DecreeSerializer(DecreesSerializer):
    students = serializers.SerializerMethodField()

    def get_students(self, decree):
        items = StudentDecree.objects.filter(decree=decree)
        return [StudentItemSerializer(item.student, context={"value": item.value}).data for item in items]


class StudentItemSerializer(StudentSerializer):
    value = serializers.SerializerMethodField()

    def get_value(self, student):
        return self.context.get("value")

    class Meta(StudentSerializer.Meta):
        fields = "__all__"


class StudentDecreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDecree
        fields = "__all__"



class ReprimandSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    issued_by_name = serializers.CharField(source='issued_by.username', read_only=True)

    class Meta:
        model = Reprimand
        fields = ('id', 'student', 'student_name', 'reason', 'date_issued', 'status', 'issued_by', 'issued_by_name')



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'username')
        write_only_fields = ('password',)
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user




class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
