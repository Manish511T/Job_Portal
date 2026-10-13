from django.db import models
from django.db.models import Q, F
# Create your models here.
class Skill(models.Model):
    name = models.CharField(max_length=50 ,unique=True)

    # Used to sort the skill in alphabetical order
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    class JobType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
        INTERNSHIP = 'INTERNSHIP', 'Internship'

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        OPEN = 'OPEN', 'Open'
        CLOSED = 'CLOSED', 'Closed'
    
    company = models.ForeignKey('companies.Company', on_delete=models.PROTECT, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=150)
    job_type = models.CharField(
        max_length= 20,
        choices= JobType.choices
    )
    salary_min = models.PositiveIntegerField(null=True,blank=True)
    salary_max = models.PositiveIntegerField(null=True,blank=True)
    experience_required = models.PositiveSmallIntegerField(default=0)
    skills = models.ManyToManyField('jobs.Skill', blank=True, related_name='jobs')
    deadline = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default= Status.DRAFT
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(salary_min__isnull = True)
                    | Q(salary_max__isnull = True)
                    | Q(salary_min__lte = F("salary_max"))
                ),
                name= 'job_salary_min_lte_max'
            )
        ]
    def __str__(self):
        return f"{self.title} at {self.company}"
    

    
