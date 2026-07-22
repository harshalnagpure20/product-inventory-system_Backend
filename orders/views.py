from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from products.models import Product
from products.permission import IsAdmin, IsCustomer
from .models import Order, OrderItem
from .serializers import (
    OrderSerializer,
    PlaceOrderSerializer,
    OrderStatusSerializer,
)


class OrderListCreateAPIView(APIView):
     permission_classes = [IsAuthenticated]

     def get(self, request):
        # Admin sees all; customer sees own
        if request.user.is_staff:
            qs = Order.objects.filter(is_deleted=False).prefetch_related("items")
        else:
            qs = Order.objects.filter(
                customer=request.user, is_deleted=False
            ).prefetch_related("items")
        return Response(OrderSerializer(qs, many=True).data)
    
     def post(self, request):
        # Customers only
        if request.user.is_staff:
            return Response(
                {"error": "Admins cannot place orders"},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = PlaceOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        items_data = serializer.validated_data["items"]

        try:
            with transaction.atomic():
                order = Order.objects.create(customer=request.user, total_price=0)
                total = Decimal("0.00")
                for item in items_data:
                    product = (
                        Product.objects.select_for_update()
                        .filter(pk=item["product_id"], is_deleted=False, is_active=True)
                        .first()
                    )
                    if not product:
                        raise ValueError(f"Product {item['product_id']} not found")
                    qty = item["quantity"]
                    if product.stock <= 0:
                        raise ValueError(f"{product.name} is out of stock")
                    if qty > product.stock:
                        raise ValueError(
                            f"Not enough stock for {product.name}. "
                            f"Available: {product.stock}"
                        )
                    line_total = product.price * qty
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=qty,
                        price=product.price,
                    )
                    product.stock -= qty
                    product.save(update_fields=["stock", "updated_at"])
                    total += line_total
                order.total_price = total
                order.save(update_fields=["total_price", "updated_at"])
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        order = Order.objects.prefetch_related("items").get(pk=order.pk)
        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Order.objects.filter(
            customer=request.user, is_deleted=False
        ).prefetch_related("items")
        return Response(OrderSerializer(qs, many=True).data)


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            pk=pk,
            is_deleted=False,
        )
        if not request.user.is_staff and order.customer_id != request.user.id:
            return None
        return order

    def get(self, request, pk):
        order = self.get_object(request, pk)
        if order is None:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(OrderSerializer(order).data)


class OrderStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        order = get_object_or_404(Order, pk=pk, is_deleted=False)
        serializer = OrderStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if order.status == "Cancelled":
            return Response(
                {"error": "Cannot update a cancelled order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = serializer.validated_data["status"]
        order.save(update_fields=["status", "updated_at"])
        return Response(OrderSerializer(order).data)


class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related("items"),
            pk=pk,
            is_deleted=False,
        )
        if not request.user.is_staff and order.customer_id != request.user.id:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.status in ("Cancelled", "Completed"):
            return Response(
                {"error": f"Cannot cancel a {order.status} order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for item in order.items.select_related("product"):
                product = Product.objects.select_for_update().get(pk=item.product_id)
                product.stock += item.quantity
                product.save(update_fields=["stock", "updated_at"])
            order.status = "Cancelled"
            order.save(update_fields=["status", "updated_at"])

        return Response({"message": "Order cancelled", "data": OrderSerializer(order).data})