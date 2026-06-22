/**
 * TikTok OAuth 2.0 — popup flow.
 *
 * Flow:
 *   1. open popup → /api/integrations/tiktok/init/
 *   2. Backend stores state in session, redirects to TikTok
 *   3. TikTok redirects back to /api/integrations/tiktok/callback/
 *   4. Backend stores token, redirects popup to /oauth/done?platform=tiktok&success=1
 *   5. /oauth/done Vue page sends postMessage to opener and closes
 *
 *   const { login } = useTikTokAuth()
 *   await login()
 */

const POPUP_OPTIONS = 'width=600,height=700,left=200,top=100,scrollbars=yes,resizable=yes'
const BACKEND_BASE = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'

export function useTikTokAuth() {
  function login() {
    return new Promise((resolve, reject) => {
      const initUrl = `${BACKEND_BASE}/api/integrations/tiktok/init/`
      const popup = window.open(initUrl, 'tiktok_oauth', POPUP_OPTIONS)

      if (!popup) {
        reject(new Error('El navegador bloqueó la ventana emergente. Permite los popups para este sitio.'))
        return
      }

      function handleMessage(event) {
        if (event.data?.type !== 'oauth_callback' || event.data?.platform !== 'tiktok') return
        cleanup()
        if (event.data.success) {
          resolve({ platform: 'tiktok' })
        } else {
          reject(new Error(event.data.error || 'Autenticación con TikTok cancelada.'))
        }
      }

      const checkClosed = setInterval(() => {
        if (popup.closed) {
          cleanup()
          reject(new Error('Ventana de TikTok cerrada sin completar la autenticación.'))
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
