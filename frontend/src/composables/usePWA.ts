import { ref, onMounted } from 'vue'

// PWA 注册类型声明
declare module 'virtual:pwa-register' {
  export function registerSW(options: {
    immediate?: boolean
    onRegistered?: (registration: ServiceWorkerRegistration | undefined) => void
    onRegisterError?: (error: Error) => void
    onNeedRefresh?: () => void
    onOfflineReady?: () => void
  }): () => Promise<void>
}

export function usePWA() {
  const needRefresh = ref(false)
  const offlineReady = ref(false)

  let updateServiceWorker: (() => Promise<void>) | undefined

  onMounted(async () => {
    // 只在生产环境或支持 PWA 的环境下执行
    if (import.meta.env.PROD && 'serviceWorker' in navigator) {
      try {
        const { registerSW } = await import('virtual:pwa-register')

        updateServiceWorker = registerSW({
          immediate: true,
          onRegistered(r: ServiceWorkerRegistration | undefined) {
            console.log('SW Registered:', r)
          },
          onRegisterError(error: Error) {
            console.log('SW Registration Error:', error)
          },
          onNeedRefresh() {
            needRefresh.value = true
          },
          onOfflineReady() {
            offlineReady.value = true
          }
        })
      } catch (error) {
        console.log('PWA registration skipped:', error)
      }
    }
  })

  const close = () => {
    needRefresh.value = false
    offlineReady.value = false
  }

  const updateApp = async () => {
    if (updateServiceWorker) {
      await updateServiceWorker()
    }
    close()
  }

  return {
    needRefresh,
    offlineReady,
    close,
    updateApp
  }
}
