<script setup lang="ts">
/**
 * 锚固计算器页面 - Week 3 实现
 * 
 * 功能：
 * - 选择混凝土等级、钢筋类型、直径、抗震等级
 * - 勾选修正系数（可选）
 * - 调用后端 API 计算锚固长度
 * - 显示 lab, la, laE 结果
 */
import { ref, onMounted, computed } from 'vue'
import api from '../api/index'
import { useRouter } from 'vue-router'
import { useOptionsStore } from '../stores/options'

const router = useRouter()
const optionsStore = useOptionsStore()

// ===== 表单数据 =====
const concreteGrade = ref<string>('')
const rebarType = ref<string>('')
const diameter = ref<number>(25)
const seismicGrade = ref<string>('非抗震')
const selectedModifiers = ref<string[]>([])

// ===== 选项数据 (从 Store 读取) =====
const concreteOptions = computed(() => optionsStore.concreteGrades)
const rebarOptions = computed(() => optionsStore.rebarTypes)
const seismicOptions = computed(() => optionsStore.seismicGrades)
const modifiersOptions = computed(() => optionsStore.modifiers)

// ===== 计算结果 =====
interface CalculationResult {
  lab_d: number
  lab_mm: number
  la_d: number
  la_mm: number
  laE_d: number
  laE_mm: number
  seismic_factor: number
  modifiers_applied: string[]
}

const result = ref<CalculationResult | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
// 不再需要 loadError，统一使用 optionsStore.loadError

// 路由参数（用于预填表单）
import { useRoute } from 'vue-router'
const route = useRoute()

// ===== 生命周期 =====
onMounted(async () => {
  const loadSuccess = await optionsStore.loadOptions()

  // 检查选项是否加载成功
  if (!loadSuccess) {
    error.value = optionsStore.loadError
  }

  // 设置默认值
  concreteGrade.value = 'C30'
  rebarType.value = 'HRB400'
  diameter.value = 25
  seismicGrade.value = '非抗震'

  // 读取路由参数进行预填
  if (route.query.rebar_type) {
    rebarType.value = route.query.rebar_type as string
  }
  if (route.query.concrete_grade) {
    concreteGrade.value = route.query.concrete_grade as string
  }
  if (route.query.diameter) {
    diameter.value = Number(route.query.diameter)
  }
  if (route.query.seismic_grade) {
    seismicGrade.value = route.query.seismic_grade as string
  }
})

// 不再需要直接调用 API

async function calculate() {
  loading.value = true
  error.value = null
  result.value = null

  try {
    const response = await api.post('/anchor/calculate', {
      concrete_grade: concreteGrade.value,
      rebar_type: rebarType.value,
      diameter: diameter.value,
      seismic_grade: seismicGrade.value,
      modifier_ids: selectedModifiers.value.length > 0 ? selectedModifiers.value : undefined,
    })
    const res = response.data

    result.value = {
      lab_d: res.lab.d_value,
      lab_mm: res.lab.mm_value,
      la_d: res.la.d_value,
      la_mm: res.la.mm_value,
      laE_d: res.laE.d_value,
      laE_mm: res.laE.mm_value,
      seismic_factor: res.laE.seismic_modifier,
      modifiers_applied: res.la.modifier_note !== '无修正'
        ? [res.la.modifier_note]
        : [],
    }

    // 保存到最近查询
    saveToRecent()
  } catch (e: any) {
    error.value = e.response?.data?.detail || '计算失败，请重试'
    console.error(e)
  } finally {
    loading.value = false
  }
}

function saveToRecent() {
  try {
    const query = `${concreteGrade.value}/${rebarType.value}/${diameter.value}mm/${seismicGrade.value}`
    let recent = JSON.parse(localStorage.getItem('recentQueries') || '[]')
    recent = recent.filter((q: any) => !(q.type === 'anchor_calc' && q.content === query))
    recent.unshift({ type: 'anchor_calc', content: query, timestamp: Date.now() })
    if (recent.length > 5) recent.pop()
    localStorage.setItem('recentQueries', JSON.stringify(recent))
  } catch (e) {
    console.error('保存最近查询失败:', e)
  }
}

function viewRelatedSpec() {
  router.push('/reference?keyword=锚固长度')
}

function reset() {
  result.value = null
  error.value = null
  selectedModifiers.value = []
}
</script>

