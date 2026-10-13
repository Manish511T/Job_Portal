from django.db import models
from django.conf import settings
# Create your models here.
class Application(models.Model):
    class STATUS(models.TextChoices):
        APPLIED = 'APPLIED', 'Applied'
        SHORTLISTED = 'SHORTLISTED', 'Shortlisted'
        REJECTED = 'REJECTED', 'Rejected'
        SELECTED = 'SELECTED', 'Selected'
   
    job = models.ForeignKey('jobs.Job',on_delete=models.PROTECT, related_name='applications')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS.choices,
        default=STATUS.APPLIED
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-applied_at']
        constraints = [
            models.UniqueConstraint(
                fields= ['job', 'candidate'],
                name = 'unique_job_candidate_application'
            )
        ]

    def __str__(self):
        return f"{self.candidate.username} → {self.job.title}"