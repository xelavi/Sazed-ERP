"""Fixtures comunes para tests de accounting_sync."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from cryptography.fernet import Fernet
from django.conf import settings


@pytest.fixture(autouse=True)
def _ensure_encryption_key(settings):  # noqa: F811
    """Asegura una clave Fernet válida durante los tests."""
    if not getattr(settings, 'ODOO_ENCRYPTION_KEY', ''):
        settings.ODOO_ENCRYPTION_KEY = Fernet.generate_key().decode()
    # Limpia la caché del Fernet (se hizo lru_cache) si se cambió la key
    from accounting_sync import fields
    fields._get_fernet.cache_clear()
    yield


@pytest.fixture
def company(db):
    from accounts.models import Company, User
    user = User.objects.create_user(email='owner@example.com', password='x')
    company = Company.objects.create(
        name='Demo Co', slug='demo-co', created_by=user,
    )
    from accounts.models import Membership
    Membership.objects.create(user=user, company=company, role='owner', is_default=True)
    company._owner = user  # acceso conveniente desde tests
    return company


@pytest.fixture
def admin_user(company):
    return company._owner


@pytest.fixture
def odoo_connection(db, company):
    from accounting_sync.models import OdooConnection
    return OdooConnection.objects.create(
        company=company,
        base_url='http://localhost:8069',
        database='test_db',
        username='api',
        password='secret-pwd',
    )


@pytest.fixture
def mock_odoorpc(monkeypatch):
    """Reemplaza `odoorpc.ODOO` por un MagicMock cazable desde el test."""
    import odoorpc
    fake_odoo = MagicMock(name='OdooInstance')
    fake_odoo.env.uid = 7
    fake_odoo.version = '17.0'
    factory = MagicMock(name='odoorpc.ODOO', return_value=fake_odoo)
    monkeypatch.setattr(odoorpc, 'ODOO', factory)
    return {'factory': factory, 'odoo': fake_odoo}


@pytest.fixture
def fake_client():
    """OdooClient con todos los métodos de red mockeados."""
    from accounting_sync.odoo_client import OdooClient
    client = OdooClient(
        base_url='http://localhost:8069',
        database='test',
        username='api',
        password='pwd',
    )
    client._search = MagicMock(return_value=[])
    client._read = MagicMock(return_value=[])
    client._create = MagicMock(return_value=999)
    client._write = MagicMock(return_value=True)
    client._call = MagicMock(return_value=[])
    client.connect = MagicMock(return_value=1)
    client.find_country_id = MagicMock(return_value=69)
    return client