<template>
  <v-container>
    <!-- 加载失败提示 (使用 Store 的错误) -->
    <v-alert v-if="optionsStore.loadError" type="error" variant="tonal" class="mb-4" closable @close="optionsStore.clearCache()">
      <div class="text-body-1">{{ optionsStore.loadError }}</div>
      <v-btn size="small" variant="outlined" class="mt-2" @click="optionsStore.loadOptions()">
        重试
      </v-btn>
    </v-alert>

    <h1 class="text-h4 mb-4">锚固长度计算器</h1>

    <!-- 输入表单 -->
    <v-card class="mb-4">
      <v-card-title>输入参数</v-card-title>
      <v-card-text>
        <v-form @submit.prevent="calculate">
          <v-row>
            <!-- 混凝土等级 -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="concreteGrade"
                :items="concreteOptions"
                item-title="grade"
                label="混凝土等级"
                required
              />
            </v-col>

            <!-- 钢筋类型 -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="rebarType"
                :items="rebarOptions"
                item-title="type"
                label="钢筋类型"
                required
              />
            </v-col>

            <!-- 钢筋直径 -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="diameter"
                :items="[6,8,10,12,14,16,18,20,22,25,28,32,36,40,50]"
                label="钢筋直径 (mm)"
                required
              />
            </v-col>

            <!-- 抗震等级 -->
            <v-col cols="12" sm="6">
              <v-select
                v-model="seismicGrade"
                :items="seismicOptions"
                item-title="grade"
                label="抗震等级"
                required
              />
            </v-col>
          </v-row>

          <!-- 修正系数 -->
          <v-expand-transition>
            <div v-if="modifiersOptions.length > 0">
              <v-divider class="my-4"></v-divider>
              <v-list density="compact">
                <v-list-item v-for="mod in modifiersOptions" :key="mod.modifier_id">
                  <v-checkbox
                    :model-value="selectedModifiers.includes(mod.modifier_id)"
                    @update:model-value="
                      $event
                        ? selectedModifiers.push(mod.modifier_id)
                        : selectedModifiers.splice(selectedModifiers.indexOf(mod.modifier_id), 1)
                    "
                    :label="mod.name"
                    :hint="mod.condition"
                    hide-details
                  />
                </v-list-item>
              </v-list>
            </div>
          </v-expand-transition>

          <!-- 操作按钮 -->
          <v-row>
            <v-col cols="12" sm="6">
              <v-btn type="submit" color="primary" :loading="loading" block>
                计算
              </v-btn>
            </v-col>
            <v-col cols="12" sm="6">
              <v-btn @click="reset" variant="outlined" block>
                重置
              </v-btn>
            </v-col>
          </v-row>
        </v-form>
      </v-card-text>
    </v-card>

    <!-- 错误提示 -->
    <v-alert v-if="error" type="error" variant="tonal" class="mb-4">
      {{ error }}
    </v-alert>

    <!-- 计算结果 -->
    <v-card v-if="result" class="mb-4">
      <v-card-title>
        <span>计算结果</span>
        <v-spacer></v-spacer>
        <v-btn size="small" variant="tonal" color="primary" @click="viewRelatedSpec">
          <v-icon start>mdi-book-open-page-variant</v-icon>
          查看相关条文
        </v-btn>
      </v-card-title>
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="4">
            <div class="text-body-2 text-medium-emphasis">基本锚固长度 lab</div>
            <div class="text-h5">{{ result.lab_d }}d</div>
            <div class="text-subtitle-2">{{ result.lab_mm }} mm</div>
          </v-col>
          <v-col cols="12" sm="4">
            <div class="text-body-2 text-medium-emphasis">受拉锚固长度 la</div>
            <div class="text-h5">{{ result.la_d }}d</div>
            <div class="text-subtitle-2">{{ result.la_mm }} mm</div>
            <div v-if="result.modifiers_applied.length > 0" class="text-caption text-primary">
              修正：{{ result.modifiers_applied.join(', ') }}
            </div>
          </v-col>
          <v-col cols="12" sm="4">
            <div class="text-body-2 text-medium-emphasis">抗震锚固长度 laE</div>
            <div class="text-h5 text-primary">{{ result.laE_d }}d</div>
            <div class="text-subtitle-2">{{ result.laE_mm }} mm</div>
            <div class="text-caption text-secondary">
              抗震系数 ζaE = {{ result.seismic_factor }}
            </div>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <!-- 占位提示 -->
    <v-card v-else>
      <v-card-text class="text-center text-medium-emphasis py-8">
        请选择参数并点击"计算"按钮
      </v-card-text>
    </v-card>
  </v-container>
</template>
