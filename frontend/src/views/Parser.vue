<script setup lang="ts">
/**
 * 标注解析器页面 - Week 4 实现
 *
 * 功能：
 * - 输入平法标注字符串（如 KL7(3) 300×650）
 * - 调用后端 API 解析
 * - 显示解析结果（构件类型、编号、跨数、截面）
 * - 显示符号释义
 * - 错误提示与建议
 */
import { ref } from 'vue'
import api from '../api/index'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// ===== 表单数据 =====
const inputText = ref('')
const pageTitle = '平法标注解析器'

// ===== 解析结果 =====
interface ParsedResult {
  component_type: string
  component_name: string
  number: number
  span_count?: string
  width?: number
  height?: number
}

interface GlossaryItem {
  symbol: string
  meaning: string
  description: string
}

const result = ref<ParsedResult | null>(null)
const glossary = ref<GlossaryItem[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const suggestion = ref<string | null>(null)

// ===== 示例列表 =====
const examples = ref<string[]>([])

// ===== 生命周期 =====
import { onMounted } from 'vue'
onMounted(async () => {
  await loadExamples()

  // 读取路由参数预填输入框
  if (route.query.text) {
    inputText.value = route.query.text as string
  }
})

// ===== 方法 =====
async function loadExamples() {
  try {
    const response = await api.get('/annotation/examples')
    examples.value = response.data.examples || []
  } catch (e) {
    console.error('加载示例失败:', e)
  }
}

function useExample(example: string) {
  inputText.value = example
  result.value = null
  error.value = null
}

async function parseAnnotation() {
  loading.value = true
  error.value = null
  result.value = null
  glossary.value = []

  try {
    const response = await api.post('/annotation/parse', {
      text: inputText.value,
    })
    const res = response.data

    if (res.success && res.parsed) {
      result.value = res.parsed
      glossary.value = res.glossary || []
      // 保存到最近查询
      saveToRecent(inputText.value)
    } else {
      error.value = res.error || '解析失败'
      suggestion.value = res.suggestion || null
    }
  } catch (e: any) {
    error.value = e.response?.data?.detail || '解析失败，请重试'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function saveToRecent(content: string) {
  try {
    let recent = JSON.parse(localStorage.getItem('recentQueries') || '[]')
    recent = recent.filter((q: any) => !(q.type === 'annotation_parse' && q.content === content))
    recent.unshift({ type: 'annotation_parse', content, timestamp: Date.now() })
    if (recent.length > 5) recent.pop()
    localStorage.setItem('recentQueries', JSON.stringify(recent))
  } catch (e) {
    console.error('保存最近查询失败:', e)
  }
}

function viewRelatedSpec() {
  if (result.value?.component_type?.includes('梁')) {
    router.push('/reference?keyword=梁平法')
  } else if (result.value?.component_type?.includes('柱')) {
    router.push('/reference?keyword=柱平法')
  } else {
    router.push('/reference?keyword=平法')
  }
}

function calculateAnchor() {
  // 如果有钢筋类型信息，传递过去
  router.push('/calculator')
}

function reset() {
  inputText.value = ''
  result.value = null
  error.value = null
  glossary.value = []
  suggestion.value = null
}
</script>

<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mt-4 mb-4">{{ pageTitle }}</h1>
      </v-col>
    </v-row>

    <!-- 输入框 -->
    <v-row>
      <v-col cols="12">
        <v-textarea
          v-model="inputText"
          label="输入平法标注"
          placeholder="例如：KL7(3) 300×650、L2、WKL6(5)、KL4（5）等"
          outlined
          clearable
          rows="3"
          auto-grow
          @keyup.enter="parseAnnotation"
          counter="50"
        >
          <template v-slot:hint>
            <div class="text-caption text-medium-emphasis mt-2">
              <v-icon size="small" color="warning">mdi-information</v-icon>
              请按示例规范填写，支持中英文括号混用
            </div>
          </template>
        </v-textarea>
      </v-col>
    </v-row>

    <!-- 示例快捷按钮 -->
    <v-row>
      <v-col cols="12">
        <div class="text-subtitle-2 mb-2">点击示例快速尝试：</div>
        <v-chip-group>
          <v-chip
            v-for="ex in examples"
            :key="ex"
            color="primary"
            variant="tonal"
            size="small"
            @click="useExample(ex)"
          >
            {{ ex }}
          </v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <!-- 解析按钮 -->
    <v-row>
      <v-col cols="12" sm="6">
        <v-btn color="primary" @click="parseAnnotation" :loading="loading" block>
          解析
        </v-btn>
      </v-col>
      <v-col cols="12" sm="6">
        <v-btn @click="reset" variant="outlined" block>
          重置
        </v-btn>
      </v-col>
    </v-row>

    <!-- 错误提示 -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      <div class="text-body-1">{{ error }}</div>
      <div v-if="suggestion" class="text-caption mt-2">{{ suggestion }}</div>
    </v-alert>

    <!-- 解析结果 -->
    <v-card v-if="result" class="mb-4">
      <v-card-title>
        <span>解析结果</span>
        <v-spacer></v-spacer>
        <v-btn size="small" variant="tonal" color="primary" @click="viewRelatedSpec" class="mr-2">
          <v-icon start>mdi-book-open-page-variant</v-icon>
          查看条文
        </v-btn>
        <v-btn size="small" variant="tonal" color="success" @click="calculateAnchor">
          <v-icon start>mdi-calculator</v-icon>
          计算锚固
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6">
            <div class="text-body-2 text-medium-emphasis">构件类型</div>
            <div class="text-h5">{{ result.component_type }} - {{ result.component_name }}</div>
          </v-col>
          <v-col cols="12" sm="6">
            <div class="text-body-2 text-medium-emphasis">编号</div>
            <div class="text-h5">{{ result.number }}号</div>
          </v-col>
          <v-col cols="12" sm="6" v-if="result.span_count">
            <div class="text-body-2 text-medium-emphasis">跨数</div>
            <div class="text-h5">{{ result.span_count }}跨</div>
          </v-col>
          <v-col cols="12" sm="6" v-if="result.width && result.height">
            <div class="text-body-2 text-medium-emphasis">截面尺寸</div>
            <div class="text-h5">{{ result.width }}×{{ result.height }} mm</div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 符号释义 -->
    <v-card v-if="glossary.length > 0" class="mb-4">
      <v-card-title>符号释义</v-card-title>
      <v-card-text>
        <v-list density="compact">
          <v-list-item
            v-for="item in glossary"
            :key="item.symbol"
            :title="item.symbol"
            :subtitle="item.meaning"
          >
            <template v-slot:append>
              <div class="text-caption text-medium-emphasis" style="max-width: 200px; white-space: normal;">
                {{ item.description }}
              </div>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
    </v-card>
  </v-container>
</template>
