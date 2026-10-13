from django.contrib import admin
from .models import Skill, Job
# Register your models here.

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'company',
        'job_type',
        'status',
        'created_at',
    )

    list_filter = ('status', 'job_type')

    search_fields = (
        'title',
        'location',
        'company__name',
    )

    filter_horizontal = ('skills',)

    list_select_related = ('company',)