from rest_framework import serializers
from typing import Any
from .models import Transaction


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class SaveFileSerializer(serializers.Serializer):
    class Meta:
        model = Transaction
        fields = "__all__"


class BalanceSerializer(serializers.Serializer[Any]):
    """
    Serializer for the parameters of the balance endpoint.
    """

    year = serializers.IntegerField(required=False, min_value=1980)
    month = serializers.IntegerField(required=False, min_value=1, max_value=12)
    is_monthly = serializers.BooleanField(required=False)
    account = serializers.IntegerField(min_value=0, required=False)

    def validate(self, data):
        """
        Check that start is before finish.
        """
        args = data.keys()
        if len(args) > 3:
            raise serializers.ValidationError("Too many arguments")
        elif "month" in args and "is_monthly" in args and data["is_monthly"]:
            raise serializers.ValidationError(
                "Arguments month and is_monthly=True are not allowed together."
            )

        return data
