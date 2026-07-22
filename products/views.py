from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
import csv

from .models import Product
from .serializers import ProductSerializer
from .permission import IsAdmin


class ProductListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get(self, request):
        queryset = Product.objects.filter(is_deleted=False)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(name__icontains=search)

        category = request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        sort = request.query_params.get("sort")
        if sort:
            queryset = queryset.order_by(sort)

        paginator = PageNumberPagination()
        paginator.page_size = 10
        result = paginator.paginate_queryset(queryset, request)
        serializer = ProductSerializer(result, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductExportCSVAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        products = (
            Product.objects.filter(is_deleted=False)
            .select_related("category")
            .order_by("-created_at")
        )

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="products.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "id",
                "name",
                "description",
                "price",
                "stock",
                "category_id",
                "category_name",
                "is_active",
                "created_at",
                "updated_at",
            ]
        )

        for product in products:
            writer.writerow(
                [
                    product.id,
                    product.name,
                    product.description or "",
                    product.price,
                    product.stock,
                    product.category_id,
                    product.category.name if product.category_id else "",
                    product.is_active,
                    product.created_at.isoformat() if product.created_at else "",
                    product.updated_at.isoformat() if product.updated_at else "",
                ]
            )

        return response


class ProductDetailAPIView(APIView):
    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

    def get_object(self, pk):
        return get_object_or_404(Product, pk=pk, is_deleted=False)

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        product = self.get_object(pk)
        product.is_deleted = True
        product.deleted_at = timezone.now()
        product.save(update_fields=["is_deleted", "deleted_at", "updated_at"])
        return Response(
            {"message": "Product deleted successfully"},
            status=status.HTTP_200_OK,
        )
