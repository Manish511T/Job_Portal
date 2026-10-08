from django.db import models
from django.conf import settings
# Create your models here.
class CandidateProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile')
    phone = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    education = models.TextField(blank=True)
    experience_years = models.PositiveSmallIntegerField(default=0)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.ManyToManyField('jobs.Skill', blank=True, related_name='candidates')

    def __str__(self):
        return self.user.username