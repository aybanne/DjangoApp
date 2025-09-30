from django.contrib import admin
from django.utils.html import format_html
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'image_preview')  # Show the preview in list
    readonly_fields = ('image_preview',)  # Make preview read-only in the form

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 150px; max-height: 150px; object-fit: contain;" />',
                obj.image.url
            )
        return "No Image"

    image_preview.short_description = 'Image Preview'
