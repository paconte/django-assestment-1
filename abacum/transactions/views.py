from rest_framework import generics, status
from rest_framework.response import Response

from .readers import CsvReader
from .serializers import FileUploadSerializer, SaveFileSerializer


class UploadFileView(generics.CreateAPIView):
    serializer_class = FileUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]

        csvReader: CsvReader = CsvReader()
        csvReader.read(file)
        csvReader.save()

        content = {
            "status": "success",
            "rows_read": csvReader.rows_success,
            "rows_not_read": csvReader.rows_failure,
        }

        return Response(content, status=status.HTTP_201_CREATED)
