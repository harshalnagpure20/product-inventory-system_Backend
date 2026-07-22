from django.urls import path
from .views import (
    OrderListCreateAPIView,
    OrderHistoryAPIView,
    OrderDetailAPIView,
    OrderStatusUpdateAPIView,
    OrderCancelAPIView,
    OrderExportCSVAPIView,
)

urlpatterns = [
    path("", OrderListCreateAPIView.as_view(), name="order-list-create"),
    path("history/", OrderHistoryAPIView.as_view(), name="order-history"),
    path("export/", OrderExportCSVAPIView.as_view(), name="order-export-csv"),
    path("<int:pk>/", OrderDetailAPIView.as_view(), name="order-detail"),
    path("<int:pk>/status/", OrderStatusUpdateAPIView.as_view(), name="order-status"),
    path("<int:pk>/cancel/", OrderCancelAPIView.as_view(), name="order-cancel"),
]
