/**
 * Vue3 入口 - 平法助手
 *
 * 引入：
 * - Vuetify 3（Material Design UI）
 * - Vue Router（hash 模式）
 * - Pinia（状态管理）
 */
import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import '@mdi/font/css/materialdesignicons.css'

// Router
import router from './router'

// App
import App from './App.vue'

// 主题色：土木工程蓝 #1976d2
const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976d2',
          secondary: '#424242',
          accent: '#82b1ff',
          error: '#ff5252',
          info: '#2196f3',
          success: '#4caf50',
          warning: '#ffc107'
        }
      }
    }
  }
})

const pinia = createPinia()

const app = createApp(App)
app.use(vuetify)
app.use(pinia)
app.use(router)
app.mount('#app')