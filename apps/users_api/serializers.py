from rest_framework import serializers
from users_api.models import CustomUser


class CustomTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        write_only=True,
    )
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        read_only=True,
    )


class CustomUserSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        max_length=128,
        required=False,
    )
    password = serializers.CharField(
        max_length=128,
        required=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'new_password',
            'avatar',
            'thumbnail',
        ]

        extra_kwargs = {
            'email': {'read_only': True},
            'password': {'write_only': True},
            'new_password': {'write_only': True},
            'thumbnail': {'read_only': True},
        }

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        password = attrs.get('password')
        if new_password is None or password is None:
            raise serializers.ValidationError('Для смены пароля нужно ввести старый и новый пароль')
        if new_password and password:
            if password != self.instance.password:
                print(password)
                print(self.instance.password)
                raise serializers.ValidationError("Старый пароль неверный")
            attrs['password'] = attrs.pop('new_password')
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        max_length=128,
    )

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'password',
            'confirm_password',
        ]

        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
