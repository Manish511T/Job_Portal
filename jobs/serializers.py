from rest_framework import serializers
from django.utils import timezone

from .models import Skill, Job
from companies.serializers import CompanySerializer


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]

    def validate_name(self, value):
        value = " ".join(value.split())

        if not value:
            raise serializers.ValidationError("Skill name cannot be empty.")

        existing_skills = Skill.objects.filter(name__iexact=value)

        if self.instance:
            existing_skills = existing_skills.exclude(pk=self.instance.pk)

        if existing_skills.exists():
            raise serializers.ValidationError("This skill already exists.")

        return value


class JobSerializer(serializers.ModelSerializer):
    # Company is output-only; the view assigns it from request.user.
    company = CompanySerializer(read_only=True)

    # Nested skill objects for responses.
    skills = SkillSerializer(many=True, read_only=True)

    # Skill IDs accepted when creating or updating a job.
    skill_ids = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.all(),
        source="skills",
        many=True,
        write_only=True,
        required=False,
    )

    applications_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            "id",
            "company",
            "title",
            "description",
            "location",
            "job_type",
            "salary_min",
            "salary_max",
            "experience_required",
            "skills",
            "skill_ids",
            "deadline",
            "status",
            "created_at",
            "applications_count",
        ]
        read_only_fields = [
            "id",
            "company",
            "created_at",
            "applications_count",
        ]

    def get_applications_count(self, obj):
        count = getattr(obj, "app_count", None)

        if count is not None:
            return count

        return obj.applications.count()

    def validate_title(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError("Job title cannot be empty.")

        return value

    def validate_deadline(self, value):
        if value is None:
            return value

        # Allow an unchanged existing deadline during an update.
        if self.instance and value == self.instance.deadline:
            return value

        if value < timezone.localdate():
            raise serializers.ValidationError("Deadline cannot be in the past.")

        return value

    def validate(self, attrs):
        # Validate minimum and maximum salary.
        salary_min = attrs.get(
            "salary_min",
            self.instance.salary_min if self.instance else None,
        )
        salary_max = attrs.get(
            "salary_max",
            self.instance.salary_max if self.instance else None,
        )

        if (
            salary_min is not None
            and salary_max is not None
            and salary_min > salary_max
        ):
            raise serializers.ValidationError(
                "Minimum salary cannot exceed maximum salary."
            )

        # Prevent reopening a closed job with an expired deadline.
        if self.instance:
            new_status = attrs.get(
                "status",
                self.instance.status,
            )
            effective_deadline = attrs.get(
                "deadline",
                self.instance.deadline,
            )

            reopening = (
                self.instance.status == Job.Status.CLOSED
                and new_status == Job.Status.OPEN
            )

            if (
                reopening
                and effective_deadline is not None
                and effective_deadline < timezone.localdate()
            ):
                raise serializers.ValidationError(
                    {
                        "deadline": (
                            "A job with an expired deadline " "cannot be reopened."
                        )
                    }
                )

        return attrs
