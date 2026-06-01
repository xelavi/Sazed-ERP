"""Tests de la API REST de integración Odoo."""
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client(admin_user):
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.mark.django_db
def test_create_odoo_connection_requires_admin(company):
    """Usuario sin membership admin no puede crear OdooConnection."""
    from accounts.models import User, Membership
    viewer = User.objects.create_user(email='viewer@example.com', password='x')
    Membership.objects.create(user=viewer, company=company, role='viewer')

    client = APIClient()
    client.force_authenticate(user=viewer)
    resp = client.post('/api/integrations/odoo/connections/', {
        'company': company.id,
        'base_url': 'http://localhost:8069',
        'database': 'demo',
        'username': 'api',
        'password': 'secret',
    }, format='json')
    assert resp.status_code == 403


@pytest.mark.django_db
def test_create_and_list_connection(api_client, company):
    resp = api_client.post('/api/integrations/odoo/connections/', {
        'company': company.id,
        'base_url': 'http://localhost:8069',
        'database': 'demo',
        'username': 'api',
        'password': 'secret-pwd',
    }, format='json')
    assert resp.status_code == 201, resp.content

    # Password no se devuelve en la respuesta
    assert 'password' not in resp.json()

    resp = api_client.get('/api/integrations/odoo/connections/')
    assert resp.status_code == 200
    payload = resp.json()
    items = payload.get('results', payload)
    assert len(items) == 1


@pytest.mark.django_db
def test_test_connection_ok(api_client):
    with patch('accounting_sync.views.OdooClient') as MockClient:
        instance = MockClient.return_value
        instance.connect.return_value = 7
        instance.server_version.return_value = '17.0'
        instance.list_modules_installed.return_value = {
            'l10n_es': True, 'l10n_es_aeat': False,
        }
        resp = api_client.post(
            '/api/integrations/odoo/test-connection/',
            {
                'base_url': 'http://localhost:8069',
                'database': 'demo',
                'username': 'api',
                'password': 'secret',
            },
            format='json',
        )
    assert resp.status_code == 200, resp.content
    body = resp.json()
    assert body['ok'] is True
    assert body['server_version'] == '17.0'
    assert body['modules'] == {'l10n_es': True, 'l10n_es_aeat': False}


@pytest.mark.django_db
def test_test_connection_failure(api_client):
    from accounting_sync.odoo_client import OdooConnectionError

    with patch('accounting_sync.views.OdooClient') as MockClient:
        instance = MockClient.return_value
        instance.connect.side_effect = OdooConnectionError('auth failed')
        resp = api_client.post(
            '/api/integrations/odoo/test-connection/',
            {
                'base_url': 'http://localhost:8069',
                'database': 'demo',
                'username': 'api',
                'password': 'wrong',
            },
            format='json',
        )
    assert resp.status_code == 400
    assert resp.json()['ok'] is False
    assert 'auth failed' in resp.json()['error']


@pytest.mark.django_db
def test_sync_log_endpoint_read_only(api_client, company, odoo_connection):
    from accounting_sync.models import SyncLog
    SyncLog.objects.create(
        company=company, entity_type='customer', entity_id='1',
        operation='PUSH', odoo_method='create', success=True,
    )

    # List works
    resp = api_client.get('/api/integrations/odoo/sync-logs/')
    assert resp.status_code == 200

    # POST not allowed (no create mixin)
    resp = api_client.post('/api/integrations/odoo/sync-logs/', {
        'company': company.id, 'entity_type': 'x', 'operation': 'PUSH',
        'odoo_method': 'create',
    }, format='json')
    assert resp.status_code == 405
