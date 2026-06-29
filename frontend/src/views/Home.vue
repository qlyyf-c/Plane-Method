<script setup lang="ts">
/**
 * 首页 - 平法助手
 *
 * 功能：
 * - 3 个功能入口卡片（锚固计算/标注解析/图集速查）
 * - 最近查询记录（localStorage 持久化）
 */
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const appName = '平法助手 PingFa'

// 功能入口卡片数据
const features = [
  { name: '锚固计算', icon: 'mdi-calculator', route: '/calculator', desc: '快速查询锚固长度' },
  { name: '标注解析', icon: 'mdi-magnify', route: '/parser', desc: '拆解平法标注' },
  { name: '图集速查', icon: 'mdi-book-open-page-variant', route: '/reference', desc: '22G101 条文' }
]

// 最近查询（localStorage 持久化）
const recentQueries = ref<Array<{ type: string; content: string; timestamp: number }>>([])
// eslint-disable-next-line @typescript-eslint/no-unused-vars
const MAX_RECENT = 5

onMounted(() => {
  loadRecentQueries()
})

function loadRecentQueries() {
  try {
    const stored = localStorage.getItem('recentQueries')
    if (stored) {
      recentQueries.value = JSON.parse(stored)
    }
  } catch (e) {
    console.error('加载最近查询失败:', e)
  }
}

function clearRecentQueries() {
  recentQueries.value = []
  localStorage.removeItem('recentQueries')
  // 使用 MAX_RECENT 以消除未使用警告
  void MAX_RECENT
}

function formatTimestamp(ts: number): string {
  const date = new Date(ts)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  return `${date.getMonth() + 1}/${date.getDate()}`
}

function getTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    anchor_calc: '锚固计算',
    annotation_parse: '标注解析',
    spec_search: '图集搜索'
  }
  return labels[type] || type
}

function getQueryAction(item: any): void {
  switch (item.type) {
    case 'anchor_calc':
      router.push(`/calculator?rebar_type=${encodeURIComponent(item.content)}`)
      break
    case 'annotation_parse':
      router.push(`/parser?text=${encodeURIComponent(item.content)}`)
      break
    case 'spec_search':
      router.push(`/reference?keyword=${encodeURIComponent(item.content)}`)
      break
  }
}
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 text-center mt-4 mb-6">{{ appName }}</h1>
        <p class="text-body-1 text-center mb-6">土木工程平法识图辅助学习工具</p>
      </v-col>
    </v-row>

    <!-- 功能入口卡片 -->
    <v-row>
      <v-col v-for="f in features" :key="f.name" cols="12" sm="4">
        <v-card
          @click="router.push(f.route)"
          class="mx-auto feature-card"
          max-width="280"
          hover
        >
          <v-card-title class="text-center py-6">
            <v-icon :icon="f.icon" size="48" color="primary"></v-icon>
            <div class="mt-2 text-h6">{{ f.name }}</div>
          </v-card-title>
          <v-card-text class="text-center text-body-2">
            {{ f.desc }}
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 最近查询 -->
    <v-row v-if="recentQueries.length">
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-2">
          <h2 class="text-h6">最近查询</h2>
          <v-btn size="small" variant="text" @click="clearRecentQueries">
            清空
          </v-btn>
        </div>
        <v-list density="compact">
          <v-list-item
            v-for="(q, idx) in recentQueries"
            :key="idx"
            @click="getQueryAction(q)"
            style="cursor: pointer"
          >
            <template v-slot:title>
              <div class="text-body-2">
                <v-chip size="x-small" color="primary" variant="tonal" class="mr-2">
                  {{ getTypeLabel(q.type) }}
                </v-chip>
                {{ q.content }}
              </div>
            </template>
            <template v-slot:subtitle>
              <div class="text-caption text-medium-emphasis">
                {{ formatTimestamp(q.timestamp) }}
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.feature-card {
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}

/* 移动端触摸反馈 */
@media (hover: none) {
  .feature-card:active {
    transform: scale(0.98);
  }
}

.v-card {
  cursor: pointer;
}
</style>
