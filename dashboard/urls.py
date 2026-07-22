from django.urls import path
from .views import AdminDashboardAPIView, CustomerDashboardAPIView

urlpatterns = [
    path("admin/", AdminDashboardAPIView.as_view(), name="dashboard-admin"),
    path("customer/", CustomerDashboardAPIView.as_view(), name="dashboard-customer"),
]
