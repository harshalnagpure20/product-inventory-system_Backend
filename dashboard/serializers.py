from rest_framework import serializers


class AdminDashboardSerializer(serializers.Serializer):
    total_products = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()
    low_stock_products = serializers.ListField()
    total_orders = serializers.IntegerField()
    revenue = serializers.DecimalField(max_digits=14, decimal_places=2)


class CustomerDashboardSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    recent_orders = serializers.ListField()
