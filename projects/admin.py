from django.contrib import admin

from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "owner",
        "created_at",
    )

    search_fields = (
        "name",
        "description",
        "owner__username",
    )

    list_filter = (
        "created_at",
        "owner",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at",)

    list_select_related = ("owner",)
