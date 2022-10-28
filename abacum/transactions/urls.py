from django.urls import path
from .views import BalanceView, UploadFileView

urlpatterns = [
    path('upload/', UploadFileView.as_view(), name='upload-csv'),
    path('balance/', BalanceView.as_view(), name='balance'),
]