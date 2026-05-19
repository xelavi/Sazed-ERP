/**
 * Lazy wrapper around the Facebook JS SDK.
 * Fetches the App ID from the backend (SystemSettings) so no .env is needed.
 *
 *   const { ready, login } = useFacebookSdk()
 *   await ready()
 *   const { accessToken } = await login()
 */
import { get } from '@/services/api'

const VERSION = 'v19.0'
// Scopes without App Review (standard access, development-safe).
// pages_manage_metadata, instagram_manage_insights, business_management
// require Advanced Access (App Review) — add them after review is approved.
const SCOPE = [
  'email',
  'public_profile',
  'pages_show_list',
  'pages_read_engagement',
  'instagram_basic',
].join(',')

let readyPromise = null

async function fetchAppId() {
  try {
    const data = await get('/settings/facebook/app-id/')
    if (!data.configured) throw new Error('not_configured')
    return data.facebook_app_id
  } catch (err) {
    if (err.message === 'not_configured') {
      throw new Error('Facebook no está configurado aún. Un administrador debe añadir el App ID en Configuración.')
    }
    throw new Error('No se pudo obtener la configuración de Facebook del servidor.')
  }
}

function waitForGlobal() {
  return new Promise((resolve, reject) => {
    if (window.FB) return resolve(window.FB)
    let tries = 0
    const interval = setInterval(() => {
      if (window.FB) {
        clearInterval(interval)
        resolve(window.FB)
      } else if (++tries > 100) {
        clearInterval(interval)
        reject(new Error('No se pudo cargar el SDK de Facebook.'))
      }
    }, 100)
  })
}

export function useFacebookSdk() {
  function ready() {
    if (readyPromise) return readyPromise
    readyPromise = Promise.all([fetchAppId(), waitForGlobal()])
      .then(([appId, FB]) => {
        FB.init({ appId, version: VERSION, xfbml: false, cookie: false })
        return FB
      })
      .catch(err => {
        readyPromise = null  // allow retry after config is saved
        throw err
      })
    return readyPromise
  }

  function login() {
    return ready().then(FB => new Promise((resolve, reject) => {
      FB.login(response => {
        if (response.status === 'connected' && response.authResponse?.accessToken) {
          resolve(response.authResponse)
        } else {
          reject(new Error('Login con Facebook cancelado.'))
        }
      }, { scope: SCOPE, return_scopes: true })
    }))
  }

  function logout() {
    return ready().then(FB => new Promise(resolve => {
      FB.getLoginStatus(res => {
        if (res.status === 'connected') FB.logout(() => resolve())
        else resolve()
      })
    }))
  }

  return { ready, login, logout }
}
