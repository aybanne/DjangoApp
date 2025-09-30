# store/models.py

import os
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from dotenv import load_dotenv
from django.utils.html import format_html

load_dotenv()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def save(self, *args, **kwargs):
        """Generate slug if missing and save product."""
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_or_fetch_image(self):
        """
        Returns the image URL.
        If missing, fetches an online image using Unsplash Source.
        """
        if self.image:
            return self.image.url

        # Generate Unsplash Source URL
        search_term = self.name.replace(" ", "+")
        return f"https://source.unsplash.com/400x300/?{search_term}"

    def image_preview(self):
        if self.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; object-fit: contain;" />',
                self.image.url
            )
        return "No Image"

    image_preview.short_description = 'Image Preview'
    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    alt = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.product.name} Image"


class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    shipping_address = models.TextField(blank=True, null=True)

    def total(self):
        return sum(item.total_price() for item in self.items.all())

    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Order #{self.id} by {self.user}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
