from rest_framework import serializers
#from users.models import User
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class RegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=30)
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    email = serializers.EmailField(required=True, max_length=30)
    password = serializers.CharField(min_length=8, max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, args):
        username = args.get("username", None)

        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": ("Username already taken")})

        return super().validate(args)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
        # validated_data['password'] = make_password(validated_data.get('password'))
        # return super(RegistrationSerializer, self).create(validated_data)
    