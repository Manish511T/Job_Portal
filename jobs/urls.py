from django.urls import path

from .views import (
    SkillListView,
    SkillDetailView,
    JobListCreateView,
    JobDetailView,
    MyJobsView,
)

urlpatterns = [
    path("skills/", SkillListView.as_view(), name="skill-list"),
    path("skills/<int:pk>/", SkillDetailView.as_view(), name="skill-detail"),

    path("jobs/", JobListCreateView.as_view(), name="job-list-create"),
    path("jobs/my/", MyJobsView.as_view(), name="my-jobs"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
]