from rest_framework import serializers

from rest_framework import serializers
from .models import Application, ApiScope, Schema

class SchemaUploadSerializer(serializers.ModelSerializer):
    application = serializers.CharField(max_length=255)
    service = serializers.CharField(max_length=255, required=False, allow_blank=True)

    class Meta:
        model = Schema
        fields = ['application', 'service', 'spec_file']

class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "name", "created_at"]


class ServiceSerializer(serializers.ModelSerializer):
    application = ApplicationSerializer(read_only=True)

    class Meta:
        model = ApiScope
        fields = ["id", "service_name", "application"]


class SchemaSerializer(serializers.ModelSerializer):
    application = serializers.CharField(source="scope.application.name", read_only=True)
    service = serializers.CharField(source="scope.service_name", read_only=True)

    class Meta:
        model = Schema
        fields = [
            "id",
            "application",
            "service",
            "version",
            "sha_256",
            "spec_file",
        ]
