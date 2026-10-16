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
        "owner",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "project__name",
        "owner__username",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    list_select_related = ("project", "owner")
