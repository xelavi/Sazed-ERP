/**
 * X (Twitter) OAuth 2.0 PKCE — popup flow.
 *
 * Flow:
 *   1. open popup → /api/integrations/twitter/init/
 *   2. Backend generates PKCE, stores in session, redirects to Twitter
 *   3. Twitter redirects back to /api/integrations/twitter/callback/
 *   4. Backend stores token, redirects popup to /oauth/done?platform=twitter&success=1
 *   5. /oauth/done Vue page sends postMessage to opener and closes
 *
 *   const { login } = useXAuth()
 *   await login()   // resolves when popup completes and token is stored
 */

const POPUP_OPTIONS = 'width=600,height=700,left=200,top=100,scrollbars=yes,resizable=yes'
const BACKEND_BASE = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'

export function useXAuth() {
  function login() {
    return new Promise((resolve, reject) => {
      const initUrl = `${BACKEND_BASE}/api/integrations/twitter/init/`
      const popup = window.open(initUrl, 'x_oauth', POPUP_OPTIONS)

      if (!popup) {
        reject(new Error('El navegador bloqueó la ventana emergente. Permite los popups para este sitio.'))
        return
      }

      function handleMessage(event) {
        if (event.data?.type !== 'oauth_callback' || event.data?.platform !== 'twitter') return
        cleanup()
        if (event.data.success) {
          resolve({ platform: 'twitter' })
        } else {
          reject(new Error(event.data.error || 'Autenticación con X cancelada.'))
        }
      }

      const checkClosed = setInterval(() => {
        if (popup.closed) {
          cleanup()
          reject(new Error('Ventana de X cerrada sin completar la autenticación.'))
        }
      }, 500)

      function cleanup() {
        clearInterval(checkClosed)
        window.removeEventListener('message', handleMessage)
      }

      window.addEventListener('message', handleMessage)
    })
  }

  return { login }
}
