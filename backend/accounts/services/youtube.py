"""
Thin wrapper around YouTube Data API v3 and Google OAuth 2.0.
Uses requests directly to avoid the heavy google-auth-oauthlib dependency.

Token flow used: Google Identity Services (GIS) implicit token flow.
The frontend obtains an access_token via GIS initTokenClient (popup).
The backend validates it via tokeninfo and stores it.
Access tokens last ~1 hour; re-authorization is triggered transparently.
"""

from __future__ import annotations

from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone


TOKENINFO_URL = 'https://oauth2.googleapis.com/tokeninfo'
USERINFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
YOUTUBE_BASE = 'https://www.googleapis.com/youtube/v3'


class YouTubeAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


def _get_client_id() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('youtube_client_id') or settings.YOUTUBE_CLIENT_ID
    except Exception:
        return settings.YOUTUBE_CLIENT_ID


def _get_client_secret() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('youtube_client_secret') or settings.YOUTUBE_CLIENT_SECRET
    except Exception:
        return settings.YOUTUBE_CLIENT_SECRET


# ── Token validation ───────────────────────────────────


def validate_token(access_token: str) -> dict:
    """
    Validate an access token via Google's tokeninfo endpoint.
    Returns token metadata including sub (user id), scope, exp.
    Raises YouTubeAPIError if token is invalid or expired.
    """
    try:
        resp = requests.get(TOKENINFO_URL, params={'access_token': access_token}, timeout=15)
    except requests.RequestException as exc:
        raise YouTubeAPIError(f'No se pudo conectar con Google: {exc}', 502)

    data = resp.json()
    if resp.status_code >= 400 or 'error_description' in data:
        msg = data.get('error_description') or data.get('error') or f'Token inválido ({resp.status_code})'
        raise YouTubeAPIError(msg, 401, data)

    client_id = _get_client_id()
    if client_id and data.get('aud') != client_id:
        raise YouTubeAPIError('El token no pertenece a esta aplicación.', 401, data)

    return data


def get_userinfo(access_token: str) -> dict:
    """Returns Google user profile (sub, email, name, picture)."""
    try:
        resp = requests.get(USERINFO_URL, params={'access_token': access_token}, timeout=15)
    except requests.RequestException as exc:
        raise YouTubeAPIError(f'No se pudo obtener el perfil de Google: {exc}', 502)

    data = resp.json()
    if resp.status_code >= 400:
        msg = data.get('error_description') or data.get('error') or f'Error {resp.status_code}'
        raise YouTubeAPIError(msg, resp.status_code, data)

    return data  # { sub, email, name, picture, ... }


# ── YouTube Data API v3 ────────────────────────────────


def _yt_get(path: str, access_token: str, params: dict | None = None) -> dict:
    url = f'{YOUTUBE_BASE}/{path.lstrip("/")}'
    merged = {'access_token': access_token, **(params or {})}
    try:
        resp = requests.get(url, params=merged, timeout=15)
    except requests.RequestException as exc:
        raise YouTubeAPIError(f'No se pudo conectar con YouTube: {exc}', 502)

    data = resp.json()
    if resp.status_code >= 400:
        msg = (data.get('error') or {}).get('message') or f'Error {resp.status_code}'
        raise YouTubeAPIError(msg, resp.status_code, data)

    return data


def get_channels(access_token: str) -> list[dict]:
    """Returns YouTube channels owned by the authenticated user."""
    data = _yt_get('channels', access_token, {
        'part': 'snippet,statistics,brandingSettings',
        'mine': 'true',
    })
    return data.get('items', [])


def get_recent_videos(access_token: str, channel_id: str, max_results: int = 10) -> list[dict]:
    """Returns recent videos for a channel with their statistics."""
    search = _yt_get('search', access_token, {
        'part': 'snippet',
        'channelId': channel_id,
        'type': 'video',
        'order': 'date',
        'maxResults': max_results,
    })

    video_ids = [item['id']['videoId'] for item in search.get('items', []) if item.get('id', {}).get('videoId')]
    if not video_ids:
        return []

    stats = _yt_get('videos', access_token, {
        'part': 'snippet,statistics',
        'id': ','.join(video_ids),
    })
    return stats.get('items', [])


# ── Helpers ────────────────────────────────────────────


def expires_at_from(expires_in: int | str | None):
    if not expires_in:
        return None
    return timezone.now() + timedelta(seconds=int(expires_in))
