"""Tests del campo EncryptedTextField."""
import pytest
from cryptography.fernet import Fernet
from django.core.exceptions import ImproperlyConfigured

from accounting_sync import fields


def test_roundtrip_encryption(settings):
    settings.ODOO_ENCRYPTION_KEY = Fernet.generate_key().decode()
    fields._get_fernet.cache_clear()
    f = fields.EncryptedTextField()

    token = f.get_prep_value('hello secret')
    assert token != 'hello secret'
    assert isinstance(token, str)

    # from_db_value descifra
    plain = f.from_db_value(token, None, None)
    assert plain == 'hello secret'


def test_empty_values_pass_through():
    f = fields.EncryptedTextField()
    assert f.get_prep_value('') == ''
    assert f.get_prep_value(None) is None
    assert f.from_db_value('', None, None) == ''
    assert f.from_db_value(None, None, None) is None


def test_invalid_token_returns_empty():
    f = fields.EncryptedTextField()
    assert f.from_db_value('garbage-not-fernet', None, None) == ''


def test_missing_key_raises(settings):
    settings.ODOO_ENCRYPTION_KEY = ''
    fields._get_fernet.cache_clear()
    f = fields.EncryptedTextField()
    with pytest.raises(ImproperlyConfigured):
        f.get_prep_value('algo')
