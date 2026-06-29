/**
 * Vue Router 配置 - 平法助手
 *
 * 5个路由：Home / Calculator / Parser / Reference / About
 * 使用 hash 模式以兼容 PWA 静态部署
 */
import { createRouter, createWebHashHistory } from 'vue-router'

// 路由定义
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页', icon: 'mdi-home' }
  },
  {
    path: '/calculator',
    name: 'Calculator',
    component: () => import('../views/Calculator.vue'),
    meta: { title: '计算', icon: 'mdi-calculator' }
  },
  {
    path: '/parser',
    name: 'Parser',
    component: () => import('../views/Parser.vue'),
    meta: { title: '解析', icon: 'mdi-magnify' }
  },
  {
    path: '/reference',
    name: 'Reference',
    component: () => import('../views/Reference.vue'),
    meta: { title: '查阅', icon: 'mdi-book-open-page-variant' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { title: '关于', icon: 'mdi-information' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router