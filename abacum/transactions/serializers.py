from rest_framework import serializers

from .models import Transaction


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class SaveFileSerializer(serializers.Serializer):
    class Meta:
        model = Transaction
        fields = "__all__"
