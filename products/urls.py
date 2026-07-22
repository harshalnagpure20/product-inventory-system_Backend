from django.urls import path
from .views import (
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductExportCSVAPIView,
)

urlpatterns = [
    path("", ProductListCreateAPIView.as_view(), name="product-list-create"),
    path("export/", ProductExportCSVAPIView.as_view(), name="product-export-csv"),
    path("<int:pk>/", ProductDetailAPIView.as_view(), name="product-detail"),
]
