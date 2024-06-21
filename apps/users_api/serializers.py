from rest_framework import serializers
from users_api.models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(
        max_length=128,
        required=False,
        write_only=True,
    )
    password = serializers.CharField(
        max_length=128,
        required=False,
        write_only=True,
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
            'thumbnail': {'read_only': True},
        }

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        password = attrs.get('password')
        if bool(new_password) != bool(password):
            raise serializers.ValidationError(
                'Для смены пароля нужно ввести старый и новый пароль'
            )
        if new_password and password:
            if not self.instance.check_password(password):
                raise serializers.ValidationError(
                    "Старый пароль неверный"
                )
            attrs['password'] = attrs.pop('new_password')
        return attrs


class PasswordRestoreSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
        ]


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

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                "Пароли не совпадают"
            )
        return attrs
