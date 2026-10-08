from django.db import models

# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=50 ,unique=True)

    # Used to sort the skill in alphabetical order
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name