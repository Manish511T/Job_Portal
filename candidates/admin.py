from django.contrib import admin
from .models import CandidateProfile
# Register your models here.

@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'phone',
        'location',
        'experience_years',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'phone',
        'location',
    ]

    filter_horizontal = ['skills']