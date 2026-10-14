from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from projects.models import Project

from .models import Task

User = get_user_model()


class TaskAPITests(APITestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="ahmet", password="TestPassword123!"
        )

        self.user2 = User.objects.create_user(
            username="mehmet", password="TestPassword123!"
        )

        self.project1 = Project.objects.create(
            name="Ahmet Project",
            description="Ahmet'in projesi",
            owner=self.user1,
        )

        self.project2 = Project.objects.create(
            name="Mehmet Project",
            description="Mehmet'in projesi",
            owner=self.user2,
        )

        self.task1 = Task.objects.create(
            project=self.project1,
            owner=self.user1,
            title="Ahmet Task",
            description="Ahmet'in gorevi",
            status="todo",
        )

        self.task2 = Task.objects.create(
            project=self.project2,
            owner=self.user2,
            title="Mehmet Task",
            description="Mehmet'in gorevi",
            status="todo",
        )

        self.url = reverse("task-list")

    def test_unauthenticated_user_cannot_list_tasks(self):
        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_user_can_list_only_own_tasks(self):
        self.client.force_authenticate(user=self.user1)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Ahmet Task")

    def test_user_can_create_task_in_own_project(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "project": self.project1.id,
            "title": "New Task",
            "description": "Yeni gorev",
            "status": "todo",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        new_task = Task.objects.get(id=response.data["id"])

        self.assertEqual(new_task.owner, self.user1)
        self.assertEqual(new_task.project, self.project1)

    def test_user_cannot_create_task_in_other_project(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            "project": self.project2.id,
            "title": "Unauthorized Task",
            "status": "todo",
        }

        response = self.client.post(self.url, data, format="json")

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(Task.objects.filter(title="Unauthorized Task").exists())

    def test_user_can_update_own_task(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("task-detail", args=[self.task1.id])

        response = self.client.patch(
            url,
            {"status": "in_progress"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.status, "in_progress")

    def test_user_cannot_access_other_users_task(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("task-detail", args=[self.task2.id])

        response = self.client.get(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_move_task_to_other_project(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("task-detail", args=[self.task1.id])

        response = self.client.patch(
            url,
            {"project": self.project2.id},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.task1.refresh_from_db()
        self.assertEqual(self.task1.project, self.project1)

    def test_user_can_delete_own_task(self):
        self.client.force_authenticate(user=self.user1)

        url = reverse("task-detail", args=[self.task1.id])

        response = self.client.delete(url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(Task.objects.filter(id=self.task1.id).exists())
