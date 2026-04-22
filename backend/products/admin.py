from django.contrib import admin

from .models import (
    Category, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, PriceList,
    ProductSupplier, StockMovement, ProductAttachment,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent']
    prepopulated_fields = {'slug': ('name',)}


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0


class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute
    extra = 0


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 0


class PriceListInline(admin.TabularInline):
    model = PriceList
    extra = 0


class ProductSupplierInline(admin.TabularInline):
    model = ProductSupplier
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'sku', 'name', 'status', 'product_type', 'category',
        'price', 'stock', 'updated_at',
    ]
    list_filter = ['status', 'product_type', 'category']
    search_fields = ['sku', 'name']
    inlines = [
        ProductImageInline, ProductAttributeInline,
        ProductVariantInline, PriceListInline, ProductSupplierInline,
    ]


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'document_ref', 'created_at']
    list_filter = ['movement_type']


@admin.register(ProductAttachment)
class ProductAttachmentAdmin(admin.ModelAdmin):
    list_display = ['product', 'file_name', 'file_size', 'uploaded_at']
