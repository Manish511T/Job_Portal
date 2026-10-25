from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "candidate",
        "status",
        "applied_at",
    )

    list_filter = ("status",)

    search_fields = (
        "job__title",
        "candidate__username",
        "candidate__email",
    )

    list_select_related = ("job", "candidate")
