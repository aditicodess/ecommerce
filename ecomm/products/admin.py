from csv import list_dialects
from django.contrib import admin
from .models import *


admin.site.register(Coupon)


class ProductImageAdmin(admin.StackedInline):
    model = ProductImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["category_name", "uid"]
    model = Category


class ProductAdmin(admin.ModelAdmin):
    list_display = ["product_name", "uid", "price"]
    inlines = [ProductImageAdmin]


@admin.register(ColorVariant)
class ColorVariantAdmin(admin.ModelAdmin):
    list_display = ["color_name", "uid", "price"]
    model = ColorVariant


@admin.register(SizeVariant)
class SizeVariantAdmin(admin.ModelAdmin):
    list_display = ["size_name", "uid", "price"]
    model = SizeVariant


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
