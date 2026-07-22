from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from products.models import Product
from products.permission import IsAdmin
from products.serializers import ProductSerializer
from orders.models import Order
from orders.serializers import OrderSerializer


LOW_STOCK_THRESHOLD = 5


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        products = Product.objects.filter(is_deleted=False)
        low_stock_qs = products.filter(stock__lte=LOW_STOCK_THRESHOLD).order_by("stock")

        orders = Order.objects.filter(is_deleted=False).exclude(status="Cancelled")
        revenue = orders.aggregate(total=Sum("total_price"))["total"] or 0

        data = {
            "total_products": products.count(),
            "low_stock_count": low_stock_qs.count(),
            "low_stock_products": ProductSerializer(low_stock_qs[:10], many=True).data,
            "total_orders": Order.objects.filter(is_deleted=False).count(),
            "revenue": revenue,
        }
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )


class CustomerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_staff:
            return Response(
                {"error": "Use the admin dashboard endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )

        orders = Order.objects.filter(
            customer=request.user,
            is_deleted=False,
        ).prefetch_related("items")

        recent = orders.order_by("-created_at")[:5]

        data = {
            "total_orders": orders.count(),
            "recent_orders": OrderSerializer(recent, many=True).data,
        }
        return Response(
            {"success": True, "data": data},
            status=status.HTTP_200_OK,
        )
