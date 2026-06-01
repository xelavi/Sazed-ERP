"""Serializers DRF para accounting_sync."""
from __future__ import annotations

from rest_framework import serializers

from .models import OdooConnection, OdooProvisioningJob, OdooTaxMapping, SyncLog


class OdooConnectionSerializer(serializers.ModelSerializer):
    """Serializer principal: password write-only, nunca expuesto."""

    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    class Meta:
        model = OdooConnection
        fields = [
            'id', 'company', 'base_url', 'database', 'username', 'password',
            'is_active', 'last_sync_at', 'last_sync_status', 'last_sync_error',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'last_sync_at', 'last_sync_status', 'last_sync_error',
            'created_at', 'updated_at',
        ]


class OdooConnectionUpdateSerializer(serializers.ModelSerializer):
    """Variante para PATCH: password opcional (no se sobrescribe si va vacío)."""

    password = serializers.CharField(write_only=True, required=False, allow_blank=False)

    class Meta:
        model = OdooConnection
        fields = [
            'base_url', 'database', 'username', 'password', 'is_active',
        ]


class TestConnectionSerializer(serializers.Serializer):
    """Body del endpoint test-connection: credenciales sin persistir."""

    base_url = serializers.URLField()
    database = serializers.CharField(max_length=100)
    username = serializers.CharField(max_length=200)
    password = serializers.CharField(write_only=True, allow_blank=False)


class OdooTaxMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = OdooTaxMapping
        fields = [
            'id', 'company', 'tax_rate', 'direction',
            'odoo_tax_id', 'odoo_tax_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class OdooProvisioningJobSerializer(serializers.ModelSerializer):
    """Estado del provisioning automático para el frontend (polling)."""

    class Meta:
        model = OdooProvisioningJob
        fields = [
            'id', 'company', 'status', 'database_name',
            'attempts', 'max_attempts',
            'logs', 'error_message',
            'created_at', 'started_at', 'finished_at',
        ]
        read_only_fields = fields


class SyncLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyncLog
        fields = [
            'id', 'company', 'user', 'entity_type', 'entity_id', 'odoo_id',
            'operation', 'odoo_method', 'success', 'request_payload_hash',
            'response_excerpt', 'error_message', 'duration_ms', 'created_at',
        ]
        read_only_fields = fields  # log es inmutable desde API
