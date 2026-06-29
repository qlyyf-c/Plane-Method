<script setup lang="ts">
/**
 * App.vue - 平法助手主框架
 *
 * 结构：
 * - Router View（页面内容）
 * - 底部导航栏（5个 tab）
 * - PWA 更新提示
 */
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PWAPrompt from './components/PWAPrompt.vue'

const route = useRoute()
const router = useRouter()

// 当前路由信息
const currentRoute = computed(() => route.name as string)

// 导航项
const navItems = [
  { name: 'Home', title: '首页', icon: 'mdi-home', path: '/' },
  { name: 'Calculator', title: '计算', icon: 'mdi-calculator', path: '/calculator' },
  { name: 'Parser', title: '解析', icon: 'mdi-magnify', path: '/parser' },
  { name: 'Reference', title: '查阅', icon: 'mdi-book-open-page-variant', path: '/reference' },
  { name: 'About', title: '关于', icon: 'mdi-information', path: '/about' }
]

// 导航跳转
const navigate = (path: string) => {
  router.push(path)
}
</script>

<template>
  <v-app>
    <!-- 主内容区域 -->
    <v-main>
      <router-view />
    </v-main>

    <!-- 底部导航栏（手机端优化） -->
    <v-bottom-navigation v-model="currentRoute" app color="primary" grow class="mobile-nav">
      <v-btn v-for="item in navItems" :key="item.name" :value="item.name" @click="navigate(item.path)">
        <v-icon size="20">{{ item.icon }}</v-icon>
        <span style="font-size: 11px">{{ item.title }}</span>
      </v-btn>
    </v-bottom-navigation>

    <!-- PWA 更新提示 -->
    <PWAPrompt />
  </v-app>
</template>

<style>
/* 全局样式 */
body {
  font-family: 'Roboto', sans-serif;
  margin: 0;
  padding: 0;
}

/* 移动端导航栏优化 */
.v-bottom-navigation.mobile-nav {
  padding: 0 !important;
}

.v-bottom-navigation.mobile-nav .v-btn {
  min-height: 56px !important;
  padding: 8px 4px !important;
  font-size: 11px !important;
}

/* 主内容区域留底部导航空间 */
v-main {
  padding-bottom: 72px !important;
}

/* 卡片悬停效果（桌面端） */
@media (hover: hover) {
  .v-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
  }
}

/* 过渡动画 */
.v-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

/* 错误边界样式 */
.v-alert[type="error"] {
  border-left: 4px solid #f44336 !important;
}

/* 加载状态优化 */
.v-progress-circular {
  color: var(--v-primary-base) !important;
}

/* 输入框移动端优化 */
.v-field--variant-outlined input {
  font-size: 16px !important; /* 防止 iOS 自动缩放 */
}

/* 按钮触摸区域优化 */
.v-btn {
  min-width: 64px !important;
  min-height: 36px !important;
}
</style>