from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsEmployer
from .models import Company
from .permissions import IsCompanyOwner, IsCompanyOwnerOrAdmin
from .serializers import CompanySerializer


class CompanyListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        if self.request.method in ("PUT", "PATCH"):
            return [IsAuthenticated(), IsCompanyOwner()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsCompanyOwnerOrAdmin()]

        return [IsAuthenticated()]

    def get(self, request):
        companies = Company.objects.all()
        serializer = CompanySerializer(
            companies,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Prevent a OneToOne constraint violation and a resulting 500.
        if Company.objects.filter(owner=request.user).exists():
            return Response(
                {"detail": "You already have a company registered."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CompanySerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = serializer.save(owner=request.user)

        return Response(
            CompanySerializer(company, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class CompanyDetailView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]

        if self.request.method in ("PUT", "PATCH"):
            return [IsAuthenticated(), IsCompanyOwner()]

        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsCompanyOwnerOrAdmin()]

        return []

    def get_object(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk):
        company = self.get_object(pk)
        serializer = CompanySerializer(
            company,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        company = self.get_object(pk)
        self.check_object_permissions(request, company)

        serializer = CompanySerializer(
            company,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Owner is not a writable serializer field.
        company = serializer.save()

        return Response(
            CompanySerializer(company, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        company = self.get_object(pk)
        self.check_object_permissions(request, company)

        serializer = CompanySerializer(
            company,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        company = serializer.save()

        return Response(
            CompanySerializer(company, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request, pk):
        company = self.get_object(pk)
        self.check_object_permissions(request, company)

        try:
            company.delete()
        except ProtectedError:
            return Response(
                {
                    "detail": (
                        "Cannot delete this company because protected "
                        "records depend on it. Remove those dependencies "
                        "or close the company instead."
                    )
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)
