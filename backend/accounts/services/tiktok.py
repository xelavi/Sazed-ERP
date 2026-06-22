"""
Thin wrapper around TikTok for Developers API v2.

OAuth flow (popup-based):
1. Backend /integrations/tiktok/init/     → stores state in session, redirects to TikTok
2. TikTok  → redirects to /integrations/tiktok/callback/
3. Backend → exchanges code, stores in SocialAccount, redirects to /oauth/done
"""

from __future__ import annotations

import secrets
import urllib.parse
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone


TIKTOK_AUTH_URL = 'https://www.tiktok.com/v2/auth/authorize/'
TIKTOK_TOKEN_URL = 'https://open.tiktokapis.com/v2/oauth/token/'
TIKTOK_REVOKE_URL = 'https://open.tiktokapis.com/v2/oauth/revoke/'
TIKTOK_API_BASE = 'https://open.tiktokapis.com/v2'

SCOPES = 'user.info.basic,video.list'


class TikTokAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


def _get_client_key() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('tiktok_client_key') or settings.TIKTOK_CLIENT_KEY
    except Exception:
        return settings.TIKTOK_CLIENT_KEY


def _get_client_secret() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('tiktok_client_secret') or settings.TIKTOK_CLIENT_SECRET
    except Exception:
        return settings.TIKTOK_CLIENT_SECRET


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def build_auth_url(redirect_uri: str, state: str) -> str:
    client_key = _get_client_key()
    if not client_key:
        raise TikTokAPIError('TikTok no está configurado en el servidor.', 500)

    params = {
        'client_key': client_key,
        'response_type': 'code',
        'scope': SCOPES,
        'redirect_uri': redirect_uri,
        'state': state,
    }
    return f'{TIKTOK_AUTH_URL}?{urllib.parse.urlencode(params)}'


def exchange_code(code: str, redirect_uri: str) -> dict:
    """Exchange authorization code for access_token + refresh_token."""
    client_key = _get_client_key()
    client_secret = _get_client_secret()
    if not client_key or not client_secret:
        raise TikTokAPIError('TikTok no está configurado en el servidor.', 500)

    try:
        resp = requests.post(
            TIKTOK_TOKEN_URL,
            data={
                'client_key': client_key,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TikTokAPIError(f'No se pudo conectar con TikTok: {exc}', 502)

    result = resp.json()
    # TikTok v2 token endpoint wraps errors at top-level: { error, error_description }
    if resp.status_code >= 400 or result.get('error'):
        msg = result.get('error_description') or result.get('error') or f'Error {resp.status_code}'
        raise TikTokAPIError(msg, resp.status_code, result)

    return result  # { access_token, refresh_token, expires_in, open_id, scope, ... }


def refresh_access_token(refresh_token: str) -> dict:
    client_key = _get_client_key()
    client_secret = _get_client_secret()

    try:
        resp = requests.post(
            TIKTOK_TOKEN_URL,
            data={
                'client_key': client_key,
                'client_secret': client_secret,
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TikTokAPIError(f'No se pudo renovar el token: {exc}', 502)

    result = resp.json()
    if resp.status_code >= 400 or result.get('error'):
        msg = result.get('error_description') or result.get('error') or f'Error {resp.status_code}'
        raise TikTokAPIError(msg, resp.status_code, result)

    return result


def get_user_info(access_token: str, open_id: str = '') -> dict:
    """Returns the authenticated user's TikTok profile."""
    params = {
        'fields': (
            'open_id,union_id,avatar_url,display_name,'
            'bio_description,follower_count,following_count,'
            'likes_count,video_count'
        ),
    }
    # open_id is optional; TikTok uses the token to identify the user
    if open_id:
        params['open_id'] = open_id

    try:
        resp = requests.get(
            f'{TIKTOK_API_BASE}/user/info/',
            params=params,
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TikTokAPIError(f'No se pudo conectar con TikTok: {exc}', 502)

    result = resp.json()
    error = result.get('error', {})
    if resp.status_code >= 400 or (error and error.get('code') != 'ok'):
        msg = error.get('message') or f'Error {resp.status_code}'
        raise TikTokAPIError(msg, resp.status_code, result)

    return result.get('data', {}).get('user', {})


def get_video_list(access_token: str, max_count: int = 10) -> list[dict]:
    """Returns recent videos for the authenticated user with analytics."""
    fields = (
        'id,title,video_description,duration,cover_image_url,embed_link,'
        'view_count,like_count,comment_count,share_count,create_time'
    )
    try:
        resp = requests.post(
            f'{TIKTOK_API_BASE}/video/list/',
            params={'fields': fields},
            json={'max_count': max_count},
            headers={
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
            },
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TikTokAPIError(f'No se pudo conectar con TikTok: {exc}', 502)

    result = resp.json()
    error = result.get('error', {})
    if resp.status_code >= 400 or (error and error.get('code') != 'ok'):
        msg = error.get('message') or f'Error {resp.status_code}'
        raise TikTokAPIError(msg, resp.status_code, result)

    return result.get('data', {}).get('videos', [])


def expires_at_from(expires_in: int | str | None):
    if not expires_in:
        return None
    return timezone.now() + timedelta(seconds=int(expires_in))
