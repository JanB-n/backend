from rest_framework import serializers
from users.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, max_length=30)
    last_name = serializers.CharField(required=True, max_length=30)
    email = serializers.EmailField(required=True, max_length=30)
    password = serializers.CharField(min_length=8, max_length=30, write_only=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password')
        #extra_kwargs = {'password': {'write_only': True}}

    def validate(self, args):
        #first_name = args.get('first_name', None)
        #last_name = args.get('last_name', None)
        email = args.get('email', None)
        #password = args.get('password', None)

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': ('Email already exists')})

        return super().validate(args)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    