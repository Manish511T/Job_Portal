from rest_framework import serializers
from .models import Skill, Job
from companies.models import Company
from companies.serializers import CompanyMiniSerializer
from django.utils import timezone
class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

    def validate_name(self, value):
        value = value.strip().title()
        if not value:
            raise serializers.ValidationError(
                "Skill name cannot be empty."
            )
        existing_skills = Skill.objects.filter(name__iexact=value)

        if self.instance:
            existing_skills = existing_skills.exclude(
                pk = self.instance.pk
            )
        if existing_skills.exists():
            raise serializers.ValidationError(
                "This skill already exists."
            )
        return value


class JobSerializer(serializers.ModelSerializer):
    # Output: nested company details
    company = CompanyMiniSerializer(read_only=True)
    # Input: company ID
    company_id = serializers.PrimaryKeyRelatedField(
        queryset = Company.objects.all(),
        source = 'company',
        write_only=True,
    )

    # Output: nested skill objects
    skills = SkillSerializer(many=True, read_only=True)
    # Input: list of skills IDs
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset = Skill.objects.all(),
        source = 'skills',
        many = True,
        write_only = True
    )

    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'company','company_id','applications_count', 'title', 'description', 'location', 'job_type', 'salary_min', 'salary_max', 'experience_required', 'skills','skill_ids', 'deadline', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_applications_count(self, obj):
        return obj.applications.count()
    

    def validate_deadline(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Deadline cannot be in the past.")
        return value

    def validate(self, attrs):
        salary_min = attrs.get(
            'salary_min', self.instance.salary_min if self.instance else None
        )
        salary_max = attrs.get(
            'salary_max', self.instance.salary_max if self.instance else None
        )

        if salary_min is not None and salary_max is not None:
            if salary_min>salary_max:
                raise serializers.ValidationError("Minimum salary cannot exceed maximum salary.")

        return attrs

    def validate_title(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(
                "Job title cannot be empty"
            )
        return value
                