from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

# Create your models here.


class CustomUserManager(UserManager):
    def create_superuser(
        self,
        username,
        email=None,
        password=None,
        **extra_fields,
    ):
        extra_fields["role"] = self.model.Role.ADMIN

        return super().create_superuser(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )


class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = "CANDIDATE", "Candidate"
        EMPLOYER = "EMPLOYER", "Employer"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.CANDIDATE)
    objects = CustomUserManager()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
