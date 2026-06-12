from rest_framework import serializers
from .models import Artifact


class ArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artifact
        fields = "__all__"
        read_only_fields = ["id", "created_at"]
