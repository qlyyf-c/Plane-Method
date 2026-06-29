/**
 * Pinia Store - 图集条文缓存
 *
 * 功能:
 * - 缓存条文分类列表
 * - 缓存条文搜索结果
 * - 避免重复 API 调用，提升加载速度
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index'

// ===== 类型定义 =====
export interface Specification {
  id: string
  clause_number: string
  title: string
  category: string
  content_html?: string
  snippet?: string
}

interface CategoryCache {
  categories: string[]
  specsByCategory: Record<string, Specification[]>
  lastUpdated: number
}

// 缓存有效期：10 分钟
const CACHE_DURATION = 10 * 60 * 1000

// ===== Store =====
export const useSpecificationStore = defineStore('specifications', () => {
  // State
  const categories = ref<string[]>([])
  const specifications = ref<Specification[]>([])
  const isLoading = ref(false)
  const _loadError = ref<string | null>(null)
  const cache = ref<CategoryCache>({
    categories: [],
    specsByCategory: {},
    lastUpdated: 0
  })

  // Getters
  const isCacheValid = computed(() => {
    if (!cache.value.lastUpdated) return false
    return Date.now() - cache.value.lastUpdated < CACHE_DURATION
  })

  const loadError = computed({
    get: () => _loadError.value,
    set: (val) => { _loadError.value = val }
  })

  // Actions
  async function loadCategories(): Promise<string | null> {
    if (isCacheValid.value && cache.value.categories.length > 0) {
      categories.value = cache.value.categories
      return null
    }

    try {
      const response = await api.get<{ categories: string[] }>('/specification/categories')
      const cats = response.data.categories || []

      categories.value = cats
      cache.value = {
        categories: cats,
        specsByCategory: {},
        lastUpdated: Date.now()
      }

      return null
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || '加载分类失败'
      console.error('加载分类失败:', e)
      return errorMsg
    }
  }

  async function searchSpecifications(keyword: string): Promise<{ results: Specification[]; error: string | null }> {
    isLoading.value = true
    _loadError.value = null

    try {
      const response = await api.get<{ results: Specification[] }>('/specification/search', {
        params: { keyword }
      })

      specifications.value = response.data.results || []
      return { results: specifications.value, error: null }
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || '搜索失败'
      console.error('搜索失败:', e)
      return { results: [], error: errorMsg }
    } finally {
      isLoading.value = false
    }
  }

  async function getByCategory(category: string): Promise<{ specs: Specification[]; error: string | null }> {
    isLoading.value = true
    _loadError.value = null

    // 检查缓存
    if (isCacheValid.value && cache.value.specsByCategory[category]) {
      specifications.value = cache.value.specsByCategory[category]
      isLoading.value = false
      return { specs: specifications.value, error: null }
    }

    try {
      const response = await api.get<{ specifications: Specification[] }>('/specification/by-category', {
        params: { category }
      })

      const specs = response.data.specifications || []
      specifications.value = specs

      // 更新缓存
      cache.value.specsByCategory[category] = specs
      cache.value.lastUpdated = Date.now()

      return { specs, error: null }
    } catch (e: any) {
      const errorMsg = e.response?.data?.detail || '加载条文失败'
      console.error('加载条文失败:', e)
      return { specs: [], error: errorMsg }
    } finally {
      isLoading.value = false
    }
  }

  async function getDetail(specId: string): Promise<Specification | null> {
    try {
      const response = await api.get<Specification>(`/specification/detail/${specId}`)
      return response.data
    } catch (e) {
      console.error('加载条文详情失败:', e)
      return null
    }
  }

  function clearCache() {
    cache.value = {
      categories: [],
      specsByCategory: {},
      lastUpdated: 0
    }
    specifications.value = []
    _loadError.value = null
  }

  return {
    // State
    categories,
    specifications,
    isLoading,
    loadError,
    // Getters
    isCacheValid,
    // Actions
    loadCategories,
    searchSpecifications,
    getByCategory,
    getDetail,
    clearCache
  }
})
