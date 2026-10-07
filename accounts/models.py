from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    class Role(models.TextChoices):
        CANDIDATE = 'CANDIDATE', 'Candidate'
        EMPLOYER = 'EMPLOYER', 'Employer'
        ADMIN = 'ADMIN', 'Admin'

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.CANDIDATE
        )


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
