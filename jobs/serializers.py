from rest_framework import serializers
from .models import Skill, Job
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
    class Meta:
        model = Job
        fields = ['id', 'company', 'title', 'description', 'location', 'job_type', 'salary_min', 'salary_max', 'experience_required', 'skills', 'deadline', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']

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
    
                