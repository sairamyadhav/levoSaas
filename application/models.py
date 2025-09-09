from django.db import models
from django.utils import timezone


class Application(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ApiScope(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="scopes")
    service_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        unique_together = ("application", "service_name")

    def __str__(self):
        if self.service_name:
            return f"{self.application.name}:{self.service_name}"
        return f"{self.application.name}:_app"


class Schema(models.Model):

    SPEC_FORMAT_CHOICES = (
        ('json', 'JOSN'),
        ('yaml', 'YAML')
    )

    scope = models.ForeignKey(ApiScope, on_delete=models.CASCADE, related_name="schemas")
    version = models.IntegerField()
    spec_file = models.FileField(upload_to="schemas/")
    spec_format = models.CharField(max_length=4, choices=SPEC_FORMAT_CHOICES)
    sha_256 = models.CharField(max_length=64)
    size_bytes = models.IntegerField()
    is_latest = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("scope", "version")
        ordering = ["-version"]

    def __str__(self):
        return f"{self.scope} v{self.version}"