from django.urls import path
from .views import SkillListView, SkillDetailView, JobListCreateView, JobDetailView

urlpatterns = [
    path("skills/", SkillListView.as_view(), name="skill-list"),
    path("skills/<int:pk>/", SkillDetailView.as_view(), name="skill-detail"),
    path("jobs/", JobListCreateView.as_view(), name="job-list"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
]
