<script setup lang="ts">
/**
 * 图集速查页面 - Week 4 实现 (Week 7 优化)
 *
 * 功能:
 * - 搜索条文 (关键字)
 * - 分类浏览 (柱/梁/墙/一般构造)
 * - 条文详情查看 (HTML 渲染)
 * - 关联跳转 (计算/标注类型)
 *
 * Week 7 优化:
 * - 使用 Pinia Store 缓存数据
 * - 避免重复 API 调用
 */
import { ref, onMounted } from 'vue'
import { useSpecificationStore } from '../stores/specifications'
import { useRoute } from 'vue-router'

const route = useRoute()
const specStore = useSpecificationStore()

// ===== 常量 =====
const pageTitle = '22G101 图集速查'

// 分类名称映射（英文 → 中文）
const categoryNames: Record<string, string> = {
  beam: '梁',
  column: '柱',
  general: '一般构造',
  wall: '墙'
}

// ===== 搜索与分类 =====
const searchKeyword = ref('')
const selectedCategory = ref<string>('')
const showDetailDialog = ref(false)
const selectedSpec = ref<any>(null)
const relatedContent = ref<any>(null)

// ===== 生命周期 =====
onMounted(async () => {
  const error = await specStore.loadCategories()
  if (error) {
    // 直接使用 v-if 显示错误
    specStore.loadError = error
    return
  }

  // 读取路由参数进行搜索
  if (route.query.keyword) {
    searchKeyword.value = route.query.keyword as string
    await searchSpecifications()
  } else if (route.query.category) {
    await getByCategory(route.query.category as string)
  }
})

// ===== 方法 =====
async function loadCategories(): Promise<string | null> {
  return specStore.loadCategories()
}

async function searchSpecifications() {
  if (!searchKeyword.value.trim()) {
    // 空关键字时，按当前分类查询
    if (selectedCategory.value) {
      await getByCategory(selectedCategory.value)
    }
    return
  }

  await specStore.searchSpecifications(searchKeyword.value)
}

async function getByCategory(category: string) {
  selectedCategory.value = category
  searchKeyword.value = '' // 清空搜索框

  await specStore.getByCategory(category)
}

async function viewDetail(specId: string) {
  try {
    // 获取条文详情
    const detail = await specStore.getDetail(specId)
    if (!detail) {
      specStore.loadError = '加载条文详情失败'
      return
    }

    selectedSpec.value = detail
    showDetailDialog.value = true
  } catch (e: any) {
    specStore.loadError = '加载条文详情失败'
    console.error(e)
  }
}

function closeDetail() {
  showDetailDialog.value = false
  selectedSpec.value = null
  relatedContent.value = null
}

// 预留方法 (后续扩展关联跳转功能)
// function navigateToRelated(type: string, value: string) { ... }

function clearError() {
  specStore.clearCache()
  specStore.loadError = null
}
</script>

<template>
  <v-container>
    <!-- 标题 -->
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mt-4 mb-4">{{ pageTitle }}</h1>
      </v-col>
    </v-row>

    <!-- 错误提示 -->
    <v-row v-if="specStore.loadError">
      <v-col cols="12">
        <v-alert type="error" variant="tonal" closable @click:close="clearError" class="mb-4">
          <div class="text-body-1">{{ specStore.loadError }}</div>
          <v-btn size="small" variant="outlined" class="mt-2" @click="loadCategories()">
            重试
          </v-btn>
        </v-alert>
      </v-col>
    </v-row>

    <!-- 搜索框（手机端堆叠） -->
    <v-row>
      <v-col cols="12">
        <v-text-field
          v-model="searchKeyword"
          label="搜索条文"
          prepend-inner-icon="mdi-magnify"
          outlined
          clearable
          @keyup.enter="searchSpecifications"
          @click:clear="searchSpecifications"
        ></v-text-field>
      </v-col>
      <v-col cols="12">
        <v-btn color="primary" @click="searchSpecifications" block class="mb-3">
          搜索
        </v-btn>
      </v-col>
    </v-row>

    <!-- 分类标签 -->
    <v-row>
      <v-col cols="12">
        <div class="text-subtitle-2 mb-2">分类浏览:</div>
        <v-chip-group
          v-model="selectedCategory"
          @update:model-value="getByCategory($event)"
        >
          <v-chip
            v-for="cat in specStore.categories"
            :key="cat"
            :value="cat"
            filter
            variant="outlined"
          >
            {{ categoryNames[cat] || cat }}
          </v-chip>
        </v-chip-group>
      </v-col>
    </v-row>

    <!-- 加载状态 -->
    <v-row v-if="specStore.isLoading">
      <v-col cols="12" class="text-center py-8">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </v-col>
    </v-row>

    <!-- 条文列表 -->
    <v-row v-if="!specStore.isLoading && !specStore.loadError && specStore.specifications.length > 0">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            {{ searchKeyword ? '搜索结果' : (selectedCategory ? categoryNames[selectedCategory] + '条文' : '条文列表') }}
            <span class="text-caption text-medium-emphasis">({{ specStore.specifications.length }}条)</span>
          </v-card-title>
          <v-divider></v-divider>
          <v-list>
            <v-list-item
              v-for="spec in specStore.specifications"
              :key="spec.id"
              @click="viewDetail(spec.id)"
              style="cursor: pointer"
            >
              <template v-slot:title>
                <div class="text-body-1 font-weight-bold">
                  {{ spec.clause_number }} - {{ spec.title }}
                </div>
              </template>
              <template v-slot:subtitle>
                <div class="text-caption text-medium-emphasis">
                  {{ spec.snippet || spec.category }}
                </div>
              </template>
              <template v-slot:append>
                <v-icon>mdi-chevron-right</v-icon>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>

    <!-- 空状态提示 -->
    <v-row v-if="!specStore.isLoading && !specStore.loadError && specStore.specifications.length === 0">
      <v-col cols="12" class="text-center py-8">
        <div class="text-body-1 text-medium-emphasis">
          {{ searchKeyword ? '未找到匹配的条文' : '请选择分类或输入关键字搜索' }}
        </div>
      </v-col>
    </v-row>

    <!-- 条文详情对话框 -->
    <v-dialog v-model="showDetailDialog" max-width="800px" scrollable>
      <v-card v-if="selectedSpec">
        <v-card-title>
          <div class="text-h5">{{ selectedSpec.title }}</div>
          <div class="text-caption text-medium-emphasis">
            {{ selectedSpec.clause_number }} · {{ selectedSpec.category }}
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="py-4">
          <!-- HTML 内容渲染 -->
          <div v-html="selectedSpec.content_html" class="spec-content"></div>

          <!-- 关联内容占位 (后续扩展) -->
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="closeDetail" variant="outlined">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
/* 条文 HTML 内容的简单样式 */
.spec-content h3 {
  font-size: 1.25rem;
  font-weight: bold;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  color: #1976d2;
}

.spec-content p {
  margin-bottom: 0.75rem;
  line-height: 1.6;
}

.spec-content ul, .spec-content ol {
  margin-left: 1.5rem;
  margin-bottom: 0.75rem;
}

.spec-content table {
  border-collapse: collapse;
  width: 100%;
  margin: 1rem 0;
}

.spec-content th, .spec-content td {
  border: 1px solid #ddd;
  padding: 0.5rem;
  text-align: left;
}

.spec-content th {
  background-color: #f5f5f5;
  font-weight: bold;
}
</style>
