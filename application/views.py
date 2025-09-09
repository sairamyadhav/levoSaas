from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .serializers import SchemaUploadSerializer
from .models import Application, ApiScope, Schema
from .services import parse_and_validate_spec, compute_sha256
from django.shortcuts import get_object_or_404
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Application, ApiScope, Schema
from .serializers import SchemaSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.parsers import MultiPartParser

class SchemaUploadView(APIView):

    parser_classes = [MultiPartParser]

    @swagger_auto_schema(request_body=SchemaUploadSerializer)
    def post(self, request):
        serializer = SchemaUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        app_name = serializer.validated_data["application"]
        service_name = serializer.validated_data.get("service") or None
        spec_file = serializer.validated_data["spec_file"]

        # Parse + validate
        try:
            spec_file.seek(0)
            spec_data, fmt = parse_and_validate_spec(spec_file)
            sha = compute_sha256(spec_data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        size_bytes = spec_file.size

        app, _ = Application.objects.get_or_create(name=app_name)
        scope, _ = ApiScope.objects.get_or_create(application=app, service_name=service_name)

        with transaction.atomic():
            latest = scope.schemas.filter(is_latest=True).first()

            if latest and latest.sha_256 == sha:
                return Response(
                    {
                        "application": app.name,
                        "service": service_name,
                        "version": latest.version,
                        "sha_256": latest.sha_256,
                        "note": "Identical to latest schema, no new version created",
                    },
                    status=status.HTTP_200_OK,
                )

            # New version
            new_version = (latest.version + 1) if latest else 1
            if latest:
                latest.is_latest = False
                latest.save(update_fields=["is_latest"])

            new_schema = Schema.objects.create(
                scope=scope,
                version=new_version,
                spec_file=spec_file,  # stored via FileField
                spec_format=fmt,
                sha_256=sha,
                size_bytes=size_bytes,
                is_latest=True,
            )

        return Response(
            {
                "application": app.name,
                "service": service_name,
                "version": new_schema.version,
                "sha_256": new_schema.sha_256,
                "is_latest": new_schema.is_latest,
            },
            status=status.HTTP_201_CREATED,
        )

class LatestSchemaView(APIView):
    """
    GET /api/schemas/{application}/[service]/latest/
    """

    def get(self, request, application, service=None):
        app = get_object_or_404(Application, name=application)
        if not app:
            return Response({"error": "No Application found"}, status=status.HTTP_404_NOT_FOUND)
        scope = ApiScope.objects.filter(application=app)
        if service:
            scope = get_object_or_404(scope, service_name=service)
            if not scope:
                return Response({"error": f"No service found in application:{application}"}, status=status.HTTP_404_NOT_FOUND)
        else:
            scope = get_object_or_404(scope, service_name=None)

        schema = Schema.objects.filter(scope=scope, is_latest=True).first()
        if not schema:
            return Response({"message": f"No schema found in {application}:{service}"}, status=status.HTTP_404_NOT_FOUND)

        serializer = SchemaSerializer(schema)
        return Response(serializer.data)


class SchemaVersionDetailView(APIView):
    """
    GET /api/schemas/{application}/[service]/versions/{version}/
    """

    def get(self, request, application, version, service=None):
        app = get_object_or_404(Application, name=application)
        scope = None
        if service:
            scope = get_object_or_404(ApiScope, service_name=service, application=app)

        schema = get_object_or_404(Schema, scope=scope, version=version)
        serializer = SchemaSerializer(schema)
        return Response(serializer.data)


class SchemaVersionListView(generics.ListAPIView):
    """
    GET /api/schemas/{application}/[service]/versions/
    """

    serializer_class = SchemaSerializer

    def get_queryset(self):
        application = get_object_or_404(Application, name=self.kwargs["application"])
        scope = None
        if "service" in self.kwargs and self.kwargs["service"]:
            scope = get_object_or_404(ApiScope, service_name=self.kwargs["service"], application=application)
        return Schema.objects.filter(scope=scope).order_by("version")