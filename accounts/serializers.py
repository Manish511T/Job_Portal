from django.contrib.auth import password_validation
from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError as DjangoValidationError


def validate_unique_email(value, instance=None):
    value = value.strip().lower()

    users = User.objects.filter(email__iexact=value)

    if instance is not None:
        users = users.exclude(pk=instance.pk)

    if users.exists():
        raise serializers.ValidationError("A user with this email already exists.")

    return value


class EmailValidationMixin:
    def validate_email(self, value):
        return validate_unique_email(
            value,
            instance=getattr(self, "instance", None),
        )


class RegisterSerializer(EmailValidationMixin, serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    role = serializers.ChoiceField(
        choices=[
            (User.Role.CANDIDATE, "Candidate"),
            (User.Role.EMPLOYER, "Employer"),
        ],
        default=User.Role.CANDIDATE,
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "password2", "role"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        candidate = User(username=attrs.get("username"), email=attrs.get("email"))
        try:
            password_validation.validate_password(attrs["password"], user=candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        return User.objects.create_user(
            password=password,
            **validated_data,
        )


class UserSerializer(EmailValidationMixin, serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "role",
            "created_at",
        ]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user

        if not user.check_password(value):
            raise serializers.ValidationError("Your current password is incorrect.")

        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        password_validation.validate_password(value, user=user)
        return value


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
