from django.urls import path
from .views import SkillListView, SkillDetailView

urlpatterns = [
    path('skills/', SkillListView.as_view(), name='skill-list'),
    path('skills/<int:id>/', SkillDetailView.as_view(), name='skill-detail')
]