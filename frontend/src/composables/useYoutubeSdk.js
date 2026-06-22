/**
 * Lazy wrapper around Google Identity Services (GIS) for YouTube.
 * Uses the implicit token flow: GIS opens a popup, returns an access_token
 * directly to the JS callback (no redirect URI needed).
 *
 * The access_token is valid for ~1 hour.
 * Backend validates it via Google tokeninfo and stores it.
 *
 *   const { ready, login } = useYoutubeSdk()
 *   await ready()
 *   const { access_token } = await login()
 */
import { get } from '@/services/api'

const GIS_URL = 'https://accounts.google.com/gsi/client'

// Scopes: read channel stats and video data.
// 'youtube.readonly' covers channels + videos + statistics.
const SCOPE = [
  'https://www.googleapis.com/auth/youtube.readonly',
  'openid',
  'profile',
  'email',
].join(' ')

let readyPromise = null

async function fetchClientId() {
  try {
    const data = await get('/settings/youtube/client-id/')
    if (!data.configured) throw new Error('not_configured')
    return data.youtube_client_id
  } catch (err) {
    if (err.message === 'not_configured') {
      throw new Error('YouTube no está configurado aún. Un administrador debe añadir el Client ID en Configuración.')
    }
    throw new Error('No se pudo obtener la configuración de YouTube del servidor.')
  }
}

function loadGIS() {
  return new Promise((resolve, reject) => {
    if (window.google?.accounts?.oauth2) return resolve()
    const existing = document.querySelector(`script[src="${GIS_URL}"]`)
    if (existing) {
      existing.addEventListener('load', resolve)
      existing.addEventListener('error', () => reject(new Error('No se pudo cargar Google Identity Services.')))
      return
    }
    const script = document.createElement('script')
    script.src = GIS_URL
    script.async = true
    script.defer = true
    script.onload = resolve
    script.onerror = () => reject(new Error('No se pudo cargar Google Identity Services.'))
    document.head.appendChild(script)
  })
}

export function useYoutubeSdk() {
  function ready() {
    if (readyPromise) return readyPromise
    readyPromise = Promise.all([fetchClientId(), loadGIS()])
      .then(([clientId]) => clientId)
      .catch(err => {
        readyPromise = null
        throw err
      })
    return readyPromise
  }

  function login() {
    return ready().then(clientId => new Promise((resolve, reject) => {
      const client = window.google.accounts.oauth2.initTokenClient({
        client_id: clientId,
        scope: SCOPE,
        callback: response => {
          if (response.error) {
            reject(new Error(response.error_description || response.error || 'Error de autenticación con Google.'))
          } else {
            resolve({
              access_token: response.access_token,
              expires_in: response.expires_in,
              scope: response.scope,
            })
          }
        },
        error_callback: err => {
          if (err.type === 'popup_closed') {
            reject(new Error('Ventana de Google cerrada.'))
          } else {
            reject(new Error(err.message || 'Error al conectar con Google.'))
          }
        },
      })
      client.requestAccessToken()
    }))
  }

  function revoke(accessToken) {
    return new Promise(resolve => {
      if (!window.google?.accounts?.oauth2) return resolve()
      window.google.accounts.oauth2.revoke(accessToken, resolve)
    })
  }

  return { ready, login, revoke }
}
