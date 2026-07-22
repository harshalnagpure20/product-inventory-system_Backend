from django.db import models
from products.models import Product
from categories.models import TimestampedModel
from django.contrib.auth.models import User

# Create your models here.
class Order(TimestampedModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Processing", "Processing"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE,related_name="orders")
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )
    def __str__(self):
        return f"Order {self.id} - {self.customer.username}"
    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ["-created_at"]  
        db_table = "orders" 
        indexes = [
            models.Index(fields=["customer"]),
        ]


class OrderItem(TimestampedModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="order_items"
    )
    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )
    def __str__(self):
        return self.product.name
    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"
        ordering = ["-created_at"]  
        db_table = "order_items" 
        indexes = [
            models.Index(fields=["product"]),
        ]