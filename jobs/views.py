from django.db.models import Count, Q
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsEmployer, IsAdminRole 
from companies.models import Company

from .models import Skill, Job
from .serializers import SkillSerializer, JobSerializer
from .permissions import IsJobOwner, IsJobOwnerOrAdmin



class SkillListView(APIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def get(self, request):
        skills = Skill.objects.all()
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SkillSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class SkillDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdminRole()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        skill = get_object_or_404(Skill, pk=pk)
        serializer = SkillSerializer(skill)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        skill = get_object_or_404(Skill, pk=pk)

        if skill.job_set.exists() or skill.candidates.exists():
            return Response(
                {
                    "detail": (
                        "Cannot delete this skill because it is "
                        "associated with jobs or candidates."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        skill.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class JobListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsEmployer()]
        return [AllowAny()]

    def get(self, request):
        jobs = (
            Job.objects.filter(status=Job.Status.OPEN)
            .select_related("company")
            .prefetch_related("skills")
            .annotate(app_count=Count("applications"))
        )

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            company = request.user.company
        except Company.DoesNotExist:
            return Response(
                {"detail": ("Create a company profile before posting a job.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(company=company)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class MyJobsView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def get(self, request):
        try:
            company = request.user.company
        except Company.DoesNotExist:
            return Response(
                {"detail": "Create a company profile first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        jobs = (
            Job.objects.filter(company=company)
            .select_related("company")
            .prefetch_related("skills")
            .annotate(app_count=Count("applications"))
            .order_by("-created_at")
        )

        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class JobDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ("GET", "HEAD", "OPTIONS"):
            return [AllowAny()]

        if self.request.method in ("PUT", "PATCH"):
            return [
                IsAuthenticated(),
                IsEmployer(),
                IsJobOwner(),
            ]

        if self.request.method == "DELETE":
            return [
                IsAuthenticated(),
                IsJobOwnerOrAdmin(),
            ]

        return [IsAuthenticated()]

    def get_object(self, request, pk):
        queryset = (
            Job.objects.select_related("company")
            .prefetch_related("skills")
            .annotate(app_count=Count("applications", distinct=True))
        )

        # Publicly visible jobs are OPEN.
        visibility_filter = Q(status=Job.Status.OPEN)

        # Employers may also see their own jobs in any status.
        if request.user.is_authenticated:
            visibility_filter |= Q(company__owner=request.user)

        job = get_object_or_404(
            queryset.filter(visibility_filter),
            pk=pk,
        )

        # Enforce object-level permissions for updates and deletion.
        self.check_object_permissions(request, job)
        return job

    def get(self, request, pk):
        job = self.get_object(request, pk)
        serializer = JobSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        job = self.get_object(request, pk)
        serializer = JobSerializer(job, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def patch(self, request, pk):
        job = self.get_object(request, pk)
        serializer = JobSerializer(
            job,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        job = self.get_object(request, pk)

        try:
            job.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Cannot delete this job because applications "
                        "are linked to it. Close the job instead."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
