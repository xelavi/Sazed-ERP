"""Tests del cliente Odoo (sin red, todo mockeado)."""
from unittest.mock import MagicMock

import pytest
from odoorpc.error import RPCError

from accounting_sync.odoo_client import OdooClient, OdooConnectionError


@pytest.mark.django_db
def test_connect_returns_uid(mock_odoorpc):
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    uid = client.connect()
    assert uid == 7
    mock_odoorpc['odoo'].login.assert_called_once_with('db', 'user', 'pwd')


@pytest.mark.django_db
def test_connect_failure_raises(mock_odoorpc):
    mock_odoorpc['odoo'].login.side_effect = ConnectionError('boom')
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    with pytest.raises(OdooConnectionError):
        client.connect()


@pytest.mark.django_db
def test_password_not_logged(caplog, mock_odoorpc):
    client = OdooClient('http://localhost:8069', 'db', 'user', 'super-secret-password')
    with caplog.at_level('INFO'):
        client.connect()
    for record in caplog.records:
        assert 'super-secret-password' not in record.getMessage()


@pytest.mark.django_db
def test_https_protocol_detected(mock_odoorpc):
    client = OdooClient('https://odoo.example.com', 'db', 'user', 'pwd')
    assert client.protocol == 'jsonrpc+ssl'
    assert client.port == 443


@pytest.mark.django_db
def test_find_partner_by_vat_hits_search(mock_odoorpc):
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    client.connect()
    fake_partner_model = MagicMock()
    fake_partner_model.search.return_value = [42]
    mock_odoorpc['odoo'].env.__getitem__.return_value = fake_partner_model

    result = client.find_partner_by_vat('ESB12345678')
    assert result == 42
    fake_partner_model.search.assert_called_once_with(
        [('vat', '=', 'ESB12345678')], limit=1,
    )


@pytest.mark.django_db
def test_create_partner_returns_id(mock_odoorpc):
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    client.connect()
    model = MagicMock()
    model.create.return_value = 99
    mock_odoorpc['odoo'].env.__getitem__.return_value = model

    new_id = client.create_partner({'name': 'X'})
    assert new_id == 99


@pytest.mark.django_db
def test_retries_on_transient_rpc_error(mock_odoorpc):
    """Tras dos RPCError transitorios, el tercer intento debe acertar."""
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    client.connect()
    model = MagicMock()
    model.search.side_effect = [RPCError('temp'), RPCError('temp'), [7]]
    mock_odoorpc['odoo'].env.__getitem__.return_value = model

    result = client.find_partner_by_vat('ESB1')
    assert result == 7
    assert model.search.call_count == 3


@pytest.mark.django_db
def test_list_modules_installed(mock_odoorpc):
    client = OdooClient('http://localhost:8069', 'db', 'user', 'pwd')
    client.connect()
    model = MagicMock()
    model.search_read.return_value = [
        {'name': 'l10n_es', 'state': 'installed'},
        {'name': 'l10n_es_aeat', 'state': 'uninstalled'},
    ]
    mock_odoorpc['odoo'].env.__getitem__.return_value = model

    result = client.list_modules_installed(['l10n_es', 'l10n_es_aeat'])
    assert result == {'l10n_es': True, 'l10n_es_aeat': False}
