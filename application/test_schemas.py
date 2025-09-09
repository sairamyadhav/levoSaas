import io
import json
import yaml
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Application, Schema


class SchemaAPITests(APITestCase):

    def setUp(self):
        self.app_name = "app1"
        self.service_name = "service1"

        self.schema_json = io.BytesIO(json.dumps({
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {}
        }).encode("utf-8"))
        self.schema_json.name = "openapi.json"

        self.schema_yaml = io.BytesIO(yaml.dump({
            "openapi": "3.0.0",
            "info": {"title": "Test API YAML", "version": "1.0.0"},
            "paths": {}
        }).encode("utf-8"))
        self.schema_yaml.name = "openapi.yaml"

    def test_upload_schema_success(self):
        url = reverse("schema-upload")
        data = {"application": self.app_name}
        response = self.client.post(url, data=data, files={"schema_file": self.schema_json})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Schema.objects.count(), 1)
        self.assertEqual(Schema.objects.first().version, 1)

    def test_upload_invalid_schema_failure(self):
        url = reverse("schema-upload")
        bad_file = io.BytesIO(b"not a schema")
        bad_file.name = "invalid.json"

        data = {"application": self.app_name}
        response = self.client.post(url, data=data, files={"schema_file": bad_file})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    def test_get_latest_schema_application_level(self):
        self.client.post(reverse("schema-upload"), data={"application": self.app_name}, files={"schema_file": self.schema_json})

        url = reverse("latest-schema", kwargs={"application": self.app_name})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["application"], self.app_name)

    def test_get_latest_schema_service_level(self):
        self.client.post(reverse("schema-upload"),
                         data={"application": self.app_name, "service": self.service_name},
                         files={"schema_file": self.schema_yaml})

        url = reverse("latest-schema-service", kwargs={"application": self.app_name, "service": self.service_name})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["service"], self.service_name)

    def test_list_versions(self):
        self.client.post(reverse("schema-upload"), data={"application": self.app_name}, files={"schema_file": self.schema_json})
        self.client.post(reverse("schema-upload"), data={"application": self.app_name}, files={"schema_file": self.schema_yaml})

        url = reverse("schema-versions", kwargs={"application": self.app_name})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 2)

    def test_get_specific_version(self):
        self.client.post(reverse("schema-upload"), data={"application": self.app_name}, files={"schema_file": self.schema_json})

        url = reverse("schema-version-detail", kwargs={"application": self.app_name, "version": 1})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["version"], 1)
