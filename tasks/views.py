from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(
            owner=self.request.user,
            project__owner=self.request.user,
        )

    def perform_create(self, serializer):
        project = serializer.validated_data["project"]

        if project.owner_id != self.request.user.id:
            raise ValidationError(
                {"project": "You can only add tasks to your own projects."}
            )

        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        project = serializer.validated_data.get(
            "project",
            serializer.instance.project,
        )

        if project.owner_id != self.request.user.id:
            raise ValidationError(
                {"project": "You can only move tasks to your own projects."}
            )

        serializer.save()
