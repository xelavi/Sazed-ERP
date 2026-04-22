from rest_framework import serializers

from core.models import Tag, SalesChannel
from core.serializers import TagSerializer, SalesChannelSerializer
from .models import (
    Category, Product, ProductImage, ProductAttribute,
    ProductAttributeValue, ProductVariant, PriceList,
    ProductSupplier, StockMovement, ProductAttachment,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'parent', 'created_at']
        read_only_fields = ['slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'position', 'created_at']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'value', 'position']


class ProductAttributeSerializer(serializers.ModelSerializer):
    values = ProductAttributeValueSerializer(many=True, read_only=True)

    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'values']


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'sku', 'price', 'stock', 'ean']


class PriceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceList
        fields = ['id', 'name', 'price', 'valid_from', 'valid_to']


class ProductSupplierSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True,
    )

    class Meta:
        model = ProductSupplier
        fields = [
            'id', 'supplier', 'supplier_name', 'supplier_sku',
            'purchase_price', 'lead_time', 'min_order', 'is_primary',
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = [
            'id', 'movement_type', 'quantity', 'document_ref',
            'user', 'notes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class ProductAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttachment
        fields = ['id', 'file', 'file_name', 'file_size', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


# ---------- Product serializers ----------

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer para la tabla/listado de productos."""

    category = serializers.StringRelatedField()
    tax = serializers.CharField(source='tax_rate.name', read_only=True, default=None)
    supplier = serializers.SerializerMethodField()
    channels = serializers.StringRelatedField(many=True)
    has_variants = serializers.BooleanField(read_only=True)
    variants_count = serializers.IntegerField(read_only=True)
    margin = serializers.DecimalField(
        read_only=True, max_digits=5, decimal_places=1,
    )
    price_from = serializers.DecimalField(
        read_only=True, max_digits=12, decimal_places=2,
    )

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'status', 'product_type', 'category',
            'stock', 'reserved', 'price', 'price_from', 'has_variants',
            'variants_count', 'cost', 'tax', 'supplier', 'channels',
            'updated_at', 'image', 'margin',
        ]

    def get_supplier(self, obj):
        primary = obj.suppliers.filter(is_primary=True).first()
        return primary.supplier.name if primary else None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer para el detalle completo de un producto."""

    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    channels = SalesChannelSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    attributes = ProductAttributeSerializer(many=True, read_only=True)
    price_lists = PriceListSerializer(many=True, read_only=True)
    suppliers = ProductSupplierSerializer(many=True, read_only=True)
    stock_movements = StockMovementSerializer(many=True, read_only=True)
    gallery = ProductImageSerializer(many=True, read_only=True)
    attachments = ProductAttachmentSerializer(many=True, read_only=True)
    has_variants = serializers.BooleanField(read_only=True)
    variants_count = serializers.IntegerField(read_only=True)
    margin = serializers.DecimalField(
        read_only=True, max_digits=5, decimal_places=1,
    )
    price_from = serializers.DecimalField(
        read_only=True, max_digits=12, decimal_places=2,
    )
    tax = serializers.CharField(source='tax_rate.name', read_only=True, default=None)

    class Meta:
        model = Product
        fields = '__all__'


class ProductWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar productos."""

    tag_ids = serializers.PrimaryKeyRelatedField(
        source='tags', many=True, write_only=True,
        queryset=Tag.objects.all(),
        required=False,
    )
    channel_ids = serializers.PrimaryKeyRelatedField(
        source='channels', many=True, write_only=True,
        queryset=SalesChannel.objects.all(),
        required=False,
    )

    class Meta:
        model = Product
        fields = [
            'id', 'sku', 'name', 'description', 'product_type', 'status',
            'unit', 'category', 'brand', 'tag_ids', 'channel_ids',
            'price', 'price_excl_tax', 'cost', 'tax_rate', 'currency',
            'stock', 'reserved', 'min_stock', 'reorder_point',
            'warehouse', 'location', 'lot_tracking',
            'weight', 'dimensions', 'shipping_class', 'digital',
            'sellable', 'purchasable', 'image', 'notes',
            'created_by', 'modified_by',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        channels = validated_data.pop('channels', [])
        product = Product.objects.create(**validated_data)
        if tags:
            product.tags.set(tags)
        if channels:
            product.channels.set(channels)
        return product

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        channels = validated_data.pop('channels', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        if channels is not None:
            instance.channels.set(channels)
        return instance
