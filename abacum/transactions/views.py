from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .pandas import pd_balance_calculator, dataframe_to_json
from .readers import CsvReader
from .serializers import BalanceSerializer, FileUploadSerializer, SaveFileSerializer
from .utils import get_utc_current_year


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


class BalanceView(APIView):
    """
    API endpoint to fetch account balances.
    """
    serializer_class = BalanceSerializer

    def get(self, request, format=None):
        serializer = BalanceSerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)

        self.year = serializer.data.get("year", get_utc_current_year())
        self.month = serializer.data.get("month", None)
        self.account = serializer.data.get('account', None)
        self.is_monthly = serializer.data.get('is_monthly', False)

        data = list(self.get_queryset().values("account", "date", "amount"))
        df = pd_balance_calculator(data, self.is_monthly)
        content = dataframe_to_json(df)

        return Response(content)


    def get_queryset(self):
        if self.account and self.month:
            return Transaction.objects.filter(
                date__year=self.year,
                date__month=self.month,
                account=self.account,
            )
        if self.account:
            return Transaction.objects.filter(
                date__year=self.year,
                account=self.account
            )
        if self.month:
            return Transaction.objects.filter(
                date__year=self.year,
                date__month=self.month,
            )

        return Transaction.objects.filter(date__year=self.year)
