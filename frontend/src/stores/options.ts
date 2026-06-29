/**
 * Pinia Store - 选项数据缓存
 *
 * 功能:
 * - 缓存锚固计算选项 (混凝土/钢筋/抗震等级/修正系数)
 * - 避免重复 API 调用，提升加载速度
 * - 提供加载状态和错误处理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../api/index'

// ===== 类型定义 =====
export interface ConcreteOption { grade: string; ft_value: number }
export interface RebarOption { type: string; fy_value: number; alpha: number }
export interface SeismicOption { grade: string; factor: number; note: string }
export interface ModifierOption { modifier_id: string; name: string; condition: string; factor: number; note: string }

export interface AnchorOptions {
  concrete_grades: ConcreteOption[]
  rebar_types: RebarOption[]
  seismic_grades: SeismicOption[]
  modifiers: ModifierOption[]
}

// ===== Store =====
export const useOptionsStore = defineStore('options', () => {
  // State
  const concreteGrades = ref<ConcreteOption[]>([])
  const rebarTypes = ref<RebarOption[]>([])
  const seismicGrades = ref<SeismicOption[]>([])
  const modifiers = ref<ModifierOption[]>([])
  const isLoading = ref(false)
  const _loadError = ref<string | null>(null)
  const lastUpdated = ref<number | null>(null)

  // Getters
  const allLoaded = computed(() => {
    return concreteGrades.value.length > 0 && rebarTypes.value.length > 0 &&
           seismicGrades.value.length > 0 && modifiers.value.length > 0
  })

  const hasExpired = computed(() => {
    if (!lastUpdated.value) return true
    // 缓存有效期：30 分钟
    return Date.now() - lastUpdated.value > 30 * 60 * 1000
  })

  const loadError = computed({
    get: () => _loadError.value,
    set: (val) => { _loadError.value = val }
  })

  // Actions
  async function loadOptions(): Promise<boolean> {
    if (allLoaded.value && !hasExpired.value) {
      return true // 使用缓存
    }

    isLoading.value = true
    _loadError.value = null

    try {
      const response = await api.get<AnchorOptions>('/anchor/options')
      const data = response.data

      concreteGrades.value = data.concrete_grades
      rebarTypes.value = data.rebar_types
      seismicGrades.value = data.seismic_grades
      modifiers.value = data.modifiers
      lastUpdated.value = Date.now()

      return true
    } catch (e: any) {
      _loadError.value = e.response?.data?.detail || '加载选项数据失败'
      console.error('加载选项失败:', e)
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearCache() {
    concreteGrades.value = []
    rebarTypes.value = []
    seismicGrades.value = []
    modifiers.value = []
    lastUpdated.value = null
    _loadError.value = null
  }

  return {
    // State
    concreteGrades,
    rebarTypes,
    seismicGrades,
    modifiers,
    isLoading,
    loadError,
    // Getters
    allLoaded,
    hasExpired,
    // Actions
    loadOptions,
    clearCache
  }
})
