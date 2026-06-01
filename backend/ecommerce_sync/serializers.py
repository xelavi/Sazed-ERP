"""Serializers de la API de integración e-commerce."""
from __future__ import annotations

from rest_framework import serializers

from .models import EcommerceSyncLog, StoreConnection, StoreTaxMapping


class StoreConnectionSerializer(serializers.ModelSerializer):
    """La API key se escribe pero nunca se devuelve."""

    api_key = serializers.CharField(write_only=True)
    has_api_key = serializers.SerializerMethodField()

    class Meta:
        model = StoreConnection
        fields = [
            'id', 'company', 'platform', 'base_url',
            'api_key', 'has_api_key',
            'is_active', 'push_products', 'push_customers', 'pull_orders',
            'last_sync_at', 'last_sync_status', 'last_sync_error',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'last_sync_at', 'last_sync_status', 'last_sync_error',
            'created_at', 'updated_at',
        ]

    def get_has_api_key(self, obj) -> bool:
        return bool(obj.api_key)


class StoreConnectionUpdateSerializer(StoreConnectionSerializer):
    """En update la api_key es opcional (no se reescribe si no se envía)."""

    api_key = serializers.CharField(write_only=True, required=False, allow_blank=True)

    def update(self, instance, validated_data):
        if not validated_data.get('api_key'):
            validated_data.pop('api_key', None)
        return super().update(instance, validated_data)


class StoreTaxMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoreTaxMapping
        fields = '__all__'


class EcommerceSyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcommerceSyncLog
        fields = '__all__'


class TestConnectionSerializer(serializers.Serializer):
    """Verifica credenciales sin persistirlas."""

    platform = serializers.ChoiceField(
        choices=StoreConnection.Platform.choices,
        default=StoreConnection.Platform.PRESTASHOP,
    )
    base_url = serializers.URLField()
    api_key = serializers.CharField()
