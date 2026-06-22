"""
Thin wrapper around X (Twitter) API v2 with OAuth 2.0 PKCE.

OAuth flow (popup-based):
1. Backend /integrations/twitter/init/  → generates PKCE, stores in session, redirects to Twitter
2. Twitter  → redirects to /integrations/twitter/callback/
3. Backend  → exchanges code for tokens, stores in SocialAccount, redirects to /oauth/done
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import urllib.parse
from datetime import timedelta

import requests
from django.conf import settings
from django.utils import timezone


TWITTER_AUTH_URL = 'https://twitter.com/i/oauth2/authorize'
TWITTER_TOKEN_URL = 'https://api.twitter.com/2/oauth2/token'
TWITTER_API_BASE = 'https://api.twitter.com/2'

SCOPES = 'tweet.read users.read follows.read offline.access'


class TwitterAPIError(Exception):
    def __init__(self, message: str, status_code: int = 400, payload: dict | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


def _get_client_id() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('twitter_client_id') or settings.TWITTER_CLIENT_ID
    except Exception:
        return settings.TWITTER_CLIENT_ID


def _get_client_secret() -> str:
    try:
        from ..models import SystemSettings
        return SystemSettings.get('twitter_client_secret') or settings.TWITTER_CLIENT_SECRET
    except Exception:
        return settings.TWITTER_CLIENT_SECRET


# ── PKCE helpers ───────────────────────────────────────


def generate_code_verifier() -> str:
    return secrets.token_urlsafe(43)


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode()


# ── OAuth URL builder ──────────────────────────────────


def build_auth_url(redirect_uri: str, state: str, code_challenge: str) -> str:
    client_id = _get_client_id()
    if not client_id:
        raise TwitterAPIError('X (Twitter) no está configurado en el servidor.', 500)

    params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'scope': SCOPES,
        'state': state,
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256',
    }
    return f'{TWITTER_AUTH_URL}?{urllib.parse.urlencode(params)}'


# ── Token exchange ─────────────────────────────────────


def exchange_code(code: str, code_verifier: str, redirect_uri: str) -> dict:
    """Exchange authorization code for access_token + refresh_token."""
    client_id = _get_client_id()
    client_secret = _get_client_secret()
    if not client_id:
        raise TwitterAPIError('X (Twitter) no está configurado en el servidor.', 500)

    # Confidential clients use HTTP Basic Auth; public clients omit auth.
    auth = (client_id, client_secret) if client_secret else None

    try:
        resp = requests.post(
            TWITTER_TOKEN_URL,
            data={
                'code': code,
                'grant_type': 'authorization_code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'code_verifier': code_verifier,
            },
            auth=auth,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TwitterAPIError(f'No se pudo conectar con X: {exc}', 502)

    result = resp.json()
    if resp.status_code >= 400 or 'error' in result:
        msg = result.get('error_description') or result.get('error') or f'Error {resp.status_code}'
        raise TwitterAPIError(msg, resp.status_code, result)

    return result  # { access_token, refresh_token, expires_in, token_type, scope }


def refresh_access_token(refresh_token: str) -> dict:
    client_id = _get_client_id()
    client_secret = _get_client_secret()
    auth = (client_id, client_secret) if client_secret else None

    try:
        resp = requests.post(
            TWITTER_TOKEN_URL,
            data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id,
            },
            auth=auth,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TwitterAPIError(f'No se pudo renovar el token: {exc}', 502)

    result = resp.json()
    if resp.status_code >= 400 or 'error' in result:
        msg = result.get('error_description') or result.get('error') or f'Error {resp.status_code}'
        raise TwitterAPIError(msg, resp.status_code, result)

    return result


# ── Twitter API v2 calls ───────────────────────────────


def get_me(access_token: str) -> dict:
    """Returns the authenticated user's profile with public metrics."""
    try:
        resp = requests.get(
            f'{TWITTER_API_BASE}/users/me',
            params={'user.fields': 'id,name,username,profile_image_url,public_metrics,description'},
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TwitterAPIError(f'No se pudo conectar con X: {exc}', 502)

    data = resp.json()
    if resp.status_code >= 400 or 'errors' in data:
        errors = data.get('errors', [{}])
        msg = errors[0].get('detail') if errors else f'Error {resp.status_code}'
        raise TwitterAPIError(msg or f'Error {resp.status_code}', resp.status_code, data)

    return data.get('data', {})


def get_user_tweets(user_id: str, access_token: str, max_results: int = 10) -> list[dict]:
    """Returns recent tweets with public metrics (likes, retweets, impressions)."""
    try:
        resp = requests.get(
            f'{TWITTER_API_BASE}/users/{user_id}/tweets',
            params={
                'max_results': max_results,
                'tweet.fields': 'public_metrics,created_at,text',
            },
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=15,
        )
    except requests.RequestException as exc:
        raise TwitterAPIError(f'No se pudo conectar con X: {exc}', 502)

    data = resp.json()
    if resp.status_code >= 400:
        errors = data.get('errors', [{}])
        msg = errors[0].get('detail') if errors else f'Error {resp.status_code}'
        raise TwitterAPIError(msg or f'Error {resp.status_code}', resp.status_code, data)

    return data.get('data', [])


# ── Helpers ────────────────────────────────────────────


def expires_at_from(expires_in: int | str | None):
    if not expires_in:
        return None
    return timezone.now() + timedelta(seconds=int(expires_in))
