from rest_framework import serializers

from .models import TaxRate, Tag, Warehouse, SalesChannel


class TaxRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxRate
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = '__all__'


class SalesChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesChannel
        fields = '__all__'
