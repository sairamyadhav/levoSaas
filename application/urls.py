from django.urls import path
from .views import SchemaUploadView, LatestSchemaView, SchemaVersionDetailView, SchemaVersionListView

urlpatterns = [
    path('upload', SchemaUploadView.as_view(), name='schema-upload'),
    path("<str:application>/<str:service>/latest/", LatestSchemaView.as_view(), name="latest-schema-service"),
    path("<str:application>/latest/", LatestSchemaView.as_view(), name="latest-schema"),
    path("<str:application>/versions/", SchemaVersionListView.as_view(), name="schema-versions"),
    path("<str:application>/<str:service>/versions/", SchemaVersionListView.as_view(), name="schema-versions-service"),
    path("<str:application>/versions/<int:version>/", SchemaVersionDetailView.as_view(), name="schema-version-detail"),
    path("<str:application>/<str:service>/versions/<int:version>/", SchemaVersionDetailView.as_view(), name="schema-version-detail-service"),
]