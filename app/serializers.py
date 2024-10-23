from rest_framework import serializers
from .models import *


class StudentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, student):
        if student.image:
            return student.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    class Meta:
        model = Student
        fields = "__all__"


class StudentItemSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField('get_value')

    def get_image(self, student):
        if student.image:
            return student.image.url.replace("minio", "localhost", 1)

        return "http://localhost:9000/images/default.png"

    def get_value(self, student):
        return self.context.get("value")

    class Meta:
        model = Student
        fields = ("id", "name", "image", "value")


class DecreesSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, decree):
        return decree.owner.username

    def get_moderator(self, decree):
        if decree.moderator:
            return decree.moderator.username

        return ""

    class Meta:
        model = Decree
        fields = "__all__"


class DecreeSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    moderator = serializers.SerializerMethodField()

    def get_owner(self, decree):
        return decree.owner.username if decree.owner else None

    def get_moderator(self, decree):
        return decree.moderator.username if decree.moderator else None
    
    def get_students(self, decree):
        items = StudentDecree.objects.filter(decree=decree)
        return [StudentItemSerializer(item.student, context={"value": item.value}).data for item in items]
    
    class Meta:
        model = Decree
        fields = "__all__"


class StudentDecreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDecree
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username')


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'username')
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