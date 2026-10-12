from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Project

User = get_user_model()


class ProjectAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", password="TestPass123!")

        self.other_user = User.objects.create_user(
            username="mehmet", password="TestPass123!"
        )

        self.project = Project.objects.create(
            name="Ahmet Project", description="Test project", owner=self.user
        )

        self.other_project = Project.objects.create(
            name="Mehmet Project",
            description="Other user's project",
            owner=self.other_user,
        )

        self.list_url = reverse("projects:project-list")
        self.detail_url = reverse("projects:project-detail", args=[self.project.id])

    def test_unauthenticated_user_cannot_list_projects(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_can_only_list_own_projects(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Ahmet Project")

    def test_user_can_create_project(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            self.list_url,
            {"name": "New Project", "description": "Created through API"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["owner"], self.user.id)

    def test_user_cannot_access_other_users_project(self):
        self.client.force_authenticate(user=self.user)

        url = reverse("projects:project-detail", args=[self.other_project.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_update_own_project(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            self.detail_url, {"name": "Updated Project"}, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.project.refresh_from_db()
        self.assertEqual(self.project.name, "Updated Project")

    def test_user_can_delete_own_project(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())
