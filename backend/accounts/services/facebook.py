"""
Thin wrapper around Facebook Graph API.

We avoid the unmaintained `facebook-sdk` package and call Graph directly
with `requests`. Reads credentials from SystemSettings (DB) with .env fallback.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import requests
from django.conf import settings
from django.utils import timezone

def _get_app_id():
    """Get Facebook App ID from DB (SystemSettings) or .env."""
    try:
        from ..models import SystemSettings
        return SystemSettings.get('facebook_app_id') or settings.FACEBOOK_APP_ID
    except Exception:
        return settings.FACEBOOK_APP_ID

def _get_app_secret():
    """Get Facebook App Secret from DB (SystemSettings) or .env."""
    try:
        from ..models import SystemSettings
        return SystemSettings.get('facebook_app_secret') or settings.FACEBOOK_APP_SECRET
    except Exception:
        return settings.FACEBOOK_APP_SECRET


GRAPH_BASE = 'https://graph.facebook.com'


class FacebookAPIError(Exception):
    """Raised when Graph API returns an error or the token is invalid."""

    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


def _graph_url(path: str) -> str:
    version = settings.FACEBOOK_GRAPH_VERSION
    path = path.lstrip('/')
    return f'{GRAPH_BASE}/{version}/{path}'


def _request(method: str, path: str, params: dict | None = None) -> dict:
    url = _graph_url(path)
    try:
        resp = requests.request(method, url, params=params or {}, timeout=15)
    except requests.RequestException as exc:
        raise FacebookAPIError(f'No se pudo conectar con Facebook: {exc}', 502)

    if resp.status_code >= 400:
        try:
            payload = resp.json()
        except ValueError:
            payload = {'raw': resp.text}
        message = (
            payload.get('error', {}).get('message')
            if isinstance(payload, dict) else None
        ) or f'Graph API error {resp.status_code}'
        raise FacebookAPIError(message, resp.status_code, payload)

    return resp.json()


def graph_get(path: str, token: str, params: dict | None = None) -> dict:
    """Generic authenticated GET against Graph API."""
    merged = {'access_token': token, **(params or {})}
    return _request('GET', path, merged)


# ── Token operations ───────────────────────────────────


def debug_token(input_token: str) -> dict:
    """
    Verify that `input_token` was issued for our app and is still valid.
    Uses an app-access-token (app_id|app_secret) which Facebook accepts
    for the debug_token endpoint.
    """
    app_id = _get_app_id()
    app_secret = _get_app_secret()
    if not app_id or not app_secret:
        raise FacebookAPIError('Facebook no está configurado en el servidor.', 500)

    app_token = f'{app_id}|{app_secret}'
    data = _request('GET', 'debug_token', {
        'input_token': input_token,
        'access_token': app_token,
    }).get('data', {})

    if not data.get('is_valid'):
        raise FacebookAPIError(
            data.get('error', {}).get('message') or 'Token de Facebook no válido.',
            401,
            data,
        )
    if str(data.get('app_id')) != str(app_id):
        raise FacebookAPIError('El token no pertenece a esta aplicación.', 401, data)

    return data


def exchange_for_long_lived(short_token: str) -> dict:
    """
    Exchange a short-lived user access token for a long-lived one (~60 days).
    Returns {'access_token': ..., 'expires_in': seconds}.
    """
    app_id = _get_app_id()
    app_secret = _get_app_secret()
    return _request('GET', 'oauth/access_token', {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': short_token,
    })


def get_me(token: str) -> dict:
    """Returns the FB user profile (id, email, name, picture)."""
    return graph_get('me', token, {'fields': 'id,email,name,first_name,last_name,picture'})


def list_pages(token: str) -> list[dict]:
    """Pages the user manages. Each item carries its own page-scoped token."""
    data = graph_get('me/accounts', token, {
        'fields': 'id,name,category,access_token,tasks',
    })
    return data.get('data', [])


def get_instagram_for_page(page_id: str, page_token: str) -> dict | None:
    """
    Returns the Instagram Business account linked to a Facebook Page, if any.
    Requires a page-scoped token (from `list_pages`) and `instagram_basic`.
    """
    data = graph_get(page_id, page_token, {
        'fields': 'instagram_business_account{id,username,name,profile_picture_url,followers_count,media_count}',
    })
    return data.get('instagram_business_account')


# ── Helpers ────────────────────────────────────────────


def expires_at_from(expires_in: int | None):
    if not expires_in:
        return None
    return timezone.now() + timedelta(seconds=int(expires_in))
