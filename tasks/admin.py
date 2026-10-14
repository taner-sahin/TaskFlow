from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "project",
        "owner",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "project",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
    )

    ordering = ("-created_at",)
